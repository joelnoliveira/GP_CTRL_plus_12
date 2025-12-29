from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def create_workload_dataset(
    db: Session,
    name: str,
    description: str,
    storage_path: str,
    mime_path: str,
    scenarios_id: int,
    is_builtin: bool = False,
    created_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Cria um novo dataset de workload."""
    if created_at is None:
        created_at = datetime.now()

    query = text(
        """
        INSERT INTO workload_datasets
        (name, description, storage_path, mime_path, is_builtin, created_at, scenarios_id)
        VALUES (:name, :description, :storage_path, :mime_path, :is_builtin, :created_at, :scenarios_id)
        RETURNING id, name, description, storage_path, mime_path, is_builtin, created_at, scenarios_id
        """
    )

    result = db.execute(
        query,
        {
            "name": name,
            "description": description,
            "storage_path": storage_path,
            "mime_path": mime_path,
            "is_builtin": is_builtin,
            "created_at": created_at,
            "scenarios_id": scenarios_id,
        },
    )
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
    results_storage_path: Optional[str] = None,
    attacker_visibility: str = "standard"
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
        attacker_visibility: Visibility of the attack (standard, white_box, black_box)
    
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
        def _ensure_float(val):
            if isinstance(val, bool):
                return 1.0 if val else 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        metrics_asr = _ensure_float(attack_results.get('metrics', {}).get('ASR', 0))
        metrics_orr = _ensure_float(attack_results.get('metrics', {}).get('ORR', 0))
        metrics_aor = _ensure_float(attack_results.get('metrics', {}).get('AOR', 0))
        metrics_useful_majority = _ensure_float(attack_results.get('metrics', {}).get('useful_majority', False))
        metrics_veridict_majority = _ensure_float(attack_results.get('metrics', {}).get('veridict_majority', False))
        
        if metrics_asr > 0 or metrics_orr > 0:
            status = "completed"
        else:
            status = "completed_no_success"
        
        # 6. Create run metric (main record with configuration + results)
        run_metric = create_run_metric(
            db,
            target_model=target_model,
            attack_model=attack_model,
            visibility=attacker_visibility,
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

