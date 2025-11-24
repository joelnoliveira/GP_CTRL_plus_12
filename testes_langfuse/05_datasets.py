"""
Test 5: Datasets and Evaluation
Create test datasets and run evaluations
"""
from config import *
from langfuse import Langfuse
from openai import OpenAI

langfuse = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST
)

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key='ollama',
)

print("📊 Testing datasets...")

# Criar dataset
dataset_name = "ml-concepts-qa"
try:
    langfuse.create_dataset(name=dataset_name)
    print(f"✅ Created dataset: {dataset_name}")
except:
    print(f"⚠️  Dataset {dataset_name} already exists")

# Adicionar test cases
test_cases = [
    {
        "input": {"question": "What is an autoencoder?"},
        "expected_output": "A neural network that learns to compress and reconstruct data"
    },
    {
        "input": {"question": "What is backpropagation?"},
        "expected_output": "An algorithm to calculate gradients for training neural networks"
    },
    {
        "input": {"question": "What is overfitting?"},
        "expected_output": "When a model performs well on training data but poorly on new data"
    }
]

for idx, case in enumerate(test_cases):
    try:
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input=case["input"],
            expected_output=case["expected_output"]
        )
        print(f"✅ Added test case {idx+1}")
    except:
        print(f"⚠️  Test case {idx+1} might already exist")

# Evaluate model on dataset
print("\n🧪 Running evaluation...")

dataset = langfuse.get_dataset(dataset_name)

for item in dataset.items:
    trace_id = langfuse.create_trace_id()
    trace_context = {"trace_id": trace_id}
    
    question = item.input["question"]
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": question}]
    )
    
    generation = langfuse.start_observation(
        trace_context=trace_context,
        as_type="generation",
        name="eval-generation",
        model=OLLAMA_MODEL,
        metadata={
            "dataset_item_id": item.id,
            "dataset_name": dataset_name
        }
    )
    generation.update(output=response.choices[0].message.content)
    generation.end()
    
    print(f"✅ Evaluated: {question[:50]}...")

langfuse.flush()
print("📊 Check Langfuse UI for evaluation results!")
