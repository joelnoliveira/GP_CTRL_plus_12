# GP_CTRL_plus_12
- Automated Red-Teaming of LLMs through Prompt-Based Attack Simulation

## Relatórios de Tempo

- Os relatórios automáticos de tempo estão disponíveis em:
[reports/README.md](reports/README.md)

## Acesso aos Devcontainers

- A documentação relativa aos devcontainers encontra-se disponível em [.devcontainer/README.md](.devcontainer/README.md)

## Containers

### Build e Startup de Containers
- O build e start dos containers são automáticos aquando da entrada nos devcontainers.

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
#### Aceder ao Container do Ollama
- Duas opções:
    - Aceder através do Docker Desktop ou equivalente.
    - Executar numa linha de comandos externa:
        ``` sh
        docker-compose -f .devcontainer/coding/docker-compose.workspace.yml exec ollama sh
        ```

#### Aceder ao Container do Backend (FastAPI)
- Ao entrar no devcontainer, o terminal embutido do VSCode acede automáticamente ao container do FastAPI.

## Executar o FastAPI
- Dentro do terminal do container do backend executar:
    ```
    cd "/workspace/backend/app"
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
    ```
- Após a execução o servidor estará disponível em : http://localhost:8000/docs
