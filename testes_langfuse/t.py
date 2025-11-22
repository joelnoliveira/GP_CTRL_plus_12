
from langfuse import Langfuse
import os

LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
LANGFUSE_HOST = os.getenv('LANGFUSE_HOST')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

from langfuse import Langfuse
import requests
from requests.auth import HTTPBasicAuth
# Importar do config.py para carregar as variáveis de ambiente corretamente
from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

# Na v2, instanciamos diretamente (as chaves já estão no os.environ via config)
langfuse = Langfuse()

# Para listar datasets na v2, a forma mais direta é via API REST
print(f"A consultar Langfuse em: {LANGFUSE_HOST}")
print("Datasets disponíveis:")

try:
    url = f"{LANGFUSE_HOST}/api/public/datasets"
    # A API do Langfuse usa Basic Auth (User=Public Key, Pass=Secret Key)
    auth = HTTPBasicAuth(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    
    response = requests.get(url, auth=auth, timeout=5)
    
    if response.status_code == 200:

        data = response.json()
        # A resposta pode ser uma lista direta ou um objeto com 'data'
        items = data.get('data', data) if isinstance(data, dict) else data
        
        if not items:
            print(" - Nenhum dataset encontrado.")
        
        for ds in items:
            print(f"- {ds.get('name')} (Items: {len(ds.get('items', []))})")
    else:
        print(f"Erro ao listar datasets: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Erro de conexão: {e}")

