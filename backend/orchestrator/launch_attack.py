import os
from dotenv import load_dotenv
import json
import yaml
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
    temperature_target: float = None,
    temperature_attacker: float = None,
    target_model_name: str = None,
    attacker_model_name: str = None,
    judge_model_name: str = None,
    jury_models: list[str] = None,
    role_play_option: str = None,
    config_file_name: str = None,
    goals_file_name: str = None,
    target_provider: str = "OLLAMA",
    api_key:str = None,
):
    load_dotenv()

    if config_file_name:
        config_path = os.path.join("custom_configs", config_file_name)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Custom config file not found: {config_file_name}")
            
        try:
            with open(config_path, "r") as f:
                if config_file_name.endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            
            if config.get("seed") is not None: seed = config.get("seed")
            if config.get("temperature_judges") is not None: temperature_judges = config.get("temperature_judges")
            if config.get("temperature_attacker") is not None: temperature_attacker = config.get("temperature_attacker")
            if config.get("temperature_target") is not None: temperature_target = config.get("temperature_target")
            if config.get("target_model_name") is not None: target_model_name = config.get("target_model_name")
            if config.get("attacker_model_name") is not None: attacker_model_name = config.get("attacker_model_name")
            if config.get("judge_model_name") is not None: judge_model_name = config.get("judge_model_name")
            if config.get("jury_models") is not None: jury_models = config.get("jury_models")
            if config.get("label") is not None: label = config.get("label")
            if config.get("role_play_option") is not None: role_play_option = config.get("role_play_option")
            if config.get("goals_file_name") is not None: goals_file_name = config.get("goals_file_name")
        except Exception as e:
            raise ValueError(f"Error loading custom config: {e}")
    
    # Load goals
    final_goals_list = []
    if goals_file_name:
        # Se for um path absoluto, usar diretamente
        if os.path.isabs(goals_file_name):
            goals_path = goals_file_name
        else:
            # Path relativo - procurar em uploads primeiro, depois em datasets
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            goals_path = os.path.join(base_path, "datasets", "uploads", goals_file_name)
            
            if not os.path.exists(goals_path):
                # Fallback para datasets (ficheiros builtin)
                goals_path = os.path.join(base_path, "datasets", goals_file_name)
        
        if not os.path.exists(goals_path):
            raise FileNotFoundError(f"Custom goals file not found: {goals_path}")
        
        try:
            with open(goals_path, "r", encoding='utf-8') as f:
                goals_data = json.load(f)
                # Malicious goals format: [{"Id": 1, "Prompt": "..."}]
                if isinstance(goals_data, list):
                    for item in goals_data:
                        if "Prompt" in item:
                            final_goals_list.append(item["Prompt"])
                        else:
                             # Fallback if just a list of strings
                             if isinstance(item, str):
                                 final_goals_list.append(item)
                else:
                    raise ValueError("Invalid goals file format. Expected a JSON list.")
        except Exception as e:
             raise ValueError(f"Error loading custom goals file: {e}")
    else:
        final_goals_list = load_labels(label=label)
    
    # Use defaults for any parameter not provided
    seed = seed if seed is not None else DEFAULTS["seed"]
    temperature_judges = temperature_judges if temperature_judges is not None else DEFAULTS["temperature_judges"]
    temperature_attacker = temperature_attacker if temperature_attacker is not None else DEFAULTS["temperature_attacker"]
    temperature_target = temperature_target if temperature_target is not None else DEFAULTS["temperature_target"]
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
            label=label,
            target_provider=target_provider,
            temperature_judges=temperature_judges,
            temperature_attacker= temperature_attacker,
            temperature_target = temperature_target,
            attacker_model_name=attacker_model_name,
            judge_model_name=judge_model_name,
            jury_models=jury_models,
            target_model_name=target_model_name,
            goals_list=final_goals_list,
            role_play_option=role_play_path,
            api_key=api_key,
        )


async def launch_attack_template(
    label: str = Goals.MALICIOUS_GOALS.value,
    seed: int = None,
    temperature_judges: float = None,
    temperature_attacker: float = None,
    temperature_target: float = None,
    target_model_name: str = None,
    jury_models: list[str] = None,
    template_path: str = None,
    target_provider: str = "OLLAMA",
    api_key:str = None,
):
    load_dotenv()
    
    # Use defaults for any parameter not provided
    seed = seed if seed is not None else DEFAULTS["seed"]
    temperature_judges = temperature_judges if temperature_judges is not None else DEFAULTS["temperature_judges"]
    temperature_attacker = temperature_attacker if temperature_attacker is not None else DEFAULTS["temperature_attacker"]
    temperature_target = temperature_target if temperature_target is not None else DEFAULTS["temperature_target"]
    target_model_name = target_model_name if target_model_name is not None else DEFAULTS["target_model_name"]
    jury_models = jury_models if jury_models is not None else DEFAULTS["jury_models"]
    
    await attacks.launch_attack_template(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=seed,
        target_provider=target_provider,
        temperature_judges=temperature_judges,
        temperature_attacker=temperature_attacker,
        temperature_target=temperature_target,
        attacker_model_name=DEFAULTS["attacker_model_name"],  # Not configurable for template
        judge_model_name=DEFAULTS["judge_model_name"],  # Not configurable for template
        jury_models=jury_models,
        target_model_name=target_model_name,
        goals_list=load_labels(label=label),
        label=label,
        template_path=template_path,
        api_key=api_key,
    )


async def launch_over_refusal_test(
    seed: int = None,
    temperature_judges: float = None,
    temperature_attacker: float = None,
    temperature_target: float = None,
    target_model_name: str = None,
    jury_models: list[str] = None,
    target_provider: str = "OLLAMA",
    api_key:str = None,
):
    load_dotenv()
    
    # Use defaults for any parameter not provided
    seed = seed if seed is not None else DEFAULTS["seed"]
    temperature_judges = temperature_judges if temperature_judges is not None else DEFAULTS["temperature_judges"]
    temperature_attacker = temperature_attacker if temperature_attacker is not None else DEFAULTS["temperature_attacker"]
    temperature_target = temperature_target if temperature_target is not None else DEFAULTS["temperature_target"]
    target_model_name = target_model_name if target_model_name is not None else DEFAULTS["target_model_name"]
    jury_models = jury_models if jury_models is not None else DEFAULTS["jury_models"]
    
    await attacks.over_refusal_test(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=seed,
        target_provider=target_provider,
        temperature_judges=temperature_judges,
        temperature_attacker=temperature_attacker,
        temperature_target=temperature_target,
        target_model_name=target_model_name,
        jury_models=jury_models,
        api_key=api_key,
    )