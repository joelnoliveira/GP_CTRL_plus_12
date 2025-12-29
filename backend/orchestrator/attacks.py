import json
import pathlib
from typing import Optional, List, Dict, Any
from datetime import datetime

from sklearn import metrics
from sqlalchemy.orm import Session
from data_repository.crud import store_run

from pyrit.common import IN_MEMORY, initialize_pyrit
from pyrit.orchestrator import CrescendoOrchestrator
# from pyrit.prompt_target import OllamaChatTarget
from pyrit.common.path import DATASETS_PATH
from pyrit.orchestrator.single_turn.flip_attack_orchestrator import FlipAttackOrchestrator
# from pyrit.score.self_ask_refusal_scorer import SelfAskRefusalScorer
from pyrit.orchestrator.single_turn.role_play_orchestrator import RolePlayOrchestrator, RolePlayPaths 
from pyrit.prompt_normalizer.normalizer_request import NormalizerRequest
from pyrit.prompt_target import (OllamaChatTarget, OpenAIChatTarget)
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.score import SelfAskRefusalScorer
from pyrit.models import SeedPromptDataset
from pyrit.models.prompt_request_response import PromptRequestResponse
from pyrit.memory.central_memory import CentralMemory

async def over_refusal_test(
        ollama_host,
        seed=2316,
        temperature_judges=0.1,
        target_model_name: str = "llama3.2:1b",
        jury_models: List[str] = ["llama3.2:1b", "llama3.2:1b", "llama3.2:1b"],
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        scenario_id: Optional[int] = None,
    ):
    try:
        started_at = datetime.now()
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        
        initialize_pyrit(memory_db_type="InMemory")
        memory = CentralMemory.get_memory_instance()
        memory_labels = {"op_name": "or-bench-hard-1k", "user_name": "jd"}


        #judge = OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=200)
        target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed})

        jury_1 = OllamaChatTarget(model_name=jury_models[0], endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
        jury_2 = OllamaChatTarget(model_name=jury_models[1], endpoint=ollama_host + "/api/chat", timeout=10000, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
        jury_3 = OllamaChatTarget(model_name=jury_models[2], endpoint=ollama_host + "/api/chat", timeout=10000, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})

        refusal_scorer_jury_1 = SelfAskRefusalScorer(
            chat_target=jury_1,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        refusal_scorer_jury_2 = SelfAskRefusalScorer(
            chat_target=jury_2,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        refusal_scorer_jury_3 = SelfAskRefusalScorer(
            chat_target=jury_3,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )


        prompt_sending_orchestrator=  PromptSendingOrchestrator(target, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], verbose=True, batch_size=3)

        or_bench_dataset= SeedPromptDataset.from_yaml_file(pathlib.Path("./datasets/or-bench-hard-1k.yaml"))


        await memory.add_seed_prompts_to_memory_async(prompts=or_bench_dataset.prompts, added_by="jd")  # type: ignore

        prompt_groups = memory.get_seed_prompt_groups()



        requests = [NormalizerRequest(seed_prompt_group=p) for p in prompt_groups]


        requests = requests[750:]

        print(len(requests))

        responses = await prompt_sending_orchestrator.send_normalizer_requests_async(prompt_request_list=requests, memory_labels=memory_labels) #type: ignore
        #await prompt_sending_orchestrator.print_conversations_async()  # type: ignore


        #memory.export_conversations(file_path="conversations.json", export_type="json")
        #memory.dispose_engine()
        prompt_sending_orchestrator.output_conversations_to_json(file_path="gemma3:27b_final.json")

        #score responses
        responses_flattened = PromptRequestResponse.flatten_to_prompt_request_pieces(responses)

        judge_2 = OllamaChatTarget(model_name="deepseek-r1:70b", endpoint=ollama_host + "/api/chat", max_requests_per_minute=10, timeout=100)

        refusal_scorer_2 = SelfAskRefusalScorer(
            chat_target=judge_2,
        )

        refusal_scores = await refusal_scorer_2.score_responses_inferring_tasks_batch_async(request_responses=responses_flattened, batch_size=1)

        ended_at = datetime.now()

        # persist run if DB and context provided
        metrics = {}
        try:
            data = []
            for r in responses_flattened:
                data.append(r)
    
            attack_results = {
                "attack_type": "over_refusal_test",
                "metrics": metrics,
                "data": data,
            }

            if db is not None and user_id is not None and scenario_id is not None:
                store_run(
                    db=db,
                    user_id=user_id,
                    scenario_id=scenario_id,
                    target_model=target_model_name,
                    attack_model=target_model_name,
                    attack_type="over_refusal_test",
                    attack_results=attack_results,
                    jury_votes_data=[],
                    started_at=started_at,
                    ended_at=ended_at,
                )
        except Exception as _err:
            print(f"Failed to store over_refusal_test run: {_err}")

    except Exception as e:
        print(f"Error in over_refusal_test: {e}")


async def launch_crescendo_attack(
        ollama_host,
        seed=2316,
        temperature_judges=0.1,
        attacker_model_name: str = "gemma3:27b",
        judge_model_name: str = "gemma3:27b",
        jury_models: List[str] = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
        target_model_name: str = "gemma3:27b",
        goals_list: List[str] = [],
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        scenario_id: Optional[int] = None,
    ):
    try:
        started_at = datetime.now()
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type=IN_MEMORY)

        objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
        attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
        judge= OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})

        orchestrator= CrescendoOrchestrator(
            objective_target=objective_target,
            adversarial_chat=attacker,
            max_turns=10,
            max_backtracks=5,
            scoring_target=judge,
            verbose=True
        )

        results = await orchestrator.run_attacks_async(objectives=goals_list, batch_size=1) # type: ignore

        data = []
        for result in results:
            await result.print_conversation_async()  # type: ignore
            data.append(await result.get_data_from_conversation_async())

        ##save variable data to a json file
        results_path = f"gemma3:27b_3.json"
        with open(results_path, "w") as f:
            json.dump(data, f)

        ended_at = datetime.now()

        # attempt to persist run if DB and context provided
        metrics = {}
        try:
            attack_results = {"attack_type": "crescendo", "metrics": metrics, "data": data}
            if db is not None and user_id is not None and scenario_id is not None:
                store_run(
                    db=db,
                    user_id=user_id,
                    scenario_id=scenario_id,
                    target_model=target_model_name,
                    attack_model=attacker_model_name,
                    attack_type="crescendo",
                    attack_results=attack_results,
                    jury_votes_data=[],
                    started_at=started_at,
                    ended_at=ended_at,
                    results_storage_path=results_path,
                )
        except Exception as _err:
            print(f"Failed to store crescendo run: {_err}")
    except Exception as e:
        print(f"Error in launch_crescendo_attack: {e}") 

async def launch_flip_attack(
        ollama_host,
        seed=2316,
        temperature_judges=0.1,
        attacker_model_name: str = "gemma3:27b",
        judge_model_name: str = "gemma3:27b",
        jury_models: List[str] = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
        target_model_name: str = "gemma3:27b",
        goals_list: List[str] = [],
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        scenario_id: Optional[int] = None,
    ):
    try:
        started_at = datetime.now()
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type=IN_MEMORY)

        objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
        attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
        judge= OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})


        refusal_scorer_judge = SelfAskRefusalScorer(
            chat_target=judge,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        orchestrator= FlipAttackOrchestrator(objective_target=objective_target, scorers=[refusal_scorer_judge], verbose=True, batch_size=1)

        results = await orchestrator.send_prompts_async(prompt_list=goals_list, metadata=goals_list) # type: ignore

        results_path = "flip_attack_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f)

        ended_at = datetime.now()
        metrics = {}
        try:
            attack_results = {"attack_type": "flip", "metrics": metrics, "data": results}
            if db is not None and user_id is not None and scenario_id is not None:
                store_run(
                    db=db,
                    user_id=user_id,
                    scenario_id=scenario_id,
                    target_model=target_model_name,
                    attack_model=attacker_model_name,
                    attack_type="flip",
                    attack_results=attack_results,
                    jury_votes_data=[],
                    started_at=started_at,
                    ended_at=ended_at,
                    results_storage_path=results_path,
                )
        except Exception as _err:
            print(f"Failed to store flip run: {_err}")
    except Exception as e:
        print(f"Error in launch_flip_attack: {e}") 

async def launch_mr_robot_attack(
        ollama_host,
        seed=2316,
        temperature_judges=0.1,
        attacker_model_name: str = "gemma3:27b",
        judge_model_name: str = "gemma3:27b",
        jury_models: List[str] = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
        target_model_name: str = "gemma3:27b",
        goals_list: List[str] = [],
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        scenario_id: Optional[int] = None,
    ):
    try:
        started_at = datetime.now()
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type=IN_MEMORY)

        objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed})
        attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=2000, options={'seed': seed})
        jury_1 = OllamaChatTarget(model_name=jury_models[0], endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
        jury_2 = OllamaChatTarget(model_name=jury_models[1], endpoint=ollama_host + "/api/chat", timeout=10000, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
        jury_3 = OllamaChatTarget(model_name=jury_models[2], endpoint=ollama_host + "/api/chat", timeout=10000, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})


        print("Setting up refusal scorers...")
        refusal_scorer_jury_1 = SelfAskRefusalScorer(
            chat_target=jury_1,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        refusal_scorer_jury_2 = SelfAskRefusalScorer(
            chat_target=jury_2,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        refusal_scorer_jury_3 = SelfAskRefusalScorer(
            chat_target=jury_3,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        #orchestrator = RolePlayOrchestrator(objective_target=objective_target, adversarial_chat=attacker, role_play_definition_path=RolePlayPaths.MR_ROBOT.value, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], batch_size=1 ,verbose=True)
        orchestrator = RolePlayOrchestrator(objective_target=objective_target, adversarial_chat=attacker, role_play_definition_path=RolePlayPaths.VIDEO_GAME.value, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], batch_size=1 ,verbose=True)
        print("results:")
        results = await orchestrator.send_as_normalizer_requests_async(goals_list=goals_list) # type: ignore
        results_path = "mr_robot_attack_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f)

        ended_at = datetime.now()

        metrics = {}
        try:
            attack_results = {"attack_type": "mr_robot", "metrics": metrics, "data": results}
            if db is not None and user_id is not None and scenario_id is not None:
                store_run(
                    db=db,
                    user_id=user_id,
                    scenario_id=scenario_id,
                    target_model=target_model_name,
                    attack_model=attacker_model_name,
                    attack_type="mr_robot",
                    attack_results=attack_results,
                    jury_votes_data=[],
                    started_at=started_at,
                    ended_at=ended_at,
                    results_storage_path=results_path,
                )
        except Exception as _err:
            print(f"Failed to store mr_robot run: {_err}")
    except Exception as e:
        print(f"Error in launch_mr_robot_attack: {e}") 
