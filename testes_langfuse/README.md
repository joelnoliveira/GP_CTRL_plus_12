# Langfuse Local Testing

Testes de integração com Langfuse (self-hosted) + Ollama para observabilidade de LLMs.

## 🚀 Setup

### 1. Levantar Langfuse (Docker)

```bash
# Levantar todos os serviços
docker compose up -d

# Verificar se está tudo up
docker compose ps
```

Serviços disponíveis:
- **Langfuse UI**: http://localhost:3000
- **Postgres**: localhost:5432
- **ClickHouse**: localhost:8123
- **Redis**: localhost:6379
- **MinIO**: localhost:9090

### 2. Criar Organização, Projeto e API Keys

1. Acede a http://localhost:3000
2. Cria uma conta (primeiro signup = admin)
3. Cria uma **organização**
4. Cria um **projeto**
5. Vai a **Settings** → **API Keys** e cria:
   - No primeiro campo ele vai pedir uma descrição é opcional somente de clicar em "Create API Key" é que ele gera as keys.
   - Warning: Esta é a única vez que as keys são mostradas!
   - Public Key (pk-lf-...)
   - Secret Key (sk-lf-...)

### 3. Configurar `.env`

Atualiza o ficheiro `.env` com as tuas keys:

```bash
# Langfuse API Keys
LANGFUSE_PUBLIC_KEY=pk-lf-XXXXXXXX
LANGFUSE_SECRET_KEY=sk-lf-XXXXXXXX
LANGFUSE_HOST=http://localhost:3000

# Ollama Config
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=gemma3:4b
```

### 4. Instalar Dependências Python

```bash
# Criar ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar packages
pip install langfuse openai
```

### 5. Garantir Ollama a Correr

```bash
# Verificar se Ollama está up
curl http://localhost:11434/api/tags

# Pull do modelo (se necessário)
ollama pull gemma3:4b
```

## 📊 Testes Disponíveis

### Scripts de Teste

| Script | Descrição |
|--------|-----------|
| `01_auto_tracing.py` | **Tracing automático** - Integração OpenAI SDK com logging automático |
| `02_manual_tracing.py` | **Tracing manual** - Criar traces, spans e generations manualmente |
| `03_scoring.py` | **Scoring/Feedback** - Adicionar scores de qualidade às traces |
| `04_prompts.py` | **Prompt Management** - Criar e usar templates de prompts |
| `05_datasets.py` | **Datasets** - Criar datasets de teste e correr avaliações |
| `06_events.py` | **Events** - Logging de eventos custom (user actions, etc) |

### Executar Testes

**Individual:**
```bash
python 01_auto_tracing.py
python 02_manual_tracing.py
# etc...
```

**Todos de uma vez:**
```bash
chmod +x run_all.sh
./run_all.sh
```

## 🔍 Validar Resultados

Acede ao Langfuse UI em http://localhost:3000 e verifica:

- **Traces** → Vê todas as execuções com timings e metadata
- **Generations** → Detalhes de cada chamada LLM (tokens, latency, cost)
- **Scores** → Feedback e avaliações de qualidade
- **Prompts** → Templates criados e versionados
- **Datasets** → Test sets e resultados de avaliações
- **Events** → Eventos custom logados

## 🛑 Parar Tudo

```bash
# Parar serviços
docker compose down

# Parar e eliminar volumes (reset completo)
docker compose down -v
```

## 📁 Estrutura do Projeto

```
.
├── .env                    # Configuração (keys, URLs)
├── config.py               # Loader de config
├── docker-compose.yml      # Stack Langfuse
├── 01_auto_tracing.py      # Teste: auto tracing
├── 02_manual_tracing.py    # Teste: manual tracing
├── 03_scoring.py           # Teste: scoring
├── 04_prompts.py           # Teste: prompts
├── 05_datasets.py          # Teste: datasets
├── 06_events.py            # Teste: events
├── run_all.sh              # Script para correr tudo
└── README.md               # Este ficheiro
```

## 💡 Notas

- **Primeiro run**: Pode demorar ~1-2 min para migrations das DBs
- **Keys**: Podes regenerar as API keys no Langfuse UI a qualquer altura
- **Modelo**: Muda `OLLAMA_MODEL` no `.env` para testar outros modelos
- **Dados**: Os dados persistem nos volumes Docker (postgres, clickhouse)

## 🐛 Troubleshooting

**Langfuse não arranca:**
```bash
docker compose logs langfuse-web
docker compose logs postgres
```

**Python não encontra langfuse:**
```bash
pip install --upgrade langfuse openai
```

**Ollama timeout:**
```bash
# Verifica se está a correr
systemctl status ollama  # Linux
# ou
ps aux | grep ollama     # Mac
```
