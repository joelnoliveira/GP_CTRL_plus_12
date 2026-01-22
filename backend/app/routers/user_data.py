"""
User Data Management Router (GDPR Compliance)
Provides endpoints for users to export and delete their personal data.
NFR-4: Conformidade - O sistema deve permitir aos utilizadores exportar e eliminar os seus dados pessoais.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Base
from ..security import get_current_user

router = APIRouter(
    prefix="/user-data",
    tags=["user-data"],
)


def get_user_by_email(db: Session, email: str):
    """Helper function to get user by email"""
    if not hasattr(Base.classes, 'users'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database tables not reflected yet"
        )
    User = Base.classes.users
    return db.query(User).filter(User.email == email).first()


@router.get("/export", summary="Export Personal Data", 
            description="Export all personal data associated with the authenticated user (GDPR Article 20 - Data Portability)")
def export_user_data(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all personal data for the authenticated user.
    
    This endpoint complies with GDPR Article 20 (Right to Data Portability).
    Returns all user data in a structured JSON format that can be downloaded.
    """
    user = get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Collect user's personal data from specified tables:
    # users, api_key_configs, runs_metrics, users_attack_loads, users_workload_datasets, scenarios_users
    user_data = {
        "export_metadata": {
            "export_date": datetime.now().isoformat(),
            "export_version": "1.0",
            "user_email": user.email
        },
        "users": {
            "id": user.id,
            "email": user.email,
            "role": "admin" if user.role else "user",
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        "api_key_configs": [],
        "runs_metrics": [],
        "users_attack_loads": [],
        "users_workload_datasets": [],
        "scenarios_users": []
    }
    
    # Get user's API key configurations (mask sensitive data)
    if hasattr(Base.classes, 'api_key_configs'):
        ApiKeyConfig = Base.classes.api_key_configs
        api_configs = db.query(ApiKeyConfig).filter(ApiKeyConfig.user_id == user.id).all()
        user_data["api_key_configs"] = [
            {
                "id": config.id,
                "name": config.name,
                "provider": config.provider,
                "model_name": config.model_name,
                "api_key_masked": f"***{config.api_key[-4:]}" if config.api_key and len(config.api_key) > 4 else "***"
            }
            for config in api_configs
        ]
    
    # Get user's runs_metrics
    if hasattr(Base.classes, 'runs_metrics'):
        RunsMetrics = Base.classes.runs_metrics
        runs = db.query(RunsMetrics).filter(RunsMetrics.users_id == user.id).all()
        user_data["runs_metrics"] = [
            {
                "id": run.id,
                "target_model": run.target_model,
                "attack_model": run.attack_model,
                "visibility": run.visibility,
                "status": run.status.strip() if run.status else None,
                "langfuse_trace_id": run.langfuse_trace_id,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "ended_at": run.ended_at.isoformat() if run.ended_at else None,
                "metrics_asr": run.metrics_asr,
                "metrics_orr": run.metrics_orr,
                "metrics_aor": run.metrics_aor,
                "metrics_useful_majority": run.metrics_useful_majority,
                "metrics_veridict_majority": run.metrics_veridict_majority,
                "workload_datasets_id": run.workload_datasets_id,
                "attack_loads_id": run.attack_loads_id,
                "scenarios_id": run.scenarios_id,
                "users_id": run.users_id
            }
            for run in runs
        ]
    
    # Get user's users_attack_loads associations
    if hasattr(Base.classes, 'users_attack_loads'):
        UsersAttackLoads = Base.classes.users_attack_loads
        user_attack_loads = db.query(UsersAttackLoads).filter(UsersAttackLoads.users_id == user.id).all()
        user_data["users_attack_loads"] = [
            {
                "users_id": ual.users_id,
                "attack_loads_id": ual.attack_loads_id
            }
            for ual in user_attack_loads
        ]
    
    # Get user's users_workload_datasets associations
    if hasattr(Base.classes, 'users_workload_datasets'):
        UsersWorkloadDatasets = Base.classes.users_workload_datasets
        user_workload_datasets = db.query(UsersWorkloadDatasets).filter(UsersWorkloadDatasets.users_id == user.id).all()
        user_data["users_workload_datasets"] = [
            {
                "users_id": uwd.users_id,
                "workload_datasets_id": uwd.workload_datasets_id
            }
            for uwd in user_workload_datasets
        ]
    
    # Get user's scenarios_users associations
    if hasattr(Base.classes, 'scenarios_users'):
        ScenariosUsers = Base.classes.scenarios_users
        user_scenarios = db.query(ScenariosUsers).filter(ScenariosUsers.users_id == user.id).all()
        user_data["scenarios_users"] = [
            {
                "scenarios_id": su.scenarios_id,
                "users_id": su.users_id
            }
            for su in user_scenarios
        ]
    
    # Return with headers that support download
    return JSONResponse(
        content=user_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_export_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@router.delete("/delete", summary="Delete Personal Data",
               description="Delete all personal data associated with the authenticated user (GDPR Article 17 - Right to Erasure)")
def delete_user_data(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all personal data for the authenticated user.
    
    This endpoint complies with GDPR Article 17 (Right to Erasure / Right to be Forgotten).
    Permanently deletes all user data from the system.
    
    WARNING: This action is irreversible!
    """
    user = get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_id = user.id
    deleted_items = {
        "runs_metrics": 0,
        "users_attack_loads": 0,
        "users_workload_datasets": 0,
        "scenarios_users": 0,
        "api_key_configs": 0,
        "users": False
    }
    
    try:
        # 1. Delete from runs_metrics (has FK to users)
        if hasattr(Base.classes, 'runs_metrics'):
            RunsMetrics = Base.classes.runs_metrics
            deleted_items["runs_metrics"] = db.query(RunsMetrics).filter(
                RunsMetrics.users_id == user_id
            ).delete(synchronize_session=False)
        
        # 2. Delete from users_attack_loads (has FK to users)
        if hasattr(Base.classes, 'users_attack_loads'):
            UsersAttackLoads = Base.classes.users_attack_loads
            deleted_items["users_attack_loads"] = db.query(UsersAttackLoads).filter(
                UsersAttackLoads.users_id == user_id
            ).delete(synchronize_session=False)
        
        # 3. Delete from users_workload_datasets (has FK to users)
        if hasattr(Base.classes, 'users_workload_datasets'):
            UsersWorkloadDatasets = Base.classes.users_workload_datasets
            deleted_items["users_workload_datasets"] = db.query(UsersWorkloadDatasets).filter(
                UsersWorkloadDatasets.users_id == user_id
            ).delete(synchronize_session=False)
        
        # 4. Delete from scenarios_users (has FK to users)
        if hasattr(Base.classes, 'scenarios_users'):
            ScenariosUsers = Base.classes.scenarios_users
            deleted_items["scenarios_users"] = db.query(ScenariosUsers).filter(
                ScenariosUsers.users_id == user_id
            ).delete(synchronize_session=False)
        
        # 5. Delete from api_key_configs (has FK to users)
        if hasattr(Base.classes, 'api_key_configs'):
            ApiKeyConfig = Base.classes.api_key_configs
            deleted_items["api_key_configs"] = db.query(ApiKeyConfig).filter(
                ApiKeyConfig.user_id == user_id
            ).delete(synchronize_session=False)
        
        # 6. Finally, delete from users table
        User = Base.classes.users
        db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
        deleted_items["users"] = True
        
        db.commit()
        
        return {
            "message": "All personal data has been successfully deleted",
            "status": "success",
            "deleted_at": datetime.now().isoformat(),
            "summary": deleted_items
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user data: {str(e)}"
        )


@router.get("/summary", summary="Get Data Summary",
            description="Get a summary of all personal data stored for the authenticated user")
def get_user_data_summary(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of all personal data stored for the authenticated user.
    
    This helps users understand what data is being stored about them
    before deciding to export or delete their data.
    """
    user = get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    summary = {
        "user_id": user.id,
        "email": user.email,
        "account_created": user.created_at.isoformat() if user.created_at else None,
        "data_counts": {
            "users": 1,
            "api_key_configs": 0,
            "runs_metrics": 0,
            "users_attack_loads": 0,
            "users_workload_datasets": 0,
            "scenarios_users": 0
        }
    }
    
    # Count api_key_configs
    if hasattr(Base.classes, 'api_key_configs'):
        ApiKeyConfig = Base.classes.api_key_configs
        summary["data_counts"]["api_key_configs"] = db.query(ApiKeyConfig).filter(
            ApiKeyConfig.user_id == user.id
        ).count()
    
    # Count runs_metrics
    if hasattr(Base.classes, 'runs_metrics'):
        RunsMetrics = Base.classes.runs_metrics
        summary["data_counts"]["runs_metrics"] = db.query(RunsMetrics).filter(
            RunsMetrics.users_id == user.id
        ).count()
    
    # Count users_attack_loads
    if hasattr(Base.classes, 'users_attack_loads'):
        UsersAttackLoads = Base.classes.users_attack_loads
        summary["data_counts"]["users_attack_loads"] = db.query(UsersAttackLoads).filter(
            UsersAttackLoads.users_id == user.id
        ).count()
    
    # Count users_workload_datasets
    if hasattr(Base.classes, 'users_workload_datasets'):
        UsersWorkloadDatasets = Base.classes.users_workload_datasets
        summary["data_counts"]["users_workload_datasets"] = db.query(UsersWorkloadDatasets).filter(
            UsersWorkloadDatasets.users_id == user.id
        ).count()
    
    # Count scenarios_users
    if hasattr(Base.classes, 'scenarios_users'):
        ScenariosUsers = Base.classes.scenarios_users
        summary["data_counts"]["scenarios_users"] = db.query(ScenariosUsers).filter(
            ScenariosUsers.users_id == user.id
        ).count()
    
    return summary
