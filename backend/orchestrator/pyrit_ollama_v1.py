import os
import json
import pathlib
import uuid
import argparse
import asyncio
import requests
from dotenv import load_dotenv

from pyrit.prompt_normalizer.normalizer_request import NormalizerRequest
from pyrit.prompt_target import OllamaChatTarget
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.score import SelfAskRefusalScorer
from pyrit.common.initialization import initialize_pyrit
from pyrit.memory.central_memory import CentralMemory
from pyrit.models import SeedPromptDataset
from pyrit.models.prompt_request_response import PromptRequestResponse

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:8080")
SEED = int(os.getenv("SEED", "1112"))
TEMPERATURE_JUDGES = float(os.getenv("TEMPERATURE_JUDGES", "0.1"))

TARGET_MODEL = os.getenv("TARGET_MODEL", "gemma3:27b")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "deepseek-r1:70b")
JURY_MODELS = os.getenv("JURY_MODELS", "deepseek-r1:70b,qwen2.5:latest,dolphin3:8b").split(",")


class OllamaClient:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host.rstrip("/")

    def delete_model(self, model_name: str):
        r = requests.delete(f"{self.host}/api/delete", json={"model": model_name})
        return r

    def pull_model(self, model_name: str, stream: bool = True):
        r = requests.post(f"{self.host}/api/pull", json={"model": model_name}, stream=stream)
        return r

    def list_models(self):
        r = requests.get(f"{self.host}/api/tags")
        return r

    def unload_model(self, model_name: str):
        # send an empty chat with keep_alive=0 to unload
        r = requests.post(f"{self.host}/api/chat", json={"model": model_name, "messages": [], "keep_alive": 0})
        return r


def initialize_pyrit_inmemory():
    initialize_pyrit(memory_db_type="InMemory")
    return CentralMemory.get_memory_instance()


def build_targets_and_scorers(target_model_name: str = TARGET_MODEL,
                              jury_models: list = JURY_MODELS,
                              seed: int = SEED,
                              temperature_judges: float = TEMPERATURE_JUDGES):
    # create chat targets
    target = OllamaChatTarget(model_name=target_model_name, endpoint=f"{OLLAMA_HOST}/api/chat",
                              timeout=None, options={'num_predict': 5000, 'seed': seed})
    juries = []
    for jm in jury_models:
        juries.append(OllamaChatTarget(model_name=jm, endpoint=f"{OLLAMA_HOST}/api/chat",
                                       timeout=None, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges}))

    # create refusal scorers for juries
    scorers = []
    for j in juries:
        scorers.append(SelfAskRefusalScorer(chat_target=j, system_prompt_path=pathlib.Path("pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")))
    return target, scorers


async def run_or_bench(prompts: list[str],
                       goals_dictionary: dict,
                       label: str,
                       target_model_name: str = TARGET_MODEL,
                       jury_models: list = JURY_MODELS,
                       batch_size: int = 3,
                       start_index: int = 0,
                       limit: int | None = None):
    """
    Send prompts to target model using Pyrit orchestrator with jury scorers.
    Returns responses object from orchestrator.
    """
    initialize_pyrit(memory_db_type="InMemory")
    memory = CentralMemory.get_memory_instance()
    memory_labels = {"op_name": label, "user_name": "jd"}

    target, scorers = build_targets_and_scorers(target_model_name=target_model_name, jury_models=jury_models)

    prompt_sending_orchestrator = PromptSendingOrchestrator(target, scorers=scorers, verbose=True, batch_size=batch_size)

    requests_list = []
    for prompt in prompts:
        requests_list.append(
            prompt_sending_orchestrator._create_normalizer_request(
                prompt_text=prompt,
                prompt_type="text",
                converters=prompt_sending_orchestrator._prompt_converters,
                metadata={"task": goals_dictionary.get(prompt)},
                conversation_id=str(uuid.uuid4()),
            )
        )

    if start_index:
        requests_list = requests_list[start_index:]
    if limit is not None:
        requests_list = requests_list[:limit]

    responses = await prompt_sending_orchestrator.send_normalizer_requests_async(prompt_request_list=requests_list, memory_labels=memory_labels)
    return prompt_sending_orchestrator, responses


def save_conversations(orchestrator: PromptSendingOrchestrator, file_path: str):
    orchestrator.output_conversations_to_json(file_path=file_path)


async def score_responses_with_judge(responses, judge_model_name: str = JUDGE_MODEL):
    responses_flattened = PromptRequestResponse.flatten_to_prompt_request_pieces(responses)
    judge_target = OllamaChatTarget(model_name=judge_model_name, endpoint=f"{OLLAMA_HOST}/api/chat", max_requests_per_minute=10, timeout=100)
    refusal_scorer = SelfAskRefusalScorer(chat_target=judge_target)
    refusal_scores = await refusal_scorer.score_responses_inferring_tasks_batch_async(request_responses=responses_flattened, batch_size=1)
    return refusal_scores


def load_goals(label: str):
    if label == "malicious_goals":
        path = "datasets/malicious_goals.json"
    elif label == "vulnerable_goals":
        path = "datasets/vulnerable_goals.json"
    else:
        raise ValueError("label must be 'malicious_goals' or 'vulnerable_goals'")
    with open(path, "r", encoding="utf-8") as f:
        goals = json.load(f)
    goals_list = [g["Prompt"] for g in goals]
    return goals_list, goals


def render_templates_from_seed_yaml(seed_yaml_path: str, goals_list: list, label: str):
    initialize_pyrit(memory_db_type="InMemory")
    seed_prompt_dataset = SeedPromptDataset.from_yaml_file(pathlib.Path(seed_yaml_path))
    prompt_list = []
    goals_dictionary = {}
    for p in seed_prompt_dataset.prompts:
        for goal in goals_list:
            full_prompt: str = p.render_template_value(prompt=goal)
            prompt_list.append(full_prompt)
            goals_dictionary[full_prompt] = goal
    return prompt_list, goals_dictionary


def main_sync_entry(args):
    client = OllamaClient(OLLAMA_HOST)

    if args.action == "list":
        r = client.list_models()
        print(r.json())
        return

    if args.action == "delete":
        if not args.model:
            print("provide --model model_name")
            return
        r = client.delete_model(args.model)
        print(r.status_code, r.text)
        return

    if args.action == "pull":
        if not args.model:
            print("provide --model model_name")
            return
        r = client.pull_model(args.model, stream=True)
        for line in r.iter_lines():
            if line:
                try:
                    print(json.loads(line))
                except Exception:
                    print(line)
        return

    if args.action == "unload":
        if not args.model:
            print("provide --model model_name")
            return
        r = client.unload_model(args.model)
        print(r.status_code, r.text)
        return

    if args.action == "run":
        # run the orchestration / or-bench flow
        label = args.label or "malicious_goals"
        seed_yaml = args.seed_yaml or "datasets/JailBreakV_28K_clean.yaml"
        start = args.start or 0
        limit = args.limit
        goals_list, _ = load_goals(label)
        if args.use_templates:
            prompt_list, goals_dictionary = render_templates_from_seed_yaml(seed_yaml, goals_list, label)
        else:
            prompt_list = goals_list
            goals_dictionary = {p: p for p in prompt_list}
        # run orchestrator
        loop = asyncio.get_event_loop()
        orchestrator, responses = loop.run_until_complete(run_or_bench(prompt_list, goals_dictionary, label,
                                                                       target_model_name=args.target or TARGET_MODEL,
                                                                       jury_models=args.jury_models or JURY_MODELS,
                                                                       batch_size=args.batch_size,
                                                                       start_index=start,
                                                                       limit=limit))
        if args.out:
            save_conversations(orchestrator, args.out)
        else:
            print("Run finished. Provide --out to save JSON of conversations.")
        return

    print("Unknown action. Use --help.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pyrit + ollama helper script")
    parser.add_argument("action", choices=["list", "delete", "pull", "unload", "run"], help="action to perform")
    parser.add_argument("--model", help="model name for pull/delete/unload")
    parser.add_argument("--label", help="dataset label: malicious_goals or vulnerable_goals")
    parser.add_argument("--seed-yaml", dest="seed_yaml", help="seed template yaml (for templates)")
    parser.add_argument("--use-templates", action="store_true", help="render jailbreak/pliny templates with goals")
    parser.add_argument("--start", type=int, help="start index for requests")
    parser.add_argument("--limit", type=int, help="limit number of requests")
    parser.add_argument("--out", help="output json file for conversations")
    parser.add_argument("--target", help="target model override")
    parser.add_argument("--jury-models", nargs="+", help="list of jury models to use")
    parser.add_argument("--batch-size", type=int, default=3, help="batch size for orchestrator")
    args = parser.parse_args()

    main_sync_entry(args)
