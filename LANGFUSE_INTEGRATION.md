# Integração Langfuse - Documentação

## 📋 Visão Geral

Este projeto integra o **Langfuse v2** para tracing e observabilidade de chamadas a LLMs (Large Language Models). O Langfuse permite monitorizar, debugar e melhorar aplicações que usam modelos de linguagem.

## 🏗️ Arquitetura

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    Stack Completa                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Backend (FastAPI)  ←→  Langfuse Client (Python SDK)       │
│         ↓                       ↓                           │
│    Ollama LLM          Langfuse Server (v2.95)             │
│         ↓                       ↓                           │
│  PostgreSQL App        PostgreSQL Langfuse                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Serviços Docker

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `backend` | 8000 | FastAPI - API principal |
| `langfuse-web` | 3000 | Langfuse UI |
| `ollama` | 11434 | Servidor Ollama (LLMs locais) |
| `postgres__db` | 5432 | PostgreSQL da aplicação |

## 🚀 Quick Start

### 1. Levantar os Containers

```bash
# Parar Ollama nativo (se estiver a correr)
sudo systemctl stop ollama

# Levantar toda a stack
docker-compose -f .devcontainer/coding/docker-compose.workspace.yml up -d

# Verificar estado
docker-compose -f .devcontainer/coding/docker-compose.workspace.yml ps
```

### 2. Configurar Langfuse

1. **Aceder à UI**: http://localhost:3000
2. **Criar conta** (primeiro signup = admin)
3. **Criar organização e projeto**
4. **Gerar API keys**: Settings → API Keys → Create new API key
5. **Copiar chaves** para os ficheiros `.env`:

```bash
# backend/.env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxx
LANGFUSE_ENABLED=true

# testes_langfuse/.env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxx
```

### 3. Instalar Modelo Ollama

```bash
# Já instalado: llama3.2:1b
# Para instalar outros modelos:
docker exec ollama ollama pull <modelo>
docker exec ollama ollama list
```

### 4. Testar a Integração

```bash
cd testes_langfuse
./run_all.sh
```

Verifica os traces em http://localhost:3000 → Traces

## 📁 Estrutura de Ficheiros

```
backend/
├── app/
│   ├── config/
│   │   └── langfuse.py          # Cliente Langfuse configurado
│   ├── main.py                  # FastAPI app
│   └── ...
├── .env                         # Variáveis de ambiente (com API keys)
├── .env.example                 # Template
└── requirements.txt             # langfuse<3.0.0

testes_langfuse/
├── 01_auto_tracing.py          # Tracing automático (OpenAI SDK)
├── 02_manual_tracing.py        # Tracing manual com spans
├── 03_scoring.py               # Adicionar scores/feedback
├── 04_prompts.py               # Gestão de prompt templates
├── 05_datasets.py              # Datasets para avaliação
├── 06_events.py                # Logging de eventos
├── config.py                   # Carregamento de .env
├── .env                        # Configuração de testes
└── run_all.sh                  # Executar todos os testes
```

## 💻 Uso no Backend

### Importar e Usar

```python
from app.config.langfuse import get_langfuse_client

# Obter cliente (retorna None se não configurado)
langfuse = get_langfuse_client()

if langfuse:
    # Criar trace
    trace = langfuse.trace(
        name="llm-request",
        user_id="user-123",
        metadata={"endpoint": "/api/generate"}
    )
    
    # Adicionar generation
    generation = trace.generation(
        name="openai-call",
        model="llama3.2:1b",
        input=[{"role": "user", "content": "Hello"}],
        output="Hi there!"
    )
    
    # Adicionar score
    trace.score(name="quality", value=0.9)
    
    # Flush (garantir envio)
    langfuse.flush()
```

### Tracing Automático com OpenAI SDK

```python
from langfuse.openai import OpenAI

# Cliente com auto-tracing
client = OpenAI(
    base_url="http://ollama:11434/v1",
    api_key="ollama"
)

# Todas as chamadas são automaticamente traced!
response = client.chat.completions.create(
    model="llama3.2:1b",
    messages=[{"role": "user", "content": "What is AI?"}]
)
```

## 🧪 Scripts de Teste

### Executar Todos

```bash
cd testes_langfuse
./run_all.sh
```

### Executar Individual

```bash
python 01_auto_tracing.py    # Tracing automático
python 02_manual_tracing.py  # Tracing manual
python 03_scoring.py         # Scores
python 04_prompts.py         # Prompt templates
python 05_datasets.py        # Datasets
python 06_events.py          # Events
```

## 🔧 Configuração

### Variáveis de Ambiente (backend/.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres_db

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...     # Obter da UI
LANGFUSE_SECRET_KEY=sk-lf-...     # Obter da UI
LANGFUSE_HOST=http://langfuse-web:3000
LANGFUSE_ENABLED=true             # false para desabilitar

# Ollama (opcional)
OLLAMA_BASE_URL=http://ollama:11434/v1
```

### Versões

- **Langfuse Server**: v2.95.11 (Docker)
- **Langfuse Python SDK**: v2.60.10 (compatível com v2.x)
- **Python**: 3.10+
- **Ollama**: latest

⚠️ **Importante**: Usamos Langfuse v2 (não v3) porque é mais estável e sem dependências extras (ClickHouse, Redis, MinIO).

## 🐛 Troubleshooting

### Langfuse não aparece nada na UI

1. **Verifica se o projeto está correto** na UI
2. **Verifica as API keys** no `.env`
3. **Refresca a página** (F5)
4. **Verifica se `LANGFUSE_ENABLED=true`**

### Erro: "address already in use" (porta 11434)

```bash
# Parar Ollama nativo
sudo systemctl stop ollama

# Reiniciar containers
docker-compose -f .devcontainer/coding/docker-compose.workspace.yml restart ollama
```

### Warning: "Failed to export span batch code: 404"

- Incompatibilidade entre SDK v3 e servidor v2
- **Solução**: Verificar que tens `langfuse<3.0.0` no `requirements.txt`

```bash
pip uninstall -y langfuse
pip install "langfuse<3.0.0"
```

### Backend não inicia

```bash
# Entrar no container
docker exec -it fast_api bash

# Iniciar manualmente
cd /workspace/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Funcionalidades Langfuse

### ✅ Implementadas

- [x] **Tracing automático** (OpenAI SDK wrapper)
- [x] **Tracing manual** (traces, spans, generations)
- [x] **Scoring** (adicionar feedback/avaliações)
- [x] **Prompt Management** (templates reutilizáveis)
- [x] **Datasets** (casos de teste para avaliação)
- [x] **Events** (logging de ações do sistema)

### 🔜 Por Implementar

- [ ] Integração no backend FastAPI
- [ ] Dashboard personalizado
- [ ] Alertas automáticos
- [ ] A/B testing de prompts
- [ ] Fine-tuning baseado em traces

## 🔒 Segurança

⚠️ **Nunca committes as API keys!**

Os ficheiros `.env` estão no `.gitignore`. Usa sempre `.env.example` como template.

Para produção:
1. Gerar chaves de encriptação seguras
2. Usar secrets management (Vault, AWS Secrets, etc)
3. Ativar autenticação no Langfuse
4. Usar HTTPS

## 📚 Recursos

- **Langfuse Docs**: https://langfuse.com/docs
- **API Reference**: https://api.reference.langfuse.com
- **Python SDK**: https://pypi.org/project/langfuse/
- **Ollama**: https://ollama.ai

## 🤝 Contribuir

1. **Criar branch** a partir de `main`
2. **Testar** com `./testes_langfuse/run_all.sh`
3. **Verificar** traces na UI
4. **Commit** sem API keys
5. **Pull Request**

## 📝 Notas

- O Langfuse está configurado para **desenvolvimento local**
- Para **produção**, ajustar passwords e chaves de encriptação
- O container `backend` inicia em modo idle - iniciar FastAPI manualmente ou ajustar comando
- Modelos Ollama são persistidos em `ollama/ollama_data/`

---

**Criado em**: Novembro 2024  
**Versão**: 1.0  
**Última atualização**: 21/11/2024
