"""
Test 7: Read / Consult Langfuse Data
- Cria um trace e lê via API pública
- Lê prompt (se existir) via HTTP
- Lê dataset e items via HTTP

SDK v2 não expõe métodos fetch_prompt/fetch_dataset; usamos chamadas REST.
"""
import os
import json
import time
from typing import Optional
import requests
from config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
)
from langfuse import Langfuse
from openai import OpenAI

# Set env vars para SDK (ingest)
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

lf = Langfuse()
client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

HOST = LANGFUSE_HOST.rstrip("/")

def _headers():
    return {
        "X-Langfuse-Public-Key": LANGFUSE_PUBLIC_KEY,
        "X-Langfuse-Secret-Key": LANGFUSE_SECRET_KEY,
        "Content-Type": "application/json",
    }

def get_trace(trace_id: str) -> Optional[dict]:
    url = f"{HOST}/api/public/traces/{trace_id}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"⚠️ Trace fetch HTTP {r.status_code}: {r.text[:120]}")
    return None

def get_prompt(name: str) -> Optional[dict]:
    # Endpoint de prompts (padrão: ?name=NAME)
    url = f"{HOST}/api/public/prompts?name={name}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        # v2 pode devolver lista ou objeto; normalizar
        if isinstance(data, dict) and data.get("name"):
            return data
        if isinstance(data, list) and data:
            return data[0]
        return None
    print(f"⚠️ Prompt fetch HTTP {r.status_code}: {r.text[:120]}")
    return None

def get_dataset(name: str) -> Optional[dict]:
    url = f"{HOST}/api/public/datasets/{name}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"⚠️ Dataset fetch HTTP {r.status_code}: {r.text[:120]}")
    return None

def get_dataset_items(name: str) -> list:
    url = f"{HOST}/api/public/datasets/{name}/items"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        return data if isinstance(data, list) else []
    print(f"⚠️ Dataset items fetch HTTP {r.status_code}: {r.text[:120]}")
    return []

print("🔎 Reading Langfuse data (via SDK + REST)...")

# 1. Criar trace via SDK
trace = lf.trace(name="read-info-trace", metadata={"origin": "read-script"})
prompt = "Explain briefly what an autoencoder is."
resp = client.chat.completions.create(
    model=OLLAMA_MODEL,
    messages=[{"role": "user", "content": prompt}]
)

trace.generation(
    name="read-info-generation",
    model=OLLAMA_MODEL,
    input=[{"role": "user", "content": prompt}],
    output=resp.choices[0].message.content,
)
lf.flush()

print(f"🧪 Created trace id: {trace.id}")

# Pequeno delay para garantir ingestão
time.sleep(1.2)

trace_data = get_trace(trace.id)
if trace_data:
    print("📥 Trace fetched via REST ✅")
    keys = list(trace_data.keys())
    print(f"🔍 Trace keys: {keys[:12]} ...")
    summary = {k: trace_data.get(k) for k in ["id", "name", "createdAt", "userId", "sessionId"] if k in trace_data}
    print(f"🗂 Trace resumo: {summary}")
else:
    print("❌ Não foi possível obter trace via REST.")

# 2. Prompt
prompt_name = "greeting-template"
prompt_data = get_prompt(prompt_name)
if prompt_data:
    print(f"📝 Prompt '{prompt_name}' encontrado: version={prompt_data.get('version')} id={prompt_data.get('id')}")
else:
    print(f"❌ Prompt '{prompt_name}' não encontrado. Corre 04_prompts.py primeiro.")

# 3. Dataset
dataset_name = "ml-concepts-qa"
dataset_data = get_dataset(dataset_name)
if dataset_data:
    print(f"📊 Dataset '{dataset_name}' encontrado: id={dataset_data.get('id')}")
    items = get_dataset_items(dataset_name)
    print(f"📋 Items: {len(items)}")
    for it in items[:3]:
        _input = it.get("input") or it.get("prompt")
        _expected = it.get("expected_output") or it.get("expectedOutput")
        print(f"   - {_input} -> {_expected}")
else:
    print(f"❌ Dataset '{dataset_name}' não encontrado. Corre 05_datasets.py primeiro.")

print("✅ Finished read operations. Confirma na UI.")