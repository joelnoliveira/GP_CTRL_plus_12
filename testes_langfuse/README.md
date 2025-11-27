# Langfuse Local Testing

Testes de integração com Langfuse (self-hosted) + Ollama para observabilidade de LLMs.

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

## 📁 Estrutura do Projeto

```
.
├── 01_auto_tracing.py      # Teste: auto tracing
├── 02_manual_tracing.py    # Teste: manual tracing
├── 03_scoring.py           # Teste: scoring
├── 04_prompts.py           # Teste: prompts
├── 05_datasets.py          # Teste: datasets
├── 06_events.py            # Teste: events
├── run_all.sh              # Script para correr tudo
└── README.md               # Este ficheiro
```
