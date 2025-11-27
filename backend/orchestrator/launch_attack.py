import os
from dotenv import load_dotenv
import json
import attacks

def load_labels(label: str):
    """
    Args:
        label (str): The type of labels to load. Must be either 
                     'malicious_goals' or 'vulnerable_goals'
    
    Returns:
        list[str]: List of prompt strings from the selected dataset
    """
    try:
        file_path = "datasets/" + label + ".json"
        "datasets/vulnerable_goals.json"
        with open(file_path, "r") as f:
            goals = json.load(f)

        #convert malicious_goals to a list of prompts
        goals_list = [goal['Prompt'] for goal in goals]
        #goals_list = goals_list[:10]
        return goals_list

    
    except Exception as e:
        print(f"Error loading labels: {e}")


def launch_attack(attack_option, label="malicious_goals"):
    load_dotenv()
    attacks_dict = {
        "CRESCENDO_ATTACK": attacks.launch_crescendo_attack,
        "FLIP_ATTACK": attacks.launch_flip_attack,
        "MR_ROBOT_ATTACK": attacks.launch_mr_robot_attack,  
    }
    if attack_option not in attacks_dict:
        raise ValueError(f"Invalid attack option: {attack_option}")
    
    #if attack_option is ALL_ATTACKS, run all attacks
    targets = attacks_dict.keys() if attack_option == "ALL_ATTACKS" else [attack_option] 

    for attack in targets:
        attacks_dict[attack](
            ollama_host=os.getenv("OLLAMA_HOST"),
            seed=2316,
            temperature_judges=0.1,
            attacker_model_name="gemma3:27b",
            judge_model_name="gemma3:27b",
            jury_models=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
            target_model_name="gemma3:27b",
            goals_list=load_labels(label=label),
        )


def main():
    launch_attack()

if __name__ == "__main__":
    main()