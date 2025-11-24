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
trace_id = langfuse.create_trace_id()
trace_context = {"trace_id": trace_id}

# Generate response
response = client.chat.completions.create(
    model=OLLAMA_MODEL,
    messages=[{"role": "user", "content": "Explain neural networks in one sentence."}]
)

generation = langfuse.start_observation(
    trace_context=trace_context,
    as_type="generation",
    name="neural-net-explanation",
    model=OLLAMA_MODEL,
)
generation.update(output=response.choices[0].message.content)
generation.end()

print(f"📝 Response: {response.choices[0].message.content}")

# Add scores
langfuse.create_score(
    trace_id=trace_id,
    name="accuracy",
    value=0.85,
    comment="Good but could be more precise"
)

langfuse.create_score(
    trace_id=trace_id,
    name="conciseness",
    value=0.95
)

langfuse.create_score(
    trace_id=trace_id,
    name="user-feedback",
    value=1,
    data_type="BOOLEAN"
)

print(f"✅ Added 3 scores to trace {trace_id}")
langfuse.flush()
