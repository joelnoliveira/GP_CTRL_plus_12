import os
from dotenv import load_dotenv
import json
#import attacks
from orchestrator import attacks
from orchestrator.constants import TypesOfAttacks, Goals, DEFAULTS
from pyrit.orchestrator.single_turn.role_play_orchestrator import RolePlayPaths 

def load_labels(label: str):
    """
    Args:
        label (str): The type of labels to load. Must be either 
                     'malicious_goals' or 'vulnerable_goals'
    
    Returns:
        list[str]: List of prompt strings from the selected dataset
    """
    try:
        file_path = "./datasets/" + label + ".json"

        with open(file_path, "r") as f:
            goals = json.load(f)

        #convert malicious_goals to a list of prompts
        goals_list = [goal['Prompt'] for goal in goals]
        #goals_list = goals_list[:10]
        return goals_list

    
    except Exception as e:
        print(f"Error loading labels: {e}")


def _get_role_play_path(role_play_option: str):
    """Convert role play option string to RolePlayPaths enum value"""
    role_play_mapping = {
        "MR_ROBOT": RolePlayPaths.MR_ROBOT.value,
        "VIDEO_GAME": RolePlayPaths.VIDEO_GAME.value,
    }
    return role_play_mapping.get(role_play_option, RolePlayPaths.MR_ROBOT.value)


async def launch_attack(
    attack_option: str,
    label: str = "malicious_goals",
    seed: int = None,
    temperature_judges: float = None,
    target_model_name: str = None,
    attacker_model_name: str = None,
    judge_model_name: str = None,
    jury_models: list[str] = None,
    role_play_option: str = None,
):
    load_dotenv()
    
    # Use defaults for any parameter not provided
    seed = seed if seed is not None else DEFAULTS["seed"]
    temperature_judges = temperature_judges if temperature_judges is not None else DEFAULTS["temperature_judges"]
    target_model_name = target_model_name if target_model_name is not None else DEFAULTS["target_model_name"]
    attacker_model_name = attacker_model_name if attacker_model_name is not None else DEFAULTS["attacker_model_name"]
    judge_model_name = judge_model_name if judge_model_name is not None else DEFAULTS["judge_model_name"]
    jury_models = jury_models if jury_models is not None else DEFAULTS["jury_models"]
    role_play_path = _get_role_play_path(role_play_option) if role_play_option else RolePlayPaths.MR_ROBOT.value
    
    attacks_dict = {
        TypesOfAttacks.CRESCENDO_ATTACK.value: attacks.launch_crescendo_attack,
        TypesOfAttacks.FLIP_ATTACK.value: attacks.launch_flip_attack,
        TypesOfAttacks.ROLE_PLAY_ATTACK.value: attacks.launch_role_play_attack,  
    }
    if attack_option not in attacks_dict and attack_option != TypesOfAttacks.ALL_ATTACKS.value:
        raise ValueError(f"Invalid attack option: {attack_option}")
    
    #if attack_option is ALL_ATTACKS, run all attacks
    targets = attacks_dict.keys() if attack_option == TypesOfAttacks.ALL_ATTACKS.value else [attack_option] 
    for attack in targets:
        print(f"Executing attack: {attack}")
        await attacks_dict[attack](
            ollama_host=os.getenv("OLLAMA_BASE_URL"),
            seed=seed,
            temperature_judges=temperature_judges,
            attacker_model_name=attacker_model_name,
            judge_model_name=judge_model_name,
            jury_models=jury_models,
            target_model_name=target_model_name,
            goals_list=load_labels(label=label),
            role_play_option=role_play_path,
        )


async def launch_attack_template(
    label: str = Goals.MALICIOUS_GOALS.value,
    seed: int = None,
    temperature_judges: float = None,
    target_model_name: str = None,
    jury_models: list[str] = None,
):
    load_dotenv()
    
    # Use defaults for any parameter not provided
    seed = seed if seed is not None else DEFAULTS["seed"]
    temperature_judges = temperature_judges if temperature_judges is not None else DEFAULTS["temperature_judges"]
    target_model_name = target_model_name if target_model_name is not None else DEFAULTS["target_model_name"]
    jury_models = jury_models if jury_models is not None else DEFAULTS["jury_models"]
    
    await attacks.launch_attack_template(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=seed,
        temperature_judges=temperature_judges,
        attacker_model_name=DEFAULTS["attacker_model_name"],  # Not configurable for template
        judge_model_name=DEFAULTS["judge_model_name"],  # Not configurable for template
        jury_models=jury_models,
        target_model_name=target_model_name,
        goals_list=load_labels(label=label),
        label=label,
    )


async def launch_over_refusal_test(
    seed: int = None,
    temperature_judges: float = None,
    target_model_name: str = None,
    jury_models: list[str] = None,
):
    load_dotenv()
    
    # Use defaults for any parameter not provided
    seed = seed if seed is not None else DEFAULTS["seed"]
    temperature_judges = temperature_judges if temperature_judges is not None else DEFAULTS["temperature_judges"]
    target_model_name = target_model_name if target_model_name is not None else DEFAULTS["target_model_name"]
    jury_models = jury_models if jury_models is not None else DEFAULTS["jury_models"]
    
    await attacks.over_refusal_test(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=seed,
        temperature_judges=temperature_judges,
        target_model_name=target_model_name,
        jury_models=jury_models,
    )