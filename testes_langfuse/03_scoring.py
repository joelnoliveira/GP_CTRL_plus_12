"""
Test 3: Scoring and Feedback
Add scores to traces to evaluate quality
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

print("⭐ Testing scoring/feedback...")

# Create trace
trace = langfuse.trace(name="scored-generation")

# Generate response
response = client.chat.completions.create(
    model=OLLAMA_MODEL,
    messages=[{"role": "user", "content": "Explain neural networks in one sentence."}]
)

generation = trace.generation(
    name="neural-net-explanation",
    model=OLLAMA_MODEL,
    input=[{"role": "user", "content": "Explain neural networks in one sentence."}],
    output=response.choices[0].message.content
)

print(f"📝 Response: {response.choices[0].message.content}")

# Add scores
trace.score(
    name="accuracy",
    value=0.85,
    comment="Good but could be more precise"
)

trace.score(
    name="conciseness",
    value=0.95
)

trace.score(
    name="user-feedback",
    value=1
)

print(f"✅ Added 3 scores to trace {trace.id}")
langfuse.flush()
