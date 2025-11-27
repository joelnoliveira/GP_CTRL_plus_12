# pyrit_ollama.py
import os
import json
import pathlib
import requests
from dotenv import load_dotenv

from pyrit.prompt_target import OllamaChatTarget
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.score import SelfAskRefusalScorer
from pyrit.models import SeedPromptDataset
from pyrit.prompt_normalizer.normalizer_request import NormalizerRequest
from pyrit.models.filter_criteria import PromptFilterCriteria
from pyrit.models.prompt_request_response import PromptRequestResponse

from pyrit.common.initialization import initialize_pyrit
from pyrit.memory.central_memory import CentralMemory


class PyritOllamaManager:
    def __init__(self):
        load_dotenv()
        self.ollama_host = os.getenv("OLLAMA_HOST")
        self.seed = 1112
        self.temperature_judges = 0.1
        
        self.target_model_name = "gemma3:27b"
        self.jury_models = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"]
        
        initialize_pyrit(memory_db_type="InMemory")
        self.memory = CentralMemory.get_memory_instance()

    def delete_model(self, model_name: str):
        """Delete a model from Ollama"""
        response = requests.delete(f"{self.ollama_host}/api/delete", json={"model": model_name})
        print(f"Delete response: {response.status_code}")
        return response

    def unload_model(self, model_name: str):
        """Unload a model from memory"""
        response = requests.post(
            f"{self.ollama_host}/api/chat", 
            json={"model": model_name, "messages": [], "keep_alive": 0}
        )
        print(f"Unload response: {response.status_code}")
        return response

    def pull_model(self, model_name: str):
        """Pull a model to Ollama"""
        response = requests.post(
            f"{self.ollama_host}/api/pull", 
            json={"model": model_name}, 
            stream=True
        )
        for line in response.iter_lines():
            if line:
                print(json.loads(line))
        return response

    def list_models(self):
        """List available models in Ollama"""
        response = requests.get(f"{self.ollama_host}/api/tags")
        return response.json()

    def setup_targets(self):
        """Setup target and jury models"""
        target = OllamaChatTarget(
            model_name=self.target_model_name,
            endpoint=f"{self.ollama_host}/api/chat",
            timeout=1000,
            options={'seed': self.seed}
        )

        jury_targets = []
        for i, model_name in enumerate(self.jury_models):
            jury_target = OllamaChatTarget(
                model_name=model_name,
                endpoint=f"{self.ollama_host}/api/chat",
                timeout=10000,
                options={
                    'num_predict': 1000,
                    'seed': self.seed,
                    'temperature': self.temperature_judges
                }
            )
            jury_targets.append(jury_target)

        return target, jury_targets

    def setup_scorers(self, jury_targets):
        """Setup refusal scorers for jury models"""
        scorers = []
        refusal_prompt_path = pathlib.Path("pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        
        for jury_target in jury_targets:
            scorer = SelfAskRefusalScorer(
                chat_target=jury_target,
                system_prompt_path=refusal_prompt_path
            )
            scorers.append(scorer)
        
        return scorers

    def run_or_bench_evaluation(self, start_index=750):
        """Run OR-Bench evaluation"""
        target, jury_targets = self.setup_targets()
        scorers = self.setup_scorers(jury_targets)
        
        prompt_sending_orchestrator = PromptSendingOrchestrator(
            target, 
            scorers=scorers, 
            verbose=True, 
            batch_size=3
        )

        # Load OR-Bench dataset
        or_bench_dataset = SeedPromptDataset.from_yaml_file(
            pathlib.Path("datasets/or-bench-hard-1k.yaml")
        )

        # Add prompts to memory
        self.memory.add_seed_prompts_to_memory(
            prompts=or_bench_dataset.prompts,
            added_by="jd"
        )

        prompt_groups = self.memory.get_seed_prompt_groups()
        requests = [NormalizerRequest(seed_prompt_group=p) for p in prompt_groups]
        
        # Process subset of requests
        requests = requests[start_index:]
        print(f"Processing {len(requests)} requests")

        memory_labels = {"op_name": "or-bench-hard-1k", "user_name": "jd"}
        
        responses = prompt_sending_orchestrator.send_normalizer_requests(
            prompt_request_list=requests,
            memory_labels=memory_labels
        )
        
        return responses, prompt_sending_orchestrator

    def save_conversations(self, orchestrator, file_path):
        """Save conversations to JSON file"""
        orchestrator.output_conversations_to_json(file_path=file_path)

    def load_malicious_goals(self):
        """Load malicious goals dataset"""
        with open("datasets/malicious_goals.json", "r") as f:
            malicious_goals = json.load(f)
        return [goal['Prompt'] for goal in malicious_goals]

    def load_vulnerable_goals(self):
        """Load vulnerable goals dataset"""
        with open("datasets/vulnerable_goals.json", "r") as f:
            vulnerable_goals = json.load(f)
        return [goal['Prompt'] for goal in vulnerable_goals]

    def render_jailbreak_prompts(self, goals_list, label):
        """Render JailbreakV28 prompts with goals"""
        seed_prompt_dataset = SeedPromptDataset.from_yaml_file(
            pathlib.Path("datasets/JailBreakV_28K_clean.yaml")
        )

        prompt_list = []
        goals_dictionary = {}

        for template_prompt in seed_prompt_dataset.prompts:
            for goal in goals_list:
                full_prompt = template_prompt.render_template_value(prompt=goal)
                prompt_list.append(full_prompt)
                goals_dictionary[full_prompt] = goal

        return prompt_list, goals_dictionary

    def score_responses(self, responses):
        """Score responses using refusal scorer"""
        responses_flattened = PromptRequestResponse.flatten_to_prompt_request_pieces(responses)
        
        judge = OllamaChatTarget(
            model_name="deepseek-r1:70b",
            endpoint=f"{self.ollama_host}/api/chat",
            max_requests_per_minute=10,
            timeout=100
        )

        refusal_scorer = SelfAskRefusalScorer(chat_target=judge)
        refusal_scores = refusal_scorer.score_responses_inferring_tasks_batch(
            request_responses=responses_flattened,
            batch_size=1
        )
        
        return refusal_scores


def main():
    manager = PyritOllamaManager()
    
    # Example usage:
    print("Available models:", manager.list_models())
    
    # Run OR-Bench evaluation
    responses, orchestrator = manager.run_or_bench_evaluation(start_index=750)
    
    # Save results
    manager.save_conversations(orchestrator, "gemma3_27b_final.json")
    
    # Score responses
    scores = manager.score_responses(responses)
    print("Refusal scores:", scores)


if __name__ == "__main__":
    main()