"""
Test 3: Scoring and Feedback
Add scores to traces to evaluate quality
"""
import os
from dotenv import load_dotenv
from langfuse import Langfuse
from openai import OpenAI

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

langfuse = Langfuse()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
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
