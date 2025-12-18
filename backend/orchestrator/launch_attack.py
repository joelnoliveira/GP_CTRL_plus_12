import os
from dotenv import load_dotenv
import json
#import attacks
from orchestrator import attacks
from orchestrator.constants import TypesOfAttacks, Goals

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
            attacker_model_name="llama3.2:1b",
            judge_model_name="llama3.2:1b",
            jury_models=["llama3.2:1b", "llama3.2:1b", "llama3.2:1b"],
            target_model_name="llama3.2:1b",
            goals_list=load_labels(label=label),
        )


async def launch_attack_template(attack_option, label=Goals.MALICIOUS_GOALS.value):
    load_dotenv()
    #to do: implemente the attack templates in attacks.py and import them here
    attacks_dict = {
        TypesOfAttacks.CRESCENDO_ATTACK.value: None, #attacks.launch_crescendo_attack_template,
        TypesOfAttacks.FLIP_ATTACK.value: None, #attacks.launch_flip_attack_template,
        TypesOfAttacks.MR_ROBOT_ATTACK.value: None, #attacks.launch_mr_robot_attack_template,  
    }
    if attack_option not in attacks_dict:
        raise ValueError(f"Invalid attack option: {attack_option}")
    
    #if attack_option is ALL_ATTACKS, run all attacks
    targets = attacks_dict.keys() if attack_option == TypesOfAttacks.ALL_ATTACKS.value else [attack_option] 
    for attack in targets:
        print("executing attack template")
        await attacks_dict[attack](
            ollama_host=os.getenv("OLLAMA_BASE_URL"),
            seed=2316,
            temperature_judges=0.1,
            attacker_model_name="llama3.2:1b",
            judge_model_name="llama3.2:1b",
            jury_models=["llama3.2:1b", "llama3.2:1b", "llama3.2:1b"],
            target_model_name="llama3.2:1b",
            goals_list=load_labels(label=label),
        )

async def launch_over_refusal_test():
    load_dotenv()
    await attacks.over_refusal_test(
        ollama_host=os.getenv("OLLAMA_BASE_URL"),
        seed=2316,
        temperature_judges=0.1,
        target_model_name = "llama3.2:1b",
        jury_models = ["llama3.2:1b", "llama3.2:1b", "llama3.2:1b"],
    )