from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


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
    metrics_veridict_majority: bool,
    template_datasets_id: int,
    #attack_loads_id: int,
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
        metrics_veridict_majority: Maioria do veredito
        template_datasets_id: ID do dataset
        scenarios_id: ID do cenário
        users_id: ID do usuário
        metrics_asr: Métrica ASR (opcional)
    
    Returns:
        Dicionário com os dados da execução criada
    """
    query = text("""
        INSERT INTO runs_metrics 
        (target_model, attack_model, visibility, status, langfuse_trace_id, 
         started_at, ended_at, metrics_asr, metrics_orr, metrics_aor, metrics_veridict_majority, 
         template_datasets_id, scenarios_id, users_id)
        VALUES 
        (:target_model, :attack_model, :visibility, :status, :langfuse_trace_id,
         :started_at, :ended_at, :metrics_asr, :metrics_orr, :metrics_aor, :metrics_veridict_majority,
         :template_datasets_id, :scenarios_id, :users_id)
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
        "metrics_veridict_majority": metrics_veridict_majority,
        "template_datasets_id": template_datasets_id,
        "scenarios_id": scenarios_id,
        "users_id": users_id
    })
    db.commit()
    
    row = result.fetchone()
    columns = result.keys()
    return dict(zip(columns, row))

def store_run(
    db: Session,
    user_id: int,
    scenario_id: int,
    template_datasets_id: int,
    target_model: str,
    attack_model: str,
    attack_results: Dict[str, Any],
    started_at: datetime,
    ended_at: datetime,
    langfuse_trace_id: Optional[str] = None,
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
        started_at: Attack start time
        ended_at: Attack end time
        langfuse_trace_id: Langfuse trace ID (optional)
        attacker_visibility: Visibility of the attack (standard, white_box, black_box)
    
    Returns:
        Dictionary with created run_metric id and details
    
    Raises:
        Exception: If any database operation fails (all writes rolled back)
    """
    print(attack_results)
    import json
    from pathlib import Path
    
    # Begin explicit transaction
    try:
        # 1. Ensure metrics are floats
        def _ensure_float(val):
            if isinstance(val, bool):
                return True if val else False
            try:
                return float(val)
            except (ValueError, TypeError):
                return False

        metrics_asr = _ensure_float(attack_results.get('metrics', {}).get('ASR', 0))
        metrics_orr = _ensure_float(attack_results.get('metrics', {}).get('ORR', 0))
        metrics_aor = _ensure_float(attack_results.get('metrics', {}).get('AOR', 0))
        #metrics_useful_majority = _ensure_float(attack_results.get('metrics', {}).get('useful_majority', False))
        metrics_veridict_majority = _ensure_float(attack_results.get('metrics', {}).get('decision', False))
        
        if metrics_asr > 0 or metrics_orr > 0:
            status = "completed"
        else:
            status = "completed_no_success"
        
        # 2. Create run metric (main record with configuration + results)
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
            metrics_veridict_majority=metrics_veridict_majority,
            template_datasets_id=template_datasets_id,
            #attack_loads_id=attack_load_id,
            scenarios_id=scenario_id,
            users_id=user_id
        )
        run_id = run_metric['id']
        
        # 3. Explicit commit of transaction
        db.commit()
        
        # 4. Return complete run information
        return {
            "run_id": run_id,
            "run_metric": run_metric,
            #"attack_load_id": attack_load_id,
            "template_datasets_id": template_datasets_id,
            "status": status,
            "message": f"Run {run_id} stored successfully"
        }
        
    except Exception as e:
        # Rollback entire transaction on any error
        db.rollback()
        raise Exception(f"Error storing attack run (all DB writes rolled back): {str(e)}")

