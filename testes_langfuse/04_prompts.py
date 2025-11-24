"""
Test 4: Prompt Management
Create and use prompt templates from Langfuse
"""
from config import *
from langfuse import Langfuse
from openai import OpenAI
import os

os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

langfuse = Langfuse()

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key='ollama',
)

print("📝 Testing prompt management...")

# Create prompt template
try:
    prompt = langfuse.create_prompt(
        name="greeting-template",
        prompt="Hello {{name}}, you are a {{role}}. Please {{task}}.",
        config={
            "model": OLLAMA_MODEL,
            "temperature": 0.7
        }
    )
    print(f"✅ Created prompt: {prompt.name}")
except Exception as e:
    print(f"⚠️  Prompt might already exist, fetching...")
    prompt = langfuse.get_prompt("greeting-template")

# Compile prompt
compiled_text = prompt.compile(
    name="Alice",
    role="data scientist",
    task="explain what an autoencoder is"
)

print(f"🔧 Compiled prompt: {compiled_text}")

# Use with LLM
trace_id = langfuse.create_trace_id()
trace_context = {"trace_id": trace_id}

response = client.chat.completions.create(
    model=OLLAMA_MODEL,
    messages=[{"role": "user", "content": compiled_text}]
)

generation = langfuse.start_observation(
    trace_context=trace_context,
    as_type="generation",
    name="templated-response",
    model=OLLAMA_MODEL,
)
generation.update(output=response.choices[0].message.content)
generation.end()

print(f"✅ Response: {response.choices[0].message.content[:150]}...")
langfuse.flush()
