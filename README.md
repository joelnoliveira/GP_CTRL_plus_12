# GP_CTRL_plus_12
- Automated Red-Teaming of LLMs through Prompt-Based Attack Simulation

## 📚 Documentação

- **Relatórios de Tempo**: [reports/README.md](reports/README.md)
- **AMBIENTE DE DESENVOLVIMENTO VSCODE (DEVCONTAINER)**: [.devcontainer/README.md](.devcontainer/README.md)
- **Integração Langfuse**: [LANGFUSE_INTEGRATION.md](LANGFUSE_INTEGRATION.md)

## Containers

### Build e Startup de Containers
- O build e start dos containers são automáticos aquando da entrada nos devcontainers.

### Serviços Disponíveis
- **Backend (FastAPI)**: http://localhost:8000/docs
- **Langfuse UI**: http://localhost:3000
- **PostgreSQL (App)**: localhost:5432
- **PostgreSQL (Langfuse)**: localhost:5433
- **Ollama**: http://localhost:11434
- **React**: http://localhost:3001

### Configurar Langfuse (Opcional)
O Langfuse permite fazer tracing das chamadas aos LLMs. Para ativar:

1. Acede a http://localhost:3000
2. Cria uma conta (primeiro signup = admin)
3. Cria um projeto
4. Vai a **Settings** → **API Keys** e cria uma chave
5. Copia as chaves para `backend/.env`:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_ENABLED=true
   ```
6. Reinicia o backend

Se não quiseres usar Langfuse, deixa `LANGFUSE_ENABLED=false` no `.env`.

### Acesso a Containers
#### Aceder à Base de Dados
- Para aceder ao container existem duas opções:
    - Aceder através do Docker Desktop ou equivalente.
    - Executar numa linha de comandos externa:
        ``` sh
        docker-compose -f .devcontainer/coding/docker-compose.workspace.yml exec db sh
        ```
- Para aceder à Base de Dados executar no container:
    ``` sh
    psql -d postgres_db -U postgres    
    ```
- Listar tabelas da seed.sql:
    ``` sql
        \dt    
    ```
- Listar tabelas do langfuse:
    ``` sql
        \dt langfuse.*
    ```
#### Aceder ao Container do Ollama
- Duas opções:
    - Aceder através do Docker Desktop ou equivalente.
    - Executar numa linha de comandos externa:
        ``` sh
        docker-compose -f .devcontainer/coding/docker-compose.workspace.yml exec ollama sh
        ```
#### Aceder ao Container do Frontend
- Duas opções:
    - Aceder através do Docker Desktop ou equivalente.
    - Executar numa linha de comandos externa:
        ``` sh
        docker-compose -f .devcontainer/coding/docker-compose.workspace.yml exec frontend sh
        ```

#### Aceder ao Container do Backend (FastAPI)
- Ao entrar no devcontainer, o terminal embutido do VSCode acede automáticamente ao container do FastAPI.

## Executar o FastAPI
- Dentro do terminal do container do backend executar:
    ```
    cd "/workspace/backend"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 
    ```
- Após a execução o servidor estará disponível em : http://localhost:8000/docs

## Scripts de instalação dos modelos no ollama
- Assumindo que o script tem as permissões necessárias, executar o script (Bash ou .dat de acordo com o sistema operativo) localizado em [ollama/scripts/](ollama/scripts/) numa consola externa.
