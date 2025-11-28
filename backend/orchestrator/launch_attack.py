import os
from dotenv import load_dotenv
import json
#import attacks
from orchestrator import attacks
from orchestrator.constants import TypesOfAttacks

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
        goals_list = goals_list[:10]
        return goals_list

    
    except Exception as e:
        print(f"Error loading labels: {e}")


async def launch_attack(attack_option, label="malicious_goals"):
    load_dotenv()
    attacks_dict = {
        TypesOfAttacks.CRESCENDO_ATTACK.value: attacks.launch_crescendo_attack,
        TypesOfAttacks.FLIP_ATTACK.value: attacks.launch_flip_attack,
        TypesOfAttacks.MR_ROBOT_ATTACK.value: attacks.launch_mr_robot_attack,  
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
            attacker_model_name="dolphin3:8b",
            judge_model_name="dolphin3:8b",
            jury_models=["dolphin3:8b"],
            target_model_name="dolphin3:8b",
            goals_list=load_labels(label=label),
        )
