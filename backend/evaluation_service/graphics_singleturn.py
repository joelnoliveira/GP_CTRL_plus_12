import json
import numpy as np
import matplotlib.pyplot as plt

def make_bar_chart_with_std(data, title, baseline_results=None):
    models = list(data.keys())
    refusal_rates = [data[model]['refusal_rate'] for model in models]
    acceptance_rates = [data[model]['acceptance_rate'] for model in models]
    refusal_stds = [data[model]['refusal_std'] for model in models]
    acceptance_stds = [data[model]['acceptance_std'] for model in models]

    for model in models:
        print(f'{model}: refusal rate: {data[model]["refusal_rate"]:.3f} (±{data[model]["refusal_std"]:.3f}), '
              f'acceptance rate: {data[model]["acceptance_rate"]:.3f} (±{data[model]["acceptance_std"]:.3f})')

    # Add spacing between models by multiplying positions by a spacing factor
    spacing_factor = 1.20  # Adjust this value to control spacing between models
    x = np.arange(len(models)) * spacing_factor
    width = 0.35

    fig, ax = plt.subplots(figsize=(13, 6))  # Create figure with custom size
    
    # Determine bar width based on whether baseline results are provided
    if baseline_results is not None:
        bar_width = width - 0.15
        
        # Add baseline results on the left side
        baseline_refusal_rates = [baseline_results[model]['refusal_rate'] if model in baseline_results else 0 for model in models]
        baseline_acceptance_rates = [baseline_results[model]['acceptance_rate'] if model in baseline_results else 0 for model in models]
        
        baseline_bars1 = ax.bar(x - 3*bar_width/2, baseline_refusal_rates, bar_width, 
                               color='red', alpha=0.6, edgecolor='darkred', linewidth=1, label='Baseline Refusal')
        baseline_bars2 = ax.bar(x - bar_width/2, baseline_acceptance_rates, bar_width, 
                               color='blue', alpha=0.6, edgecolor='darkblue', linewidth=1, label='Baseline Acceptance')
        
        # Normal bars on the right side
        bars1 = ax.bar(x + 0.5*bar_width, refusal_rates, bar_width, yerr=refusal_stds, 
                       color='red', label='Refusal', capsize=4)
        bars2 = ax.bar(x + 1.5*bar_width, acceptance_rates, bar_width, yerr=acceptance_stds,
                       color='blue', label='Acceptance', capsize=4)
        
        # Add text annotations for baseline bars in faded black
        for bar, rate in zip(baseline_bars1, baseline_refusal_rates):
            if rate > 0:  # Only show annotation if there's a value
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.00005,
                        f'{height:.3f}', ha='center', va='bottom', rotation=0, fontsize=12, color='black', alpha=0.6)

        for bar, rate in zip(baseline_bars2, baseline_acceptance_rates):
            if rate > 0:  # Only show annotation if there's a value
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.00005,
                        f'{height:.3f}', ha='center', va='bottom', rotation=0, fontsize=12, color='black', alpha=0.6)
    else:
        # Normal bars at full width when no baseline results
        bar_width = width
        bars1 = ax.bar(x - bar_width/2, refusal_rates, bar_width, yerr=refusal_stds, 
                       color='red', label='Refusal', capsize=4)
        bars2 = ax.bar(x + bar_width/2, acceptance_rates, bar_width, yerr=acceptance_stds,
                       color='blue', label='Acceptance', capsize=4)
    
    # Add faded horizontal line at y=1.0
    ax.axhline(y=1.0, color='gray', linestyle='-', alpha=0.5, linewidth=1)

    # Add text annotations to main bars
    for bar, std in zip(bars1, refusal_stds):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                f'{height:.3f}', ha='center', va='bottom', rotation=0, fontsize=14)

    for bar, std in zip(bars2, acceptance_stds):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                f'{height:.3f}', ha='center', va='bottom', rotation=0, fontsize=14)

    # Set larger font sizes for all text elements
    plt.xlabel('Models', fontsize=16)
    plt.ylabel('Rate', fontsize=16)
    plt.title(title, fontsize=18)
    plt.xticks(x, models, fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(0, 1.03)
    plt.legend(loc='upper right', fontsize=12)
    plt.tight_layout()
    plt.show()

malicious_or_vulnerable = "malicious"
type_role_play = "mrrobot_2"

# codellama
with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/codellama_1.json', 'r') as f:
    data_codellama_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/codellama_2.json', 'r') as f:
    data_codellama_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/codellama_3.json', 'r') as f:
    data_codellama_3 = json.load(f)

# llama2
with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama2_1.json', 'r') as f:
    data_llama2_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama2_2.json', 'r') as f:
    data_llama2_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama2_3.json', 'r') as f:
    data_llama2_3 = json.load(f)

# zephyr
with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/zephyr_1.json', 'r') as f:
    data_zephyr_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/zephyr_2.json', 'r') as f:
    data_zephyr_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/zephyr_3.json', 'r') as f:
    data_zephyr_3 = json.load(f)

# llama3.1
with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama3.1_8b_1.json', 'r') as f:
    data_llama3_1_8b_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama3.1_8b_2.json', 'r') as f:
    data_llama3_1_8b_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama3.1_8b_3.json', 'r') as f:
    data_llama3_1_8b_3 = json.load(f)

# llama3.1:70b
with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama3.1_70b_1.json', 'r') as f:
    data_llama3_1_70b_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama3.1_70b_2.json', 'r') as f:
    data_llama3_1_70b_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/llama3.1_70b_3.json', 'r') as f:
    data_llama3_1_70b_3 = json.load(f)

# gemma3:27b
with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/gemma3_27b_1.json', 'r') as f:
    data_gemma3_27b_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/gemma3_27b_2.json', 'r') as f:
    data_gemma3_27b_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/single_turn/role_play/{type_role_play}/gemma3_27b_3.json', 'r') as f:
    data_gemma3_27b_3 = json.load(f)

import json

def get_refusal_acceptance_rate_different_percentage_from_file(file_name, scorers_percentage):
    with open(file_name, 'r') as f:
        data = json.load(f)
    
    if sum(scorers_percentage) != 1:
        raise ValueError("The sum of the scorers_percentage should be 1")
    
    num_responses=0
    num_falses=0
    num_trues=0
    for i in data.keys():
        for j in data[i].keys():
            if data[i][j]['role'] == 'assistant':
                num_responses += 1
                if len(data[i][j]['scores']) > 1:
                    #get the scores
                    scores = data[i][j]['scores']
                    score_percentage = {'True': 0 , 'False': 0} #this will store the percentage of True and False scores based on the scorers_percentage
                    for index, score in enumerate(scores):
                        if score['score_value'] == "True":
                            score_percentage['True'] += scorers_percentage[index]
                        else:
                            score_percentage['False'] += scorers_percentage[index]
                    
                    #now we need to check if the score is true or false
                    if score_percentage['True'] > score_percentage['False']:
                        num_trues += 1
                    elif score_percentage['True'] < score_percentage['False']:
                        num_falses += 1
                    else:
                        print("ERROR")
                        return
            
    return num_falses/num_responses, num_trues/num_responses, num_responses
    


num_falses_zephyr, num_trues_zephyr, num_responses_zephyr = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_zephyr.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_llama2, num_trues_llama2, num_responses_llama2 = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_llama2.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_codellama, num_trues_codellama, num_responses_codellama = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_codellama.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_llama3_1, num_trues_llama3_1, num_responses_llama3_1 = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_llama3.1.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_gemma3_27b, num_trues_gemma3_27b, num_responses_gemma3_27b = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_gemma3:27b.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_llama3_1_70b, num_trues_llama3_1_70b, num_responses_llama3_1_70b = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_llama3.1:70b.json', scorers_percentage=[0.5, 0.25, 0.25])


baseline_data = {
    "Zephyr": {
        "refusal_rate": num_trues_zephyr,
        "acceptance_rate": num_falses_zephyr
    },
    "Llama2": {
        "refusal_rate": num_trues_llama2,
        "acceptance_rate": num_falses_llama2
    },
    "CodeLlama": {
        "refusal_rate": num_trues_codellama,
        "acceptance_rate": num_falses_codellama
    },
    "Llama3.1:8b": {
        "refusal_rate": num_trues_llama3_1,
        "acceptance_rate": num_falses_llama3_1
    },
    "Llama3.1:70b": {
        "refusal_rate": num_trues_llama3_1_70b,
        "acceptance_rate": num_falses_llama3_1_70b
    },
    "Gemma3:27b": {
        "refusal_rate": num_trues_gemma3_27b,
        "acceptance_rate": num_falses_gemma3_27b
    }
}

#assert len(data_codellama_1) == len(data_codellama_2) == len(data_codellama_3) == len(data_llama2_1) == len(data_llama2_2) == len(data_llama2_3) == len(data_zephyr_1) == len(data_zephyr_2) == len(data_zephyr_3) == len(data_llama3_1_8b_1) == len(data_llama3_1_8b_2) == len(data_llama3_1_8b_3)
num_responses = len(data_codellama_1)

def num_falses_file(data):
    num_falses=0 # not refusals
    for i in data.keys():
        for j in data[i].keys():
            if (data[i][j]['role'] == "assistant"):
                if(len(data[i][j]['scores']) != 0):
                    if(data[i][j]['scores'][0]['score_value']== "False"):
                        num_falses += 1
    return num_falses

def num_trues_file(data):
    num_trues=0 # refusals
    for i in data.keys():
        for j in data[i].keys():
            if (data[i][j]['role'] == "assistant"):
                if(len(data[i][j]['scores']) != 0):
                    if(data[i][j]['scores'][0]['score_value']== "True"):
                        num_trues += 1
    return num_trues 


# Calculate rates and standard deviations for each model across the 3 runs

# Define datasets mapping similar to multi-turn notebook
datasets_map = {
    
    #"Codellama": [data_codellama_1],
    #"Llama2": [data_llama2_1],
    #"Zephyr": [data_zephyr_1],
    #"Llama3.1:8b": [data_llama3_1_8b_1],
    #"Llama3.1:70b": [data_llama3_1_70b_1],
    #"Gemma3:27b": [data_gemma3_27b_1]

    "Zephyr": [data_zephyr_1, data_zephyr_2, data_zephyr_3],
    "Llama2": [data_llama2_1, data_llama2_2, data_llama2_3],
    "CodeLlama": [data_codellama_1, data_codellama_2, data_codellama_3],
    "Llama3.1:8b": [data_llama3_1_8b_1, data_llama3_1_8b_2, data_llama3_1_8b_3],
    "Llama3.1:70b": [data_llama3_1_70b_1, data_llama3_1_70b_2, data_llama3_1_70b_3],
    "Gemma3:27b": [data_gemma3_27b_1, data_gemma3_27b_2, data_gemma3_27b_3]
}

model_names = list(datasets_map.keys())

# Calculate acceptance/refusal rates for each individual run, then take mean and std
model_acceptance_rates_per_run = {model: [] for model in model_names}
model_refusal_rates_per_run = {model: [] for model in model_names}

for model_name, list_of_model_datasets in datasets_map.items():
    for individual_dataset_run in list_of_model_datasets:
        n_falses = num_falses_file(individual_dataset_run)
        n_trues = num_trues_file(individual_dataset_run)
        
        # Calculate rate for this specific run
        acceptance_rate = n_falses / num_responses
        refusal_rate = n_trues / num_responses
        
        model_acceptance_rates_per_run[model_name].append(acceptance_rate)
        model_refusal_rates_per_run[model_name].append(refusal_rate)
        
        print(f"{model_name} run {len(model_acceptance_rates_per_run[model_name])}: {n_falses}/{num_responses} acceptance = {acceptance_rate:.3f} acceptance rate")

# Calculate means and standard deviations
mean_acceptance_rates = {}
std_acceptance_rates = {}
mean_refusal_rates = {}
std_refusal_rates = {}

for model_name in model_names:
    acceptance_rates = model_acceptance_rates_per_run[model_name]
    refusal_rates = model_refusal_rates_per_run[model_name]
    
    mean_acceptance_rates[model_name] = np.mean(acceptance_rates)
    std_acceptance_rates[model_name] = np.std(acceptance_rates)
    mean_refusal_rates[model_name] = np.mean(refusal_rates)
    std_refusal_rates[model_name] = np.std(refusal_rates)


# Prepare data for plotting with standard deviations
data = {
    model: {
        "refusal_rate": mean_refusal_rates[model],
        "acceptance_rate": mean_acceptance_rates[model], 
        "refusal_std": std_refusal_rates[model],
        "acceptance_std": std_acceptance_rates[model]
    } for model in model_names
}

make_bar_chart_with_std(data, f"{malicious_or_vulnerable.title()} - Single Turn Role Play (Mr. Robot ) - 3 runs each, {num_responses} entries per run", baseline_results=baseline_data)


