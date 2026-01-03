import os
from dotenv import load_dotenv
import json
#import attacks
from orchestrator import attacks
from orchestrator.constants import TypesOfAttacks, Goals
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


async def launch_attack(attack_option, label=Goals.MALICIOUS_GOALS.value):
    load_dotenv()
    attacks_dict = {
        TypesOfAttacks.CRESCENDO_ATTACK.value: attacks.launch_crescendo_attack,
        TypesOfAttacks.FLIP_ATTACK.value: attacks.launch_flip_attack,
        TypesOfAttacks.ROLE_PLAY_ATTACK.value: attacks.launch_role_play_attack,  
    }
    if attack_option not in attacks_dict:
        raise ValueError(f"Invalid attack option: {attack_option}")
    
    #if attack_option is ALL_ATTACKS, run all attacks
    targets = attacks_dict.keys() if attack_option == TypesOfAttacks.ALL_ATTACKS.value else [attack_option] 
    for attack in targets:
        print("executing attack")
        await attacks_dict[attack](
            ollama_host=os.getenv("OLLAMA_BASE_URL"),
            seed=2316,
            temperature_judges=0.1,
            attacker_model_name="qwen2.5:7b",
            judge_model_name="qwen2.5:7b",
            jury_models=["qwen2.5:7b", "qwen2.5:7b", "qwen2.5:7b"],
            target_model_name="qwen2.5:7b",
            goals_list=load_labels(label=label),
            label=label,
            role_play_option=RolePlayPaths.MR_ROBOT.value,
        )


async def launch_attack_template(label=Goals.MALICIOUS_GOALS.value):
    load_dotenv()
    await attacks.launch_attack_template(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=2316,
        temperature_judges=0.1,
        attacker_model_name="qwen2.5:7b",
        judge_model_name="qwen2.5:7b",
        jury_models=["qwen2.5:7b", "qwen2.5:7b", "qwen2.5:7b"],
        target_model_name="qwen2.5:7b",
        goals_list=load_labels(label=label),
        label=label,
    )

async def launch_over_refusal_test():
    load_dotenv()
    await attacks.over_refusal_test(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=2316,
        temperature_judges=0.1,
        target_model_name = "qwen2.5:7b",
        jury_models = ["qwen2.5:7b", "qwen2.5:7b", "qwen2.5:7b"],
    )