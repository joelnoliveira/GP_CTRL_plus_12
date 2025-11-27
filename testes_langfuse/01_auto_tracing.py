"""
Test 1: Automatic Tracing
Langfuse automatically traces all OpenAI SDK calls
"""
import os
from dotenv import load_dotenv
from langfuse import observe, get_client
from openai import OpenAI

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

# Cliente OpenAI NORMAL (sem wrapper do Langfuse)
client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key='ollama',
)

@observe()
def main():
    print("🔄 Testing automatic tracing (via decorator)...")
    
    # Opcional: Definir nome do trace
    langfuse_client = get_client()
    langfuse_client.update_current_trace(
        name="auto-tracing-test-v3",
        user_id="test-user"
    )
 
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": "What is an autoencoder in one sentence?"}]
    )
    print(f"✅ Response: {response.choices[0].message.content}")
    
    return response

if __name__ == "__main__":
    # Configurar Langfuse (lê do ambiente)
    # Certifica-te que LANGFUSE_PUBLIC_KEY e LANGFUSE_SECRET_KEY estão no .env
    
    try:
        main()
        # Flush explícito via client
        get_client().flush()
        print("📊 Check Langfuse UI at http://localhost:3000 for the trace!")
    except Exception as e:
        print(f"❌ Error: {e}")

