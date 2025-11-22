"""
Test 1: Automatic Tracing
Langfuse automatically traces all OpenAI SDK calls
"""
from config import *
from langfuse.openai import OpenAI

# Cliente com tracing automático
client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key='ollama',
)

print("🔄 Testing automatic tracing...")
response = client.chat.completions.create(
    model=OLLAMA_MODEL,
    messages=[{"role": "user", "content": "What is an autoencoder in one sentence?"}]
)
print(f"✅ Response: {response.choices[0].message.content}")
print("📊 Check Langfuse UI at http://localhost:3000 for the trace!")
