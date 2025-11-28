import json
import pathlib

from pyrit.common import IN_MEMORY, initialize_pyrit
from pyrit.orchestrator import CrescendoOrchestrator
from pyrit.prompt_target import OllamaChatTarget
from pyrit.common.path import DATASETS_PATH
from pyrit.orchestrator.single_turn.flip_attack_orchestrator import FlipAttackOrchestrator
from pyrit.score.self_ask_refusal_scorer import SelfAskRefusalScorer
from pyrit.orchestrator.single_turn.role_play_orchestrator import RolePlayOrchestrator, RolePlayPaths 

async def launch_crescendo_attack(
    ollama_host: str,
    seed=2316,
    temperature_judges=0.1,
    attacker_model_name="gemma3:27b",
    judge_model_name="gemma3:27b",
    jury_models=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
    target_model_name="gemma3:27b",
    goals_list=None,
):
    try:
        if not ollama_host:
            raise ValueError("ollama_host cannot be None or empty")
        
        if goals_list is None:
            goals_list = []
        
        print("Initializing pyrit")
        initialize_pyrit(memory_db_type=IN_MEMORY)

        print("Setting up targets")
        base_url = ollama_host.rstrip('/')
        
        # Test Ollama connection first
        await test_ollama_connection(base_url)
        
        # Check if models are available
        await check_models_available(base_url, [attacker_model_name, judge_model_name, target_model_name])
        
        objective_target = OllamaChatTarget(
            model_name=target_model_name, 
            endpoint=f"{base_url}/api/chat", 
            timeout=5000, 
            options={'seed': seed}
        )
        attacker = OllamaChatTarget(
            model_name=attacker_model_name, 
            endpoint=f"{base_url}/api/chat", 
            timeout=5000, 
            options={'seed': seed}
        )
        judge = OllamaChatTarget(
            model_name=judge_model_name, 
            endpoint=f"{base_url}/api/chat", 
            timeout=5000, 
            options={'seed': seed}
        )

        print("Setting up orchestrator")
        orchestrator = CrescendoOrchestrator(
            objective_target=objective_target,
            adversarial_chat=attacker,
            max_turns=10,
            max_backtracks=5,
            scoring_target=judge,
            verbose=True
        )

        print("Launching attack")
        # Test with a single goal first
        test_goals = goals_list[:1] if goals_list else ["Test goal"]
        print(f"Testing with {len(test_goals)} goals")
        
        results = await orchestrator.run_attacks_async(objectives=test_goals, batch_size=1)

        data = []
        print("Processing results")
        for result in results:
            await result.print_conversation_async()
            data.append(await result.get_data_from_conversation_async())
        
        print("Saving results")
        with open("gemma3:27b_3.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("Attack completed successfully")
        return data
        
    except Exception as e:
        print(f"Error in launch_crescendo_attack: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise


async def test_ollama_connection(ollama_url: str):
    """Test if Ollama is accessible"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags", timeout=10.0)
            if response.status_code == 200:
                print("✅ Ollama connection successful")
            else:
                raise ConnectionError(f"Ollama API returned status {response.status_code}")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Ollama at {ollama_url}: {e}")


async def check_models_available(ollama_url: str, model_names: list):
    """Check if required models are available"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags", timeout=10.0)
            if response.status_code == 200:
                available_models = [model['name'] for model in response.json().get('models', [])]
                print(f"Available models: {available_models}")
                
                for model_name in model_names:
                    # Check for exact match or partial match
                    found = any(model_name in available_model for available_model in available_models)
                    if not found:
                        print(f"⚠️  Model '{model_name}' not found in available models")
                    else:
                        print(f"✅ Model '{model_name}' is available")
            else:
                print("⚠️  Could not fetch model list from Ollama")
    except Exception as e:
        print(f"⚠️  Could not check model availability: {e}")
        
# async def launch_crescendo_attack(
#         ollama_host,
#         seed=2316,
#         temperature_judges=0.1,
#         attacker_model_name = "gemma3:27b",
#         judge_model_name = "gemma3:27b",
#         jury_models = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
#         target_model_name = "gemma3:27b",
#         goals_list = [],
#     ):
#     try:
#         print("Initializing pyrit")
#         initialize_pyrit(memory_db_type=IN_MEMORY)

#         print("Setting up targets")
#         objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
#         attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
#         judge= OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})

#         print("Setting up orchestrator")
#         orchestrator= CrescendoOrchestrator(
#             objective_target=objective_target,
#             adversarial_chat=attacker,
#             max_turns=10,
#             max_backtracks=5,
#             scoring_target=judge,
#             verbose=True
#         )

#         print("Launching attack")
#         results = await orchestrator.run_attacks_async(objectives=goals_list, batch_size=1) # type: ignore

#         data = []
#         print("Processing results")
#         for result in results:
#             await result.print_conversation_async()  # type: ignore
#             data.append(await result.get_data_from_conversation_async())
#         print("Saving results")
#         ##save variable data to a json file
#         with open("gemma3:27b_3.json", "w") as f:
#             json.dump(data, f)
#     except Exception as e:
#         print(f"Error in launch_crescendo_attack: {e}") 

async def launch_flip_attack(
        ollama_host,
        seed=2316,
        temperature_judges=0.1,
        attacker_model_name = "gemma3:27b",
        judge_model_name = "gemma3:27b",
        jury_models = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
        target_model_name = "gemma3:27b",
        goals_list = [],
    ):
    initialize_pyrit(memory_db_type=IN_MEMORY)

    objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
    attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})
    judge= OllamaChatTarget(model_name=judge_model_name, endpoint=ollama_host + "/api/chat", timeout=5000, options={'seed': seed})


    refusal_scorer_judge = SelfAskRefusalScorer(
        chat_target=judge,
        system_prompt_path=pathlib.Path("pyrit/datasets/score/refusal/refusal_to_generate_code.yaml")
    )

    orchestrator= FlipAttackOrchestrator(objective_target=objective_target, scorers=[refusal_scorer_judge], verbose=True, batch_size=1)

    results = await orchestrator.send_prompts_async(prompt_list=goals_list, metadata=goals_list) # type: ignore

    with open("flip_attack_results.json", "w") as f:
       json.dump(results, f)


async def launch_mr_robot_attack(
        ollama_host,
        seed=2316,
        temperature_judges=0.1,
        attacker_model_name = "gemma3:27b",
        judge_model_name = "gemma3:27b",
        jury_models = ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
        target_model_name = "gemma3:27b",
        goals_list = [],
    ):
    initialize_pyrit(memory_db_type=IN_MEMORY)

    objective_target = OllamaChatTarget(model_name=target_model_name, endpoint=ollama_host + "/api/chat", timeout=1000, options={'seed': seed})
    attacker = OllamaChatTarget(model_name=attacker_model_name, endpoint=ollama_host + "/api/chat", timeout=2000, options={'seed': seed})
    jury_1 = OllamaChatTarget(model_name=jury_models[0], endpoint=ollama_host + "/api/chat", timeout=None, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
    jury_2 = OllamaChatTarget(model_name=jury_models[1], endpoint=ollama_host + "/api/chat", timeout=10000, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})
    jury_3 = OllamaChatTarget(model_name=jury_models[2], endpoint=ollama_host + "/api/chat", timeout=10000, options={'num_predict': 1000, 'seed': seed, 'temperature': temperature_judges})



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

    #orchestrator = RolePlayOrchestrator(objective_target=objective_target, adversarial_chat=attacker, role_play_definition_path=RolePlayPaths.MR_ROBOT.value, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], batch_size=1 ,verbose=True)
    orchestrator = RolePlayOrchestrator(objective_target=objective_target, adversarial_chat=attacker, role_play_definition_path=RolePlayPaths.VIDEO_GAME.value, scorers=[refusal_scorer_jury_1, refusal_scorer_jury_2, refusal_scorer_jury_3], batch_size=1 ,verbose=True)

    results = await orchestrator.send_as_normalizer_requests_async(goals_list=goals_list) # type: ignore
    with open("mr_robot_attack_results.json", "w") as f:
        json.dump(results, f)
