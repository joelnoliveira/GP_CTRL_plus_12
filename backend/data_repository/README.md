# CRUD - Funções de Leitura e Escrita da Base de Dados

Este módulo fornece funções para interagir com a base de dados PostgreSQL do projeto.

## 📋 Índice

- [Funções de Leitura](#funções-de-leitura)
- [Funções de Escrita](#funções-de-escrita)
- [Como Usar](#como-usar)
- [Testes](#testes)

## 📖 Funções de Leitura

### Funções Genéricas

#### `read_all_from_table(db, table_name, limit=None)`
Lê todos os registros de uma tabela específica.

```python
from data_repository import crud
from app.database import SessionLocal

db = SessionLocal()
users = crud.read_all_from_table(db, "users", limit=10)
db.close()
```

#### `read_by_id(db, table_name, record_id)`
Lê um registro específico por ID.

```python
user = crud.read_by_id(db, "users", 1)
```

### Usuários

#### `read_users(db, limit=None)`
Retorna todos os usuários.

#### `read_user_by_id(db, user_id)`
Retorna um usuário específico por ID.

#### `read_user_by_email(db, email)`
Retorna um usuário específico por email.

```python
users = crud.read_users(db, limit=50)
user = crud.read_user_by_id(db, 1)
user = crud.read_user_by_email(db, "admin@example.com")
```

### Cenários

#### `read_scenarios(db, limit=None)`
Retorna todos os cenários.

#### `read_scenario_by_id(db, scenario_id)`
Retorna um cenário específico por ID.

```python
scenarios = crud.read_scenarios(db)
scenario = crud.read_scenario_by_id(db, 1)
```

### Datasets de Workload

#### `read_workload_datasets(db, scenario_id=None)`
Retorna datasets de workload. Se `scenario_id` for fornecido, filtra por cenário.

#### `read_workload_dataset_by_id(db, dataset_id)`
Retorna um dataset específico por ID.

```python
datasets = crud.read_workload_datasets(db)
datasets_scenario = crud.read_workload_datasets(db, scenario_id=1)
dataset = crud.read_workload_dataset_by_id(db, 1)
```

### Cargas de Ataque

#### `read_attack_loads(db, limit=None)`
Retorna todas as cargas de ataque.

#### `read_attack_load_by_id(db, attack_id)`
Retorna uma carga de ataque específica por ID.

```python
attacks = crud.read_attack_loads(db)
attack = crud.read_attack_load_by_id(db, 1)
```

### Métricas de Execução

#### `read_runs_metrics(db, limit=None)`
Retorna todas as métricas de execução.

#### `read_run_metric_by_id(db, run_id)`
Retorna uma métrica de execução específica por ID.

#### `read_runs_by_user(db, user_id)`
Retorna todas as execuções de um usuário específico.

#### `read_run_with_details(db, run_id)`
Retorna uma execução completa com detalhes (JOIN com outras tabelas).

#### `read_recent_runs(db, limit=10)`
Retorna as execuções mais recentes com informações resumidas.

```python
runs = crud.read_runs_metrics(db, limit=10)
run = crud.read_run_metric_by_id(db, 1)
user_runs = crud.read_runs_by_user(db, user_id=1)
run_details = crud.read_run_with_details(db, run_id=1)
recent = crud.read_recent_runs(db, limit=5)
```

### Votos do Júri

#### `read_jury_votes(db, run_id=None)`
Retorna os votos do júri. Se `run_id` for fornecido, filtra por execução.

```python
all_votes = crud.read_jury_votes(db)
run_votes = crud.read_jury_votes(db, run_id=1)
```

## ✍️ Funções de Escrita

### Usuários

#### `create_user(db, email, password, role=False, created_at=None)`
Cria um novo usuário.

```python
user = crud.create_user(
    db,
    email="novo@example.com",
    password="senha_hash",
    role=False  # False=user, True=admin
)
print(f"Usuário criado com ID: {user['id']}")
```

#### `bulk_create_users(db, users)`
Cria múltiplos usuários de uma vez.

```python
users = [
    {"email": "user1@test.com", "password": "hash1", "role": False},
    {"email": "user2@test.com", "password": "hash2", "role": False}
]
count = crud.bulk_create_users(db, users)
print(f"{count} usuários criados")
```

### Cenários

#### `create_scenario(db, name, description, created_at=None)`
Cria um novo cenário.

```python
scenario = crud.create_scenario(
    db,
    name="Meu Cenário de Teste",
    description="Descrição detalhada do cenário"
)
```

### Datasets de Workload

#### `create_workload_dataset(db, name, description, storage_path, scenarios_id, is_builtin=False, created_at=None)`
Cria um novo dataset de workload.

```python
dataset = crud.create_workload_dataset(
    db,
    name="Meu Dataset",
    description="Dataset personalizado",
    storage_path="/data/my_dataset.json",
    scenarios_id=1,
    is_builtin=False
)
```

### Cargas de Ataque

#### `create_attack_load(db, name, description, type, storage_path, is_builtin=False, created_at=None)`
Cria uma nova carga de ataque.

```python
attack = crud.create_attack_load(
    db,
    name="Custom Attack",
    description="Meu ataque personalizado",
    type="custom",
    storage_path="/attacks/custom.yaml",
    is_builtin=False
)
```

### Métricas de Execução

#### `create_run_metric(db, ...)`
Cria uma nova métrica de execução. Requer muitos parâmetros - veja exemplo completo:

```python
from datetime import datetime

run = crud.create_run_metric(
    db,
    target_model="gpt-4",
    attack_model="gemma-3",
    visibility="public",
    status="completed",
    langfuse_trace_id="trace_abc123",
    started_at=datetime.now(),
    ended_at=datetime.now(),
    metrics_asr=85,
    metrics_orr=90,
    metrics_aor=80,
    metrics_useful_majority=True,
    metrics_veridict_majority=True,
    workload_datasets_id=1,
    attack_loads_id=1,
    scenarios_id=1,
    users_id=1
)
```

### Votos do Júri

#### `create_jury_vote(db, usefulness, model_name, runs_metrics_id, jury_index=None, veridict=None, created_at=None)`
Cria um novo voto do júri.

```python
vote = crud.create_jury_vote(
    db,
    usefulness=True,
    veridict=True,
    model_name="gpt-4-judge",
    runs_metrics_id=1,
    jury_index=1
)
```

### Popular Base de Dados

#### `seed_database(db)`
Popula a base de dados com dados de exemplo para testes.

```python
counts = crud.seed_database(db)
print(f"Criados: {counts}")
# Output: {'users': 3, 'scenarios': 2, 'workload_datasets': 1, 'attack_loads': 2}
```

## 🚀 Como Usar

### 1. Uso Simples (Script Python)

```python
from app.database import SessionLocal
from data_repository import crud

# Criar sessão
db = SessionLocal()

try:
    # Ler dados
    users = crud.read_users(db, limit=10)
    print(f"Total de usuários: {len(users)}")
    
    # Criar dados
    new_user = crud.create_user(
        db,
        email="test@example.com",
        password="hashed_password"
    )
    print(f"Novo usuário ID: {new_user['id']}")
    
finally:
    db.close()
```

### 2. Uso com FastAPI

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from data_repository import crud

app = FastAPI()

@app.get("/api/users")
def get_users(db: Session = Depends(get_db)):
    users = crud.read_users(db, limit=50)
    return {"users": users}

@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.read_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users")
def create_user_endpoint(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = crud.create_user(db, email, password)
    return user
```

## 🧪 Testes

### Testar Funções de Leitura

```bash
cd /workspace/backend
python test_crud.py
```

### Popular Base de Dados com Dados de Teste

```bash
cd /workspace/backend
python seed_database.py
```

Escolha uma das opções:
1. Usar função automática `seed_database()`
2. Popular manualmente (mostra cada passo)
3. Apenas verificar dados existentes

### Exemplos de Uso

```bash
cd /workspace/backend
python exemplo_uso_crud.py
```

## 📝 Notas Importantes

1. **Sempre feche a sessão**: Use `try/finally` ou context managers
2. **Tratamento de erros**: As funções podem lançar exceções do SQLAlchemy
3. **Transações**: As funções de escrita fazem `db.commit()` automaticamente
4. **Senhas**: Em produção, sempre use hash para senhas (ex: bcrypt)
5. **SQL Injection**: As funções usam `text()` com parâmetros para prevenir SQL injection

## 🔒 Segurança

```python
# ✅ BOM - Usa parâmetros
user = crud.read_user_by_email(db, "user@example.com")

# ❌ RUIM - Nunca faça isso
query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL Injection!
```

## 📊 Estrutura de Retorno

Todas as funções de leitura retornam:
- **Listas**: `List[Dict[str, Any]]` - Para múltiplos registros
- **Dict ou None**: `Optional[Dict[str, Any]]` - Para registro único

Exemplo de estrutura:
```python
{
    'id': 1,
    'email': 'user@example.com',
    'role': False,
    'created_at': datetime(2025, 12, 3, 22, 51, 51)
}
```
