from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime


def read_all_from_table(db: Session, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Lê todos os registros de uma tabela específica.
    
    Args:
        db: Sessão do banco de dados
        table_name: Nome da tabela a ser consultada
        limit: Limite opcional de registros a retornar
    
    Returns:
        Lista de dicionários com os registros da tabela
    """
    query = f"SELECT * FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"
    
    result = db.execute(text(query))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def read_by_id(db: Session, table_name: str, record_id: int) -> Optional[Dict[str, Any]]:
    """
    Lê um registro específico por ID.
    
    Args:
        db: Sessão do banco de dados
        table_name: Nome da tabela
        record_id: ID do registro
    
    Returns:
        Dicionário com os dados do registro ou None se não encontrado
    """
    query = text(f"SELECT * FROM {table_name} WHERE id = :id")
    result = db.execute(query, {"id": record_id})
    row = result.fetchone()
    
    if row:
        columns = result.keys()
        return dict(zip(columns, row))
    return None


def read_users(db: Session, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lê todos os usuários da base de dados."""
    return read_all_from_table(db, "users", limit)


def read_user_by_id(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """Lê um usuário específico por ID."""
    return read_by_id(db, "users", user_id)


def read_user_by_email(db: Session, email: str) -> Optional[Dict[str, Any]]:
    """Lê um usuário específico por email."""
    query = text("SELECT * FROM users WHERE email = :email")
    result = db.execute(query, {"email": email})
    row = result.fetchone()
    
    if row:
        columns = result.keys()
        return dict(zip(columns, row))
    return None


def read_runs_metrics(db: Session, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lê todas as métricas de execução."""
    return read_all_from_table(db, "runs_metrics", limit)


def read_run_metric_by_id(db: Session, run_id: int) -> Optional[Dict[str, Any]]:
    """Lê uma métrica de execução específica por ID."""
    return read_by_id(db, "runs_metrics", run_id)


def read_runs_by_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Lê todas as execuções de um usuário específico."""
    query = text("SELECT * FROM runs_metrics WHERE users_id = :user_id ORDER BY started_at DESC")
    result = db.execute(query, {"user_id": user_id})
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def read_jury_votes(db: Session, run_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Lê os votos do júri. Se run_id for fornecido, filtra por execução.
    """
    if run_id:
        query = text("SELECT * FROM jury_votes WHERE runs_metrics_id = :run_id")
        result = db.execute(query, {"run_id": run_id})
    else:
        query = text("SELECT * FROM jury_votes")
        result = db.execute(query)
    
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def read_scenarios(db: Session, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lê todos os cenários."""
    return read_all_from_table(db, "scenarios", limit)


def read_scenario_by_id(db: Session, scenario_id: int) -> Optional[Dict[str, Any]]:
    """Lê um cenário específico por ID."""
    return read_by_id(db, "scenarios", scenario_id)


def read_workload_datasets(db: Session, scenario_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Lê os datasets de workload. Se scenario_id for fornecido, filtra por cenário.
    """
    if scenario_id:
        query = text("SELECT * FROM workload_datasets WHERE scenarios_id = :scenario_id")
        result = db.execute(query, {"scenario_id": scenario_id})
    else:
        query = text("SELECT * FROM workload_datasets")
        result = db.execute(query)
    
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def read_workload_dataset_by_id(db: Session, dataset_id: int) -> Optional[Dict[str, Any]]:
    """Lê um dataset de workload específico por ID."""
    return read_by_id(db, "workload_datasets", dataset_id)


def read_attack_loads(db: Session, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lê todas as cargas de ataque."""
    return read_all_from_table(db, "attack_loads", limit)


def read_attack_load_by_id(db: Session, attack_id: int) -> Optional[Dict[str, Any]]:
    """Lê uma carga de ataque específica por ID."""
    return read_by_id(db, "attack_loads", attack_id)


def read_models(db: Session) -> List[Dict[str, Any]]:
    """Lê todos os modelos."""
    return read_all_from_table(db, "models")


def read_run_with_details(db: Session, run_id: int) -> Optional[Dict[str, Any]]:
    """
    Lê uma execução completa com todos os detalhes relacionados (joins).
    """
    query = text("""
        SELECT 
            rm.*,
            u.email as user_email,
            s.name as scenario_name,
            wd.name as workload_dataset_name,
            al.name as attack_load_name
        FROM runs_metrics rm
        LEFT JOIN users u ON rm.users_id = u.id
        LEFT JOIN scenarios s ON rm.scenarios_id = s.id
        LEFT JOIN workload_datasets wd ON rm.workload_datasets_id = wd.id
        LEFT JOIN attack_loads al ON rm.attack_loads_id = al.id
        WHERE rm.id = :run_id
    """)
    
    result = db.execute(query, {"run_id": run_id})
    row = result.fetchone()
    
    if row:
        columns = result.keys()
        return dict(zip(columns, row))
    return None


def read_recent_runs(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Lê as execuções mais recentes com informações básicas.
    """
    query = text("""
        SELECT 
            rm.id,
            rm.target_model,
            rm.attack_model,
            rm.status,
            rm.started_at,
            rm.ended_at,
            rm.metrics_asr,
            u.email as user_email,
            s.name as scenario_name
        FROM runs_metrics rm
        LEFT JOIN users u ON rm.users_id = u.id
        LEFT JOIN scenarios s ON rm.scenarios_id = s.id
        ORDER BY rm.started_at DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"limit": limit})
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


# ============================================================================
# FUNÇÕES DE ESCRITA (CREATE/INSERT)
# ============================================================================

def create_user(
    db: Session,
    email: str,
    password: str,
    role: bool = False,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um novo usuário na base de dados.
    
    Args:
        db: Sessão do banco de dados
        email: Email do usuário
        password: Senha (deve ser hash em produção)
        role: Papel do usuário (True=admin, False=user)
        created_at: Data de criação (padrão: agora)
    
    Returns:
        Dicionário com os dados do usuário criado
    """
    if created_at is None:
        created_at = datetime.now()
    
    query = text("""
        INSERT INTO users (email, password, role, created_at)
        VALUES (:email, :password, :role, :created_at)
        RETURNING id, email, role, created_at
    """)
    
    result = db.execute(query, {
        "email": email,
        "password": password,
        "role": role,
        "created_at": created_at
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def create_scenario(
    db: Session,
    name: str,
    description: str,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um novo cenário.
    
    Args:
        db: Sessão do banco de dados
        name: Nome do cenário
        description: Descrição do cenário
        created_at: Data de criação (padrão: agora)
    
    Returns:
        Dicionário com os dados do cenário criado
    """
    if created_at is None:
        created_at = datetime.now()
    
    query = text("""
        INSERT INTO scenarios (name, description, created_at)
        VALUES (:name, :description, :created_at)
        RETURNING id, name, description, created_at
    """)
    
    result = db.execute(query, {
        "name": name,
        "description": description,
        "created_at": created_at
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def create_workload_dataset(
    db: Session,
    name: str,
    description: str,
    storage_path: str,
    mime_path: str,
    scenarios_id: int,
    is_builtin: bool = False,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um novo dataset de workload.
    
    Args:
        db: Sessão do banco de dados
        name: Nome do dataset
        description: Descrição do dataset
        storage_path: Caminho de armazenamento
        mime_path: Caminho do MIME
        scenarios_id: ID do cenário associado
        is_builtin: Se é um dataset built-in
        created_at: Data de criação (padrão: agora)
    
    Returns:
        Dicionário com os dados do dataset criado
    """
    if created_at is None:
        created_at = datetime.now()
    
    query = text("""
        INSERT INTO workload_datasets 
        (name, description, storage_path, mime_path, is_builtin, created_at, scenarios_id)
        VALUES (:name, :description, :storage_path, :mime_path, :is_builtin, :created_at, :scenarios_id)
        RETURNING id, name, description, storage_path, mime_path, is_builtin, created_at, scenarios_id
    """)
    
    result = db.execute(query, {
        "name": name,
        "description": description,
        "storage_path": storage_path,
        "mime_path": mime_path,
        "is_builtin": is_builtin,
        "created_at": created_at,
        "scenarios_id": scenarios_id
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def create_attack_load(
    db: Session,
    name: str,
    description: str,
    type: str,
    storage_path: str,
    is_builtin: bool = False,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria uma nova carga de ataque.
    
    Args:
        db: Sessão do banco de dados
        name: Nome da carga de ataque
        description: Descrição
        type: Tipo de ataque
        storage_path: Caminho de armazenamento
        is_builtin: Se é built-in
        created_at: Data de criação (padrão: agora)
    
    Returns:
        Dicionário com os dados da carga de ataque criada
    """
    if created_at is None:
        created_at = datetime.now()
    
    query = text("""
        INSERT INTO attack_loads 
        (name, description, type, storage_path, is_builtin, created_at)
        VALUES (:name, :description, :type, :storage_path, :is_builtin, :created_at)
        RETURNING id, name, description, type, storage_path, is_builtin, created_at
    """)
    
    result = db.execute(query, {
        "name": name,
        "description": description,
        "type": type,
        "storage_path": storage_path,
        "is_builtin": is_builtin,
        "created_at": str(created_at)  # Note: created_at é TEXT nesta tabela
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def create_model(db: Session, name: int) -> Dict[str, Any]:
    """
    Cria um novo modelo.
    
    Args:
        db: Sessão do banco de dados
        name: Nome/ID do modelo (BIGINT conforme schema)
    
    Returns:
        Dicionário com os dados do modelo criado
    """
    query = text("""
        INSERT INTO models (name)
        VALUES (:name)
        RETURNING name
    """)
    
    result = db.execute(query, {"name": name})
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def create_run_metric(
    db: Session,
    target_model: str,
    attack_model: str,
    visibility: str,
    status: str,
    langfuse_trace_id: str,
    started_at: datetime,
    ended_at: datetime,
    metrics_orr: int,
    metrics_aor: int,
    metrics_useful_majority: bool,
    metrics_veridict_majority: bool,
    workload_datasets_id: int,
    attack_loads_id: int,
    scenarios_id: int,
    users_id: int,
    metrics_asr: Optional[int] = None
) -> Dict[str, Any]:
    """
    Cria uma nova métrica de execução.
    
    Args:
        db: Sessão do banco de dados
        target_model: Modelo alvo
        attack_model: Modelo de ataque
        visibility: Visibilidade
        status: Status da execução
        langfuse_trace_id: ID do trace no Langfuse
        started_at: Data de início
        ended_at: Data de término
        metrics_orr: Métrica ORR
        metrics_aor: Métrica AOR
        metrics_useful_majority: Maioria útil
        metrics_veridict_majority: Maioria do veredito
        workload_datasets_id: ID do dataset
        attack_loads_id: ID da carga de ataque
        scenarios_id: ID do cenário
        users_id: ID do usuário
        metrics_asr: Métrica ASR (opcional)
    
    Returns:
        Dicionário com os dados da execução criada
    """
    query = text("""
        INSERT INTO runs_metrics 
        (target_model, attack_model, visibility, status, langfuse_trace_id, 
         started_at, ended_at, metrics_asr, metrics_orr, metrics_aor, 
         metrics_useful_majority, metrics_veridict_majority, 
         workload_datasets_id, attack_loads_id, scenarios_id, users_id)
        VALUES 
        (:target_model, :attack_model, :visibility, :status, :langfuse_trace_id,
         :started_at, :ended_at, :metrics_asr, :metrics_orr, :metrics_aor,
         :metrics_useful_majority, :metrics_veridict_majority,
         :workload_datasets_id, :attack_loads_id, :scenarios_id, :users_id)
        RETURNING id, target_model, attack_model, status, started_at, ended_at
    """)
    
    result = db.execute(query, {
        "target_model": target_model,
        "attack_model": attack_model,
        "visibility": visibility,
        "status": status,
        "langfuse_trace_id": langfuse_trace_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "metrics_asr": metrics_asr,
        "metrics_orr": metrics_orr,
        "metrics_aor": metrics_aor,
        "metrics_useful_majority": metrics_useful_majority,
        "metrics_veridict_majority": metrics_veridict_majority,
        "workload_datasets_id": workload_datasets_id,
        "attack_loads_id": attack_loads_id,
        "scenarios_id": scenarios_id,
        "users_id": users_id
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def create_jury_vote(
    db: Session,
    usefulness: bool,
    model_name: str,
    runs_metrics_id: int,
    jury_index: Optional[int] = None,
    veridict: Optional[bool] = None,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um novo voto do júri.
    
    Args:
        db: Sessão do banco de dados
        usefulness: Utilidade
        model_name: Nome do modelo
        runs_metrics_id: ID da execução
        jury_index: Índice do júri (opcional, deve ser único)
        veridict: Veredito (opcional)
        created_at: Data de criação (padrão: agora)
    
    Returns:
        Dicionário com os dados do voto criado
    """
    if created_at is None:
        created_at = datetime.now()
    
    query = text("""
        INSERT INTO jury_votes 
        (jury_index, usefulness, veridict, model_name, created_at, runs_metrics_id)
        VALUES (:jury_index, :usefulness, :veridict, :model_name, :created_at, :runs_metrics_id)
        RETURNING id, jury_index, usefulness, veridict, model_name, created_at, runs_metrics_id
    """)
    
    result = db.execute(query, {
        "jury_index": jury_index,
        "usefulness": usefulness,
        "veridict": veridict,
        "model_name": model_name,
        "created_at": created_at,
        "runs_metrics_id": runs_metrics_id
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))


def bulk_create_users(db: Session, users: List[Dict[str, Any]]) -> int:
    """
    Cria múltiplos usuários de uma vez.
    
    Args:
        db: Sessão do banco de dados
        users: Lista de dicionários com dados dos usuários
               Cada dict deve ter: email, password, role (opcional), created_at (opcional)
    
    Returns:
        Número de usuários criados
    """
    created_count = 0
    
    for user_data in users:
        email = user_data.get('email')
        password = user_data.get('password')
        role = user_data.get('role', False)
        created_at = user_data.get('created_at', datetime.now())
        
        if not email or not password:
            continue
        
        query = text("""
            INSERT INTO users (email, password, role, created_at)
            VALUES (:email, :password, :role, :created_at)
        """)
        
        db.execute(query, {
            "email": email,
            "password": password,
            "role": role,
            "created_at": created_at
        })
        created_count += 1
    
    db.commit()
    return created_count


def seed_database(db: Session) -> Dict[str, int]:
    """
    Popula a base de dados com dados de exemplo para testes.
    
    Returns:
        Dicionário com contagem de registros criados por tabela
    """
    counts = {
        "users": 0,
        "scenarios": 0,
        "workload_datasets": 0,
        "attack_loads": 0
    }
    
    # Criar usuários de exemplo
    users = [
        {"email": "admin@example.com", "password": "hashed_password_1", "role": True},
        {"email": "user1@example.com", "password": "hashed_password_2", "role": False},
        {"email": "user2@example.com", "password": "hashed_password_3", "role": False},
    ]
    counts["users"] = bulk_create_users(db, users)
    
    # Criar cenários de exemplo
    scenario1 = create_scenario(
        db,
        name="Test Scenario 1",
        description="Cenário de teste para ataques de prompt injection"
    )
    scenario2 = create_scenario(
        db,
        name="Test Scenario 2",
        description="Cenário de teste para jailbreak"
    )
    counts["scenarios"] = 2
    
    # Criar workload datasets de exemplo
    dataset1 = create_workload_dataset(
        db,
        name="Sample Dataset 1",
        description="Dataset de exemplo com prompts maliciosos",
        storage_path="./datasets/sample1.json",
        mime_path="application/json",
        scenarios_id=scenario1['id'],
        is_builtin=True
    )
    counts["workload_datasets"] = 1
    
    # Criar attack loads de exemplo
    attack1 = create_attack_load(
        db,
        name="CRESCENDO Attack",
        description="Ataque gradual de escalação",
        type="crescendo",
        storage_path="./attacks/crescendo.yaml",
        is_builtin=True
    )
    attack2 = create_attack_load(
        db,
        name="MR Robot Attack",
        description="Ataque baseado em personagem",
        type="mr_robot",
        storage_path="./attacks/mr_robot.yaml",
        is_builtin=True
    )
    counts["attack_loads"] = 2
    
    return counts


def store_run(
    db: Session,
    user_id: int,
    scenario_id: int,
    target_model: str,
    attack_model: str,
    attack_type: str,
    attack_results: Dict[str, Any],
    jury_votes_data: List[Dict[str, Any]],
    started_at: datetime,
    ended_at: datetime,
    langfuse_trace_id: Optional[str] = None,
    goals_list: Optional[List[str]] = None,
    config_params: Optional[Dict[str, Any]] = None,
    results_storage_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Stores complete attack run information to the database atomically.
    Saves configuration, results, artifacts, and jury votes.
    
    All database writes are atomic: either all succeed and commit, or all fail and rollback.
    
    Args:
        db: Database session
        user_id: User who initiated the attack
        scenario_id: Scenario ID
        target_model: Target model name
        attack_model: Attack model name
        attack_type: Type of attack (crescendo, flip, mr_robot)
        attack_results: Dictionary with results data (to be saved to JSON file)
        jury_votes_data: List of jury votes with format: 
                        [{"jury_index": 0, "model_name": "model1", "usefulness": True, "veridict": True}, ...]
        started_at: Attack start time
        ended_at: Attack end time
        langfuse_trace_id: Langfuse trace ID (optional)
        goals_list: List of goals/prompts used (optional)
        config_params: Configuration parameters used (optional)
        results_storage_path: Path where JSON results are stored (optional)
    
    Returns:
        Dictionary with created run_metric id and details
    
    Raises:
        Exception: If any database operation fails (all writes rolled back)
    """
    import json
    from pathlib import Path
    
    # Begin explicit transaction
    try:
        # 1. Save results JSON to filesystem if not already saved
        if results_storage_path is None:
            results_dir = "./datasets"
            Path(results_dir).mkdir(parents=True, exist_ok=True)
            timestamp = started_at.strftime("%Y%m%d_%H%M%S")
            results_storage_path = f"{results_dir}/{attack_type}_{timestamp}.json"
            
            with open(results_storage_path, "w") as f:
                json.dump(attack_results, f, indent=2)
        
        # 2. Create attack load (contains artifacts/configuration)
        attack_load = create_attack_load(
            db,
            name=f"{attack_type}_{started_at.strftime('%Y%m%d_%H%M%S')}",
            description=f"{attack_type.upper()} attack configuration and results",
            type=attack_type,
            storage_path=results_storage_path,
            is_builtin=False,
            created_at=started_at
        )
        attack_load_id = attack_load['id']
        
        # 3. Create workload dataset (contains goals/prompts)
        workload_dataset = create_workload_dataset(
            db,
            name=f"goals_{attack_type}_{started_at.strftime('%Y%m%d_%H%M%S')}",
            description=f"Attack goals/prompts for {attack_type}",
            storage_path=results_storage_path,
            mime_path="application/json",
            scenarios_id=scenario_id,
            is_builtin=False,
            created_at=started_at
        )
        workload_dataset_id = workload_dataset['id']
        
        # 4. Calculate metrics from results
        metrics_asr = attack_results.get('metrics', {}).get('asr', 0)
        metrics_orr = attack_results.get('metrics', {}).get('orr', 0)
        metrics_aor = attack_results.get('metrics', {}).get('aor', 0)
        metrics_useful_majority = attack_results.get('metrics', {}).get('useful_majority', False)
        metrics_veridict_majority = attack_results.get('metrics', {}).get('veridict_majority', False)
        
        # 5. Determine run status
        status = "completed" if metrics_asr > 0 else "completed_no_success"
        
        # 6. Create run metric (main record with configuration + results)
        run_metric = create_run_metric(
            db,
            target_model=target_model,
            attack_model=attack_model,
            visibility="standard",
            status=status,
            langfuse_trace_id=langfuse_trace_id or f"trace_{started_at.timestamp()}",
            started_at=started_at,
            ended_at=ended_at,
            metrics_asr=metrics_asr,
            metrics_orr=metrics_orr,
            metrics_aor=metrics_aor,
            metrics_useful_majority=metrics_useful_majority,
            metrics_veridict_majority=metrics_veridict_majority,
            workload_datasets_id=workload_dataset_id,
            attack_loads_id=attack_load_id,
            scenarios_id=scenario_id,
            users_id=user_id
        )
        run_id = run_metric['id']
        
        # 7. Store jury votes
        for vote_data in jury_votes_data:
            create_jury_vote(
                db,
                usefulness=vote_data.get('usefulness', False),
                model_name=vote_data.get('model_name', 'unknown'),
                runs_metrics_id=run_id,
                jury_index=vote_data.get('jury_index'),
                veridict=vote_data.get('veridict'),
                created_at=vote_data.get('created_at', datetime.now())
            )
        
        # 8. Explicit commit of transaction
        db.commit()
        
        # 9. Return complete run information
        return {
            "run_id": run_id,
            "run_metric": run_metric,
            "attack_load_id": attack_load_id,
            "workload_dataset_id": workload_dataset_id,
            "results_path": results_storage_path,
            "status": status,
            "message": f"Run {run_id} stored successfully"
        }
        
    except Exception as e:
        # Rollback entire transaction on any error
        db.rollback()
        raise Exception(f"Error storing attack run (all DB writes rolled back): {str(e)}")

