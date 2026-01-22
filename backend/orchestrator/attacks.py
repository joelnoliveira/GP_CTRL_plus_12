import json
import pathlib
import uuid
import time 
from datetime import datetime

from data_repository.crud import store_run
from pyrit.common import IN_MEMORY, initialize_pyrit
from pyrit.orchestrator import CrescendoOrchestrator
# from pyrit.prompt_target import OllamaChatTarget
from pyrit.common.path import DATASETS_PATH
from pyrit.orchestrator.single_turn.flip_attack_orchestrator import FlipAttackOrchestrator
# from pyrit.score.self_ask_refusal_scorer import SelfAskRefusalScorer
from pyrit.orchestrator.single_turn.role_play_orchestrator import RolePlayOrchestrator, RolePlayPaths 
from pyrit.prompt_normalizer.normalizer_request import NormalizerRequest
from pyrit.prompt_target import (OllamaChatTarget, OpenAIChatTarget, HuggingFaceChatTarget, AzureMLChatTarget)
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.score import SelfAskRefusalScorer
from pyrit.models import SeedPromptDataset
from pyrit.models.prompt_request_response import PromptRequestResponse
from pyrit.memory.central_memory import CentralMemory
from orchestrator.constants import DEFAULTS, Goals, TargetModel

from evaluation_service.run_metrics import get_run_metrics, get_run_metrics_crescendo
from evaluation_service.vulnerability_analysis import vuln_analysis
async def over_refusal_test(
        # ollama_host,
        # seed=2316,
        # temperature_judges=0.1,
        # target_model_name = "llama3.2:1b",
        # jury_models = ["llama3.2:1b", "llama3.2:1b", "llama3.2:1b"],
        ollama_host, **kwargs
    ):
    args = {**DEFAULTS, **kwargs}
    seed = args["seed"]
    temperature_judges = args["temperature_judges"]
    temperature_target = args["temperature_target"]
    target_model_name = args["target_model_name"]
    jury_models = args["jury_models"]
    target_provider = args["target_provider"]
    api_key = args["api_key"]
    db = args["db"]
    
    begin_started_at = time.time()
    started_at = time.localtime(begin_started_at)
    started_at = datetime.fromtimestamp(begin_started_at)
    
    try:
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        
        initialize_pyrit(memory_db_type="InMemory")
        memory = CentralMemory.get_memory_instance()
        memory_labels = {"op_name": "or-bench-hard-1k", "user_name": "jd"}


        #judge = OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=200)
        #target = target_provider_dict[target_provider](model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed, 'temperature': temperature_target})
        if target_provider == TargetModel.OLLAMA.value:
            target = OllamaChatTarget(
                model_name=target_model_name,
                endpoint= ollama_host + "/api/chat",
                timeout=1000,
                options={'seed': seed, 'temperature': temperature_target}
            )
        elif target_provider == TargetModel.OPEN_AI.value:
            target = OpenAIChatTarget(
                deployment_name=target_model_name,
                api_key=api_key,  # ← vem da BD
                is_azure_target=False
            )

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


        requests = requests[:2]

        print(len(requests))

        responses = await prompt_sending_orchestrator.send_normalizer_requests_async(prompt_request_list=requests, memory_labels=memory_labels) #type: ignore
        #await prompt_sending_orchestrator.print_conversations_async()  # type: ignore


        #memory.export_conversations(file_path="conversations.json", export_type="json")
        #memory.dispose_engine()
        result_json = prompt_sending_orchestrator.output_conversations_to_json(file_path="debug_results/orr_atks_test.json")

        metrics = get_run_metrics(result_json, atk_type='over_refusal')
                
        ended_at = time.time()
        ended_at = time.localtime(begin_started_at)
        ended_at = datetime.fromtimestamp(time.time())
        
        store_run(
            db=db,
            user_id=1,
            scenario_id=3,
            template_datasets_id=None,
            target_model=target_model_name,
            attack_model=None,
            attack_results={
                "metrics": metrics,
            },
            started_at=started_at,
            ended_at=ended_at,
            langfuse_trace_id=None or f"trace_{started_at.isoformat()}",
            attacker_visibility="standard"
        )
        
        print(f"[DEBUG] metrics: {metrics}")

    except Exception as e:
        raise Exception(f"Error in over_refusal_test: {e}")

#we need to change this for each type of attack (just a baseline for the people that will do this later)
async def launch_attack_template(ollama_host, **kwargs):
    args = {**DEFAULTS, **kwargs}
    seed = args["seed"]
    goals_list = args["goals_list"] if args["goals_list"] is not None else []
    label = args["label"]
    jury_models = args["jury_models"]
    temperature_judges = args["temperature_judges"]
    temperature_target = args["temperature_target"]
    target_model_name = args["target_model_name"]
    template_path = args.get("template_path")
    target_provider = args["target_provider"]
    api_key = args["api_key"]
    db = args["db"]
    scenario_id = args["scenario_id"]
    template_datasets_id = args["template_dataset_id"]
    
    begin_started_at = time.time()
    started_at = time.localtime(begin_started_at)
    started_at = datetime.fromtimestamp(begin_started_at)
    
    try:
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type="InMemory")

        # template attack
        path = pathlib.Path(template_path) if template_path else pathlib.Path("datasets/JailBreakV_28K_clean.yaml")
        
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                # Transform list-based JSON (e.g. malicious_goals) to SeedPrompt compatible format
                formatted_prompts = []
                for item in data:
                    if "Prompt" in item:
                        formatted_prompts.append({
                            "value": item["Prompt"],
                            "data_type": "text"
                        })
                    elif "value" in item:
                         formatted_prompts.append(item)
                
                seed_prompt_dataset = SeedPromptDataset(prompts=formatted_prompts)
            else:
                 # Attempt to load as standard dict-based dataset
                 seed_prompt_dataset = SeedPromptDataset.from_dict(data)
        else:
            seed_prompt_dataset = SeedPromptDataset.from_yaml_file(path)

        prompt_list = []
        goals_dictionary = {}

        #baseline from Donato... it will need to be adapted to our needs
        #to quickly test the attack template, we will limit the number of goals and prompts
        goals_list = goals_list[:1]
        seed_prompt_dataset.prompts = seed_prompt_dataset.prompts[:3]

        for goal in goals_list:
            for p in seed_prompt_dataset.prompts:
                full_prompt: str = p.render_template_value(
                    prompt=goal
                )
                prompt_list.append(full_prompt)
                goals_dictionary[full_prompt] = goal
        
        memory = CentralMemory.get_memory_instance()
        memory_labels = {"op_name": label, "user_name": "jd"}

        if target_provider == TargetModel.OLLAMA.value:
            target = OllamaChatTarget(
                model_name=target_model_name,
                endpoint= ollama_host + "/api/chat",
                timeout=1000,
                options={'seed': seed, 'temperature': temperature_target}
            )
        elif target_provider == TargetModel.OPEN_AI.value:
            target = OpenAIChatTarget(
                deployment_name=target_model_name,
                api_key=api_key,  # ← vem da BD
                is_azure_target=False
            )
        #judge = OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=200)
        #target = target_provider_dict[target_provider](model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'num_predict': 5000, 'seed': seed, 'temperature': temperature_target})

        #target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 5000, 'seed': seed, 'temperature': temperature_target})

        jury_1 = OllamaChatTarget(model_name=jury_models[0], endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 5000, 'seed': seed, 'temperature': temperature_judges})
        jury_2 = OllamaChatTarget(model_name=jury_models[1], endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
        jury_3 = OllamaChatTarget(model_name=jury_models[2], endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})

        refusal_scorer_jury_1 = SelfAskRefusalScorer(
            chat_target=jury_1,
            system_prompt_path=pathlib.Path("pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        refusal_scorer_jury_2 = SelfAskRefusalScorer(
            chat_target=jury_2,
            system_prompt_path=pathlib.Path("pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        refusal_scorer_jury_3 = SelfAskRefusalScorer(
            chat_target=jury_3,
            system_prompt_path=pathlib.Path("pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        prompt_sending_orchestrator=  PromptSendingOrchestrator(target, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], verbose=True, batch_size=3)


        requests: list[NormalizerRequest] = []
        for prompt in prompt_list:
            requests.append(
                prompt_sending_orchestrator._create_normalizer_request(
                prompt_text=prompt,
                prompt_type="text",
                converters=prompt_sending_orchestrator._prompt_converters,
                metadata={"task": goals_dictionary[prompt]},
                conversation_id=str(uuid.uuid4()),
        )
        )

        # requests = requests[900:]
        #requests = requests[1000:]
        responses = await prompt_sending_orchestrator.send_normalizer_requests_async(prompt_request_list=requests, memory_labels=memory_labels) #type: ignore
        #await prompt_sending_orchestrator.print_conversations_async()  # type: ignore
        
        result_json = prompt_sending_orchestrator.output_conversations_to_json(file_path="debug_results/template_atks_test.json")
        #score responses
        # ??? responses_flattened = PromptRequestResponse.flatten_to_prompt_request_pieces(responses)

        print(f"[DEBUG] goals list length: {len(goals_list)}")
        metrics = get_run_metrics(result_json, atk_type='attack_template', n_goals=len(goals_list))

        print(f"[DEBUG] metrics: {metrics}")

        if label == Goals.VULNERABLE_GOALS.value:
            vuln_analysis(result_json)
        
        ended_at = time.time()
        ended_at = time.localtime(begin_started_at)
        ended_at = datetime.fromtimestamp(time.time())
        
        store_run(
            db=db,
            user_id=1,
            scenario_id=scenario_id,
            template_datasets_id=template_datasets_id,
            target_model=target_model_name,
            attack_model=None,
            attack_results={
                "metrics": metrics,
            },
            started_at=started_at,
            ended_at=ended_at,
            langfuse_trace_id=None or f"trace_{started_at.isoformat()}",
            attacker_visibility="standard"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Error in launch_attack_template: {e}")

async def launch_crescendo_attack(ollama_host, **kwargs):
    args = {**DEFAULTS, **kwargs}
    seed = args["seed"]
    attacker_model_name = args["attacker_model_name"]
    judge_model_name = args["judge_model_name"]
    target_model_name = args["target_model_name"]
    goals_list = args["goals_list"] if args["goals_list"] is not None else []
    temperature_target = args["temperature_target"]
    temperature_attacker = args["temperature_attacker"]
    temperature_judge = args["jury_models"]
    label = args["label"]
    target_provider = args["target_provider"]
    api_key = args["api_key"]
    db = args["db"]
    scenario_id = args["scenario_id"]
    attacker_model_name = args["attacker_model_name"]

    begin_started_at = time.time()
    started_at = time.localtime(begin_started_at)
    started_at = datetime.fromtimestamp(begin_started_at)
    
    try:
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type=IN_MEMORY)

        #judge = OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=200)
        #objective_target = target_provider_dict[target_provider](model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed, 'temperature': temperature_target})
        if target_provider == TargetModel.OLLAMA.value:
            objective_target = OllamaChatTarget(
                model_name=target_model_name,
                endpoint= ollama_host + "/api/chat",
                timeout=1000,
                options={'seed': seed, 'temperature': temperature_target}
            )
        elif target_provider == TargetModel.OPEN_AI.value:
            objective_target = OpenAIChatTarget(
                deployment_name=target_model_name,
                api_key=api_key,  # ← vem da BD
                is_azure_target=False
            )

        #objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed, 'temperature': temperature_target})
        attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed, 'temperature': temperature_attacker})
        judge= OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed, 'temperature': temperature_judge})

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

        orchestrator.output_conversations_to_json(file_path="debug_results/crescendo_atk_test.json")

        metrics = get_run_metrics_crescendo(data)
        print(f"[DEBUG] metrics: {metrics}")

        if label == Goals.VULNERABLE_GOALS.value:
            vulnerabilities = vuln_analysis(data)

        ended_at = time.time()
        ended_at = time.localtime(begin_started_at)
        ended_at = datetime.fromtimestamp(time.time())
        
        store_run(
            db=db,
            user_id=1,
            scenario_id=scenario_id,
            template_datasets_id=None,
            target_model=target_model_name,
            attack_model=attacker_model_name,
            attack_results={
                "metrics": metrics,
            },
            started_at=started_at,
            ended_at=ended_at,
            langfuse_trace_id=None or f"trace_{started_at.isoformat()}",
            attacker_visibility="standard"
        )
        ##save variable data to a json file
        with open("debug_results/crescendo_atk_test_clean.json", "w") as f:
            json.dump(data, f)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Error in launch_crescendo_attack: {e}") 

async def launch_flip_attack(ollama_host, **kwargs):
    args = {**DEFAULTS, **kwargs}
    seed = args["seed"]
    attacker_model_name = args["attacker_model_name"]
    judge_model_name = args["judge_model_name"]
    target_model_name = args["target_model_name"]
    goals_list = args["goals_list"] if args["goals_list"] is not None else []
    temperature_target = args["temperature_target"]
    temperature_attacker = args["temperature_attacker"]
    temperature_judge = args["jury_models"]
    label = args["label"]
    target_provider = args["target_provider"]
    api_key = args["api_key"]
    try:
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type=IN_MEMORY)

        #judge = OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=200)
        #objective_target = target_provider_dict[target_provider](model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed, 'temperature': temperature_target})
        if target_provider == TargetModel.OLLAMA.value:
            objective_target = OllamaChatTarget(
                model_name=target_model_name,
                endpoint= ollama_host + "/api/chat",
                timeout=1000,
                options={'seed': seed, 'temperature': temperature_target}
            )
        elif target_provider == TargetModel.OPEN_AI.value:
            objective_target = OpenAIChatTarget(
                deployment_name=target_model_name,
                api_key=api_key,  # ← vem da BD
                is_azure_target=False

            )
        #objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed, 'temperature': temperature_target})
        attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed, 'temperature': temperature_attacker})
        judge= OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed, 'temperature': temperature_judge})


        refusal_scorer_judge = SelfAskRefusalScorer(
            chat_target=judge,
            system_prompt_path=pathlib.Path("./pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
        )

        orchestrator= FlipAttackOrchestrator(objective_target=objective_target, scorers=[refusal_scorer_judge], verbose=True, batch_size=1)

        results = await orchestrator.send_prompts_async(prompt_list=goals_list, metadata=goals_list) # type: ignore

        orchestrator.output_conversations_to_json(file_path="results/attacker_llm/malicious/single_turn/role_play/video_game2/gemma3_27b_3.json")
        # with open("flip_attack_results.json", "w") as f:
        #     json.dump(results, f)
    except Exception as e:
        print(f"Error in launch_flip_attack: {e}") 

async def launch_role_play_attack(ollama_host, **kwargs):
    args = {**DEFAULTS, **kwargs}
    seed = args["seed"]
    attacker_model_name = args["attacker_model_name"]
    jury_models = args["jury_models"]
    temperature_judges = args["temperature_judges"]
    target_model_name = args["target_model_name"]
    goals_list = args["goals_list"] if args["goals_list"] is not None else []
    role_play_option = args.get("role_play_option", RolePlayPaths.MR_ROBOT.value)
    temperature_target = args["temperature_target"]
    temperature_attacker = args["temperature_attacker"]
    label = args["label"]
    target_provider = args["target_provider"]
    api_key = args["api_key"]
    db = args["db"]
    scenario_id = args["scenario_id"]
    attacker_model_name = args["attacker_model_name"]

    begin_started_at = time.time()
    started_at = time.localtime(begin_started_at)
    started_at = datetime.fromtimestamp(begin_started_at)
    
    try:
        ollama_host = ollama_host.rstrip('/').replace('/v1', '')
        initialize_pyrit(memory_db_type=IN_MEMORY)

    
        #judge = OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=200)
        #objective_target = target_provider_dict[target_provider](model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed, 'temperature': temperature_target})
        if target_provider == TargetModel.OLLAMA.value:
            objective_target = OllamaChatTarget(
                model_name=target_model_name,
                endpoint= ollama_host + "/api/chat",
                timeout=1000,
                options={'seed': seed, 'temperature': temperature_target}
            )
        elif target_provider == TargetModel.OPEN_AI.value:
            objective_target = OpenAIChatTarget(
                deployment_name=target_model_name,
                api_key=api_key,  # ← vem da BD
                is_azure_target=False

            )

        
        #objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed, 'temperature': temperature_target})
        attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=2000, options={'seed': seed, 'temperature': temperature_attacker})
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
        #orchestrator = RolePlayOrchestrator(objective_target=objective_target, adversarial_chat=attacker, role_play_definition_path=RolePlayPaths.VIDEO_GAME.value, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], batch_size=1 ,verbose=True)
        orchestrator = RolePlayOrchestrator(objective_target=objective_target, adversarial_chat=attacker, role_play_definition_path=role_play_option, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], batch_size=1 ,verbose=True)

        print("results:")
        results = await orchestrator.send_as_normalizer_requests_async(goals_list=goals_list) # type: ignore
        result_json = orchestrator.output_conversations_to_json(file_path="debug_results/role_play_atk_test.json")
        # with open("mr_robot_attack_results.json", "w") as f:
        #     json.dump(results, f)

        metrics = get_run_metrics(result_json, atk_type='llm')
        print(f"[DEBUG] metrics: {metrics}")

        if label == Goals.VULNERABLE_GOALS.value:
            vulnerabilities = vuln_analysis(result_json)

        ended_at = time.time()
        ended_at = time.localtime(begin_started_at)
        ended_at = datetime.fromtimestamp(time.time())
        
        store_run(
            db=db,
            user_id=1,
            scenario_id=scenario_id,
            template_datasets_id=None,
            target_model=target_model_name,
            attack_model=attacker_model_name,
            attack_results={
                "metrics": metrics,
            },
            started_at=started_at,
            ended_at=ended_at,
            langfuse_trace_id=None or f"trace_{started_at.isoformat()}",
            attacker_visibility="standard"
        )
    except Exception as e:
        raise Exception(f"Error in launch_mr_robot_attack: {e}") 