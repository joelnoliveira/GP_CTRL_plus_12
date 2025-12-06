import json

#open multi_turn results, there are 3 for each model

malicious_or_vulnerable = "vulnerable"

# codellama
with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/codellama_1.json', 'r') as f:
    data_codellama_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/codellama_2.json', 'r') as f:
    data_codellama_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/codellama_3.json', 'r') as f:
    data_codellama_3 = json.load(f)

# llama2
with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama2_1.json', 'r') as f:
    data_llama2_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama2_2.json', 'r') as f:
    data_llama2_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama2_3.json', 'r') as f:
    data_llama2_3 = json.load(f)

# zephyr
with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/zephyr_1.json', 'r') as f:
    data_zephyr_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/zephyr_2.json', 'r') as f:
    data_zephyr_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/zephyr_3.json', 'r') as f:
    data_zephyr_3 = json.load(f)

# llama3.1
with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama3.1_8b_1.json', 'r') as f:
    data_llama3_1_8b_1 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama3.1_8b_2.json', 'r') as f:
    data_llama3_1_8b_2 = json.load(f)

with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama3.1_8b_3.json', 'r') as f:
    data_llama3_1_8b_3 = json.load(f)


if malicious_or_vulnerable=="malicious":
    # llama3.1:70b
    with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama3.1_70b_1.json', 'r') as f:
        data_llama3_1_70b_1 = json.load(f)

    with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama3.1_70b_2.json', 'r') as f:
        data_llama3_1_70b_2 = json.load(f)

    with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/llama3.1_70b_3.json', 'r') as f:
        data_llama3_1_70b_3 = json.load(f)

    #gemma3:27b
    with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/gemma3_27b_1.json', 'r') as f:
        data_gemma3_27b_1 = json.load(f)

    with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/gemma3_27b_2.json', 'r') as f:
        data_gemma3_27b_2 = json.load(f)

    with open(f'results/attacker_llm/{malicious_or_vulnerable}/multi_turn/gemma3_27b_3.json', 'r') as f:
        data_gemma3_27b_3 = json.load(f)


del f

assert len(data_codellama_1) == len(data_codellama_2) == len(data_codellama_3) == len(data_llama2_1) == len(data_llama2_2) == len(data_llama2_3) == len(data_zephyr_1) == len(data_zephyr_2) == len(data_zephyr_3)

for i in range(len(data_codellama_3)):
    #check if the objective was achieved for each entry and in how many turns
    if(data_codellama_3[i]['achieved_objective']):
        turns=0
        for j in range(len(data_codellama_3[i]['messages'])):
            if(data_codellama_3[i]['messages'][j]['role'] == 'user'):
                turns+=1
        print(f"Codellama achieved objective in {turns} turns")
    else:
        print(f"Codellama did not achieve objective")


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


num_falses_zephyr, num_trues_zephyr, num_responses_zephyr = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_zephyr.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_llama2, num_trues_llama2, num_responses_llama2 = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_llama2.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_codellama, num_trues_codellama, num_responses_codellama = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_codellama.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_llama3_1, num_trues_llama3_1, num_responses_llama3_1 = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_llama3.1.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_gemma3_27b, num_trues_gemma3_27b, num_responses_gemma3_27b = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_gemma3:27b.json', scorers_percentage=[0.5, 0.25, 0.25])

num_falses_llama3_1_70b, num_trues_llama3_1_70b, num_responses_llama3_1_70b = get_refusal_acceptance_rate_different_percentage_from_file(f'results/new_judging_system/{malicious_or_vulnerable}/no_adversarial/after_human_judge_llama3.1:70b.json', scorers_percentage=[0.5, 0.25, 0.25])


baseline_data = {
    "zephyr": {
        "refusal_rate": num_trues_zephyr,
        "acceptance_rate": num_falses_zephyr
    },
    "llama2": {
        "refusal_rate": num_trues_llama2,
        "acceptance_rate": num_falses_llama2
    },
    "codellama": {
        "refusal_rate": num_trues_codellama,
        "acceptance_rate": num_falses_codellama
    },
    "llama3.1:8b": {
        "refusal_rate": num_trues_llama3_1,
        "acceptance_rate": num_falses_llama3_1
    },
    "llama3.1:70b": {
        "refusal_rate": num_trues_llama3_1_70b,
        "acceptance_rate": num_falses_llama3_1_70b
    },
    "gemma3:27b": {
        "refusal_rate": num_trues_gemma3_27b,
        "acceptance_rate": num_falses_gemma3_27b
    }
}

import matplotlib.pyplot as plt
import numpy as np

# --- Configuration: Ensure your data variables are correctly named here ---
# These should be lists of dictionaries as per your data structure
# Example: data_codellama_1 = [{"achieved_objective": True, "messages": [...]}, ...]

datasets_map = {
    "zephyr": [data_zephyr_1, data_zephyr_2, data_zephyr_3],
    "llama2": [data_llama2_1, data_llama2_2, data_llama2_3],
    "codellama": [data_codellama_1, data_codellama_2, data_codellama_3],
    "llama3.1:8b": [data_llama3_1_8b_1, data_llama3_1_8b_2, data_llama3_1_8b_3],
    "llama3.1:70b": [data_llama3_1_70b_1, data_llama3_1_70b_2, data_llama3_1_70b_3],
    "gemma3:27b": [data_gemma3_27b_1, data_gemma3_27b_2, data_gemma3_27b_3]
}
model_names = list(datasets_map.keys())

# --- Metrics Collection for Refusal/Acceptance Rates ---
# Calculate success/refusal rate for each individual run, then take mean and std
model_acceptance_rates_per_run = {model: [] for model in model_names}
model_refusal_rates_per_run = {model: [] for model in model_names}

for model_name, list_of_model_datasets in datasets_map.items():
    for individual_dataset_run in list_of_model_datasets:
        num_entries = len(individual_dataset_run)
        if num_entries == 0:
            model_acceptance_rates_per_run[model_name].append(0.0)
            model_refusal_rates_per_run[model_name].append(1.0)
            continue
            
        achieved_count = 0
        for entry in individual_dataset_run:
            if entry.get('achieved_objective', False):
                achieved_count += 1
        
        # Calculate rate for this specific run (e.g., out of 31 entries)
        acceptance_rate = achieved_count / num_entries
        refusal_rate = 1.0 - acceptance_rate
        
        model_acceptance_rates_per_run[model_name].append(acceptance_rate)
        model_refusal_rates_per_run[model_name].append(refusal_rate)
        
        print(f"{model_name} run {len(model_acceptance_rates_per_run[model_name])}: {achieved_count}/{num_entries} successful = {acceptance_rate:.3f} acceptance rate")

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
    width = 0.175  # Half the original width (was 0.35)

    fig, ax = plt.subplots(figsize=(13,6))
    
    # Plot baseline results first (on the left)
    if baseline_results is not None:
        baseline_refusal_rates = [baseline_results[model]['refusal_rate'] for model in models if model in baseline_results]
        baseline_acceptance_rates = [baseline_results[model]['acceptance_rate'] for model in models if model in baseline_results]
        baseline_refusal_stds = [baseline_results[model].get('refusal_std', 0) for model in models if model in baseline_results]
        baseline_acceptance_stds = [baseline_results[model].get('acceptance_std', 0) for model in models if model in baseline_results]
        
        baseline_x = x[:len(baseline_refusal_rates)]
        
        # Position baseline bars on the left side
        baseline_bars1 = ax.bar(baseline_x - 1.5*width, baseline_refusal_rates, width, 
                               yerr=baseline_refusal_stds, color='red', label='Baseline Refusal', 
                               capsize=3, alpha=0.6, edgecolor='darkred', linewidth=1)
        baseline_bars2 = ax.bar(baseline_x - 0.5*width, baseline_acceptance_rates, width, 
                               yerr=baseline_acceptance_stds, color='blue', label='Baseline Acceptance', 
                               capsize=3, alpha=0.6, edgecolor='darkblue', linewidth=1)
    
    # Plot main results on the right side
    bars1 = ax.bar(x + 0.5*width, refusal_rates, width, yerr=refusal_stds, 
                   color='red', label='Refusal', capsize=4, alpha=0.8)
    bars2 = ax.bar(x + 1.5*width, acceptance_rates, width, yerr=acceptance_stds,
                   color='blue', label='Acceptance', capsize=4, alpha=0.8)
    
    # Add faded horizontal line at y=1.0
    ax.axhline(y=1.0, color='gray', linestyle='-', alpha=0.5, linewidth=1)

    # Add text annotations to baseline bars if they exist
    if baseline_results is not None:
        for bar, std in zip(baseline_bars1, baseline_refusal_stds):
            height = bar.get_height()
        
            ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', rotation=0, fontsize=12, 
                    color='black', alpha=0.7)

        for bar, std in zip(baseline_bars2, baseline_acceptance_stds):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', rotation=0, fontsize=12, 
                    color='black', alpha=0.7)

    # Add text annotations to main bars
    for i in range(len(models)):
        # Handle bars1 (refusal rates)
        height1 = bars1[i].get_height()
        std1 = refusal_stds[i]
        height2 = bars2[i].get_height()
        std2 = acceptance_stds[i]
        
        if height1 > 0:
            ax.text(bars1[i].get_x() + bars1[i].get_width()/2., height1 + std1 + 0.01,
                        f'{height1:.3f}', ha='center', va='bottom', rotation=0, fontsize=14)
        elif height1 == 0 and height2 == 0:
            ax.text(bars1[i].get_x() + bars1[i].get_width()/2., std1 + 0.01,
                    'X', ha='center', va='bottom', rotation=0, fontsize=14)

        # Handle bars2 (acceptance rates)
        if height2 > 0:
            ax.text(bars2[i].get_x() + bars2[i].get_width()/2., height2 + std2 + 0.01,
                        f'{height2:.3f}', ha='center', va='bottom', rotation=0, fontsize=14)
        elif height1 == 0 and height2 == 0:
            ax.text(bars2[i].get_x() + bars2[i].get_width()/2., std2 + 0.01,
                    'X', ha='center', va='bottom', rotation=0, fontsize=14)

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

# Prepare data for plotting
data = {
    model: {
        "refusal_rate": mean_refusal_rates[model],
        "acceptance_rate": mean_acceptance_rates[model], 
        "refusal_std": std_refusal_rates[model],
        "acceptance_std": std_acceptance_rates[model]
    } for model in model_names
}

if malicious_or_vulnerable == 'vulnerable':
    data["llama3.1:70b"]['refusal_rate'] = 0
    data["llama3.1:70b"]['acceptance_rate'] = 0
    data['llama3.1:70b']['refusal_std'] = 0
    data['llama3.1:70b']['acceptance_std'] = 0

    data["gemma3:27b"]['refusal_rate'] = 0
    data["gemma3:27b"]['acceptance_rate'] = 0
    data['gemma3:27b']['refusal_std'] = 0
    data['gemma3:27b']['acceptance_std'] = 0

make_bar_chart_with_std(data, f"Multi-turn Attack Success/Refusal Rates (3 runs each, {len(data_codellama_1)} entries per run)", baseline_results=baseline_data)


# --- Additional Analysis: Collect turn data for successful attempts ---
model_all_successful_turns_combined = {model: [] for model in model_names}

for model_name, list_of_model_datasets in datasets_map.items():
    for individual_dataset_run in list_of_model_datasets:
        for entry in individual_dataset_run:
            if entry.get('achieved_objective', False):
                turns = 0
                messages = entry.get('messages', [])
                if isinstance(messages, list):
                    for message in messages:
                        if isinstance(message, dict) and message.get('role') == 'user':
                            turns += 1
                    model_all_successful_turns_combined[model_name].append(turns)

# --- Plot 2: Distribution of All Successful Turns (Combined across dataset runs) ---
turns_data_for_boxplot = []
model_labels_for_boxplot = []
model_color_map = {"codellama": '#1f77b4', "llama2": '#ff7f0e', "zephyr": '#2ca02c', "llama3.1:8b": '#d62728'}

for model_name in model_names:
    combined_turns = model_all_successful_turns_combined[model_name]
    if combined_turns:
        turns_data_for_boxplot.append(combined_turns)
        model_labels_for_boxplot.append(model_name)

if turns_data_for_boxplot:
    plt.figure(figsize=(10, 6))
    bp = plt.boxplot(turns_data_for_boxplot, tick_labels=model_labels_for_boxplot, patch_artist=True, vert=True, widths=0.6)
    
    for i, patch in enumerate(bp['boxes']):
        box_model_name = model_labels_for_boxplot[i]
        patch.set_facecolor(model_color_map.get(box_model_name, '#BEBEBE'))
        patch.set_alpha(0.75)

    plt.xlabel("Model", fontsize=16)
    plt.ylabel("Number of User Turns (for successful attempts)", fontsize=16)
    plt.title("Distribution of User Turns for Successful Attempts (All Dataset Runs Combined)", fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout(pad=1.5)
    plt.show()
else:
    print("No successful attempts with turn data found across all models.")

# --- Print Mean and Standard Deviation of Turns ---
print("\n--- Mean and Standard Deviation of Turns for Successful Attempts (all dataset runs combined) ---")
for model_name in model_names:
    turns_list = model_all_successful_turns_combined[model_name]
    if turns_list:
        mean_turns = np.mean(turns_list)
        std_dev_turns = np.std(turns_list)
        num_successes_with_turns = len(turns_list)
        print(f"{model_name}: Mean Turns = {mean_turns:.2f}, Std Dev = {std_dev_turns:.2f} (from {num_successes_with_turns} successful attempts with turn data)")
    else:
        print(f"{model_name}: No successful attempts with turn data found.")

