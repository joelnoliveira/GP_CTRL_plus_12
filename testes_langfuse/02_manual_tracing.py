"""
Test 2: Manual Tracing
Create traces manually with custom spans and metadata
"""
from config import *
from langfuse import Langfuse
from openai import OpenAI
import os

# Set env vars for langfuse
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

langfuse = Langfuse()

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key='ollama',
)

print("🔧 Testing manual tracing...")

# Create trace context
trace_id = langfuse.create_trace_id()
trace_context = {"trace_id": trace_id}

print(f"Created trace: {trace_id}")

# Step 1: Document retrieval span
retrieval_span = langfuse.start_span(
    trace_context=trace_context,
    name="document-retrieval",
    input={"query": "autoencoder"},
    metadata={"num_docs": 3}
)
retrieval_span.update(output={"docs": ["doc1", "doc2", "doc3"]})
retrieval_span.end()

# Step 2: LLM generation
prompt = "What is an autoencoder?"
response = client.chat.completions.create(
    model=OLLAMA_MODEL,
    messages=[{"role": "user", "content": prompt}]
)

generation = langfuse.start_observation(
    trace_context=trace_context,
    as_type="generation",
    name="llm-generation",
    model=OLLAMA_MODEL,
    input=[{"role": "user", "content": prompt}],
)
generation.update(
    output=response.choices[0].message.content,
    usage={
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens
    }
)
generation.end()

print(f"✅ Trace ID: {trace_id}")
print(f"📊 Response: {response.choices[0].message.content}")
langfuse.flush()
