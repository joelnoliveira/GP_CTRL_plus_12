from fastapi.responses import StreamingResponse
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .models import reflect_tables, Base
from .database import get_db
from .schemas import AttackRequest, AttackTemplateRequest, OverRefusalTestRequest
import io
import json
import os
from dotenv import load_dotenv
from langfuse import get_client
from urllib.parse import quote
from .routers import auth, file_upload
from orchestrator import launch_attack, launch_attack_template, launch_over_refusal_test
from sqlalchemy.orm import joinedload
from .security import get_current_user, get_current_user_or_public
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import or_
from fastapi import Query
from typing import Optional, List


# Load .env from workspace root
dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"
)
load_dotenv(dotenv_path)

AVAILABLE_EXTERNAL_TARGET_MODELS = [
    "gpt-3.5-turbo",
    "gpt-5.2-codex",
    "gpt-4o-mini-tts-2025-12-15",
    "gpt-realtime-mini-2025-12-15",
]

# Rate limiter: 900 requests per day per IP to prevent DoS
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Reflect database tables when the app starts"""
    reflect_tables()
    yield


app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_current_user_or_public)])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://10.17.0.162:3001",
        "http://10.3.2.49:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_current_user_id(db: Session, current_user_email: str) -> int:
    User = Base.classes.users
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user.id


def _model_to_dict(obj) -> dict:
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


def _get_model_class(name: str):
    try:
        return getattr(Base.classes, name)
    except Exception:
        return None


# Uses auth router
app.include_router(auth.router)
app.include_router(file_upload.router)


# liveness test, performed on container that depend on this one, do not delete!
@app.get("/status/alive")
async def check_alive():
    return {"alive": "It would seem so!"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/gdpr/export")
async def export_personal_data(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Export personal data for the authenticated user (GDPR)."""
    try:
        user_id = _get_current_user_id(db, current_user_email)

        Users = _get_model_class("users")
        RunsMetrics = _get_model_class("runs_metrics")
        JuryVotes = _get_model_class("jury_votes")
        RunsMetricsModels = _get_model_class("runs_metrics_models")
        UsersTemplateDatasets = _get_model_class("users_template_datasets")
        ScenariosUsers = _get_model_class("scenarios_users")
        ApiKeyConfigs = _get_model_class("api_key_configs")
        AuditLogs = _get_model_class("audit_logs")

        if not Users:
            raise HTTPException(status_code=500, detail="Users table not available")

        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        runs = []
        if RunsMetrics:
            runs = db.query(RunsMetrics).filter(RunsMetrics.users_id == user_id).all()
        run_ids = [run.id for run in runs]

        jury_votes = []
        runs_models = []
        if run_ids and JuryVotes:
            jury_votes = (
                db.query(JuryVotes).filter(JuryVotes.runs_metrics_id.in_(run_ids)).all()
            )
        if run_ids and RunsMetricsModels:
            runs_models = (
                db.query(RunsMetricsModels)
                .filter(RunsMetricsModels.runs_metrics_id.in_(run_ids))
                .all()
            )

        data = {
            "runs_metrics": [_model_to_dict(run) for run in runs],
            "jury_votes": [_model_to_dict(vote) for vote in jury_votes],
            "runs_metrics_models": [_model_to_dict(item) for item in runs_models],
            "users_template_datasets": [
                _model_to_dict(row)
                for row in db.query(UsersTemplateDatasets)
                .filter(UsersTemplateDatasets.users_id == user_id)
                .all()
            ]
            if UsersTemplateDatasets
            else [],
            "scenarios_users": [
                _model_to_dict(row)
                for row in db.query(ScenariosUsers)
                .filter(ScenariosUsers.users_id == user_id)
                .all()
            ]
            if ScenariosUsers
            else [],
            "api_key_configs": [
                _model_to_dict(row)
                for row in db.query(ApiKeyConfigs)
                .filter(ApiKeyConfigs.user_id == user_id)
                .all()
            ]
            if ApiKeyConfigs
            else [],
            "audit_logs": [
                _model_to_dict(row)
                for row in db.query(AuditLogs)
                .filter(AuditLogs.user_id == user_id)
                .all()
            ]
            if AuditLogs
            else [],
        }

        payload = json.dumps(data, ensure_ascii=False, default=str, indent=2).encode(
            "utf-8"
        )
        filename = f"gdpr_export_user_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        return StreamingResponse(
            io.BytesIO(payload),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados: {str(e)}")


@app.delete("/gdpr/delete")
async def delete_personal_data(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Delete personal data for the authenticated user (GDPR)."""
    try:
        user_id = _get_current_user_id(db, current_user_email)

        Users = _get_model_class("users")
        RunsMetrics = _get_model_class("runs_metrics")
        JuryVotes = _get_model_class("jury_votes")
        RunsMetricsModels = _get_model_class("runs_metrics_models")
        UsersTemplateDatasets = _get_model_class("users_template_datasets")
        ScenariosUsers = _get_model_class("scenarios_users")
        ApiKeyConfigs = _get_model_class("api_key_configs")
        AuditLogs = _get_model_class("audit_logs")

        if not Users:
            raise HTTPException(status_code=500, detail="Users table not available")

        runs = []
        if RunsMetrics:
            runs = db.query(RunsMetrics).filter(RunsMetrics.users_id == user_id).all()
        run_ids = [run.id for run in runs]

        if run_ids and JuryVotes:
            db.query(JuryVotes).filter(JuryVotes.runs_metrics_id.in_(run_ids)).delete(
                synchronize_session=False
            )
        if run_ids and RunsMetricsModels:
            db.query(RunsMetricsModels).filter(
                RunsMetricsModels.runs_metrics_id.in_(run_ids)
            ).delete(synchronize_session=False)
        if run_ids and RunsMetrics:
            db.query(RunsMetrics).filter(RunsMetrics.id.in_(run_ids)).delete(
                synchronize_session=False
            )

        if UsersTemplateDatasets:
            db.query(UsersTemplateDatasets).filter(
                UsersTemplateDatasets.users_id == user_id
            ).delete(synchronize_session=False)
        if ScenariosUsers:
            db.query(ScenariosUsers).filter(ScenariosUsers.users_id == user_id).delete(
                synchronize_session=False
            )
        if ApiKeyConfigs:
            db.query(ApiKeyConfigs).filter(ApiKeyConfigs.user_id == user_id).delete(
                synchronize_session=False
            )
        if AuditLogs:
            db.query(AuditLogs).filter(AuditLogs.user_id == user_id).delete(
                synchronize_session=False
            )
        db.query(Users).filter(Users.id == user_id).delete(synchronize_session=False)

        db.commit()

        return {"status": "success", "message": "User data deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao apagar dados: {str(e)}")


# Example endpoints using reflected ORM models

# @app.get("/users")
# async def get_users(db: Session = Depends(get_db)):
#     """Get all users from the database"""
#     User = Base.classes.users
#     users = db.query(User).all()
#     return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

# @app.get("/users/{user_id}")
# async def get_user(user_id: int, db: Session = Depends(get_db)):
#     """Get a specific user by ID"""
#     User = Base.classes.users
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         return {"error": "User not found"}
#     return {"id": user.id, "username": user.username, "email": user.email}

# @app.get("/posts")
# async def get_posts(db: Session = Depends(get_db)):
#     """Get all posts from the database"""
#     Post = Base.classes.posts
#     posts = db.query(Post).all()
#     return [{"id": p.id, "user_id": p.user_id, "title": p.title, "content": p.content} for p in posts]

# @app.get("/users/{user_id}/posts")
# async def get_user_posts(user_id: int, db: Session = Depends(get_db)):
#     """Get all posts by a specific user"""
#     Post = Base.classes.posts
#     posts = db.query(Post).filter(Post.user_id == user_id).all()
#     return [{"id": p.id, "title": p.title, "content": p.content} for p in posts]

# @app.get("/comments")
# async def get_comments(db: Session = Depends(get_db)):
#     """Get all comments from the database"""
#     Comment = Base.classes.comments
#     comments = db.query(Comment).all()
#     return [{"id": c.id, "post_id": c.post_id, "user_id": c.user_id, "comment_text": c.comment_text} for c in comments]


# ==================== API Key Configs ====================
class ApiKeyConfigRequest(BaseModel):
    name: str
    provider: str
    model_name: Optional[str] = None
    api_key: str


class ApiKeyConfigResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_name: str = None
    api_key: str = None


class CreateDatasetRequest(BaseModel):
    name: str
    description: str = None
    metadata: dict = None


# ==================== Endpoints ====================
@app.post("/datasets")
async def create_dataset(request: CreateDatasetRequest):
    langfuse = get_client()
    dataset = langfuse.create_dataset(
        name=request.name, description=request.description, metadata=request.metadata
    )
    return dataset


@app.get("/datasets")
async def get_datasets():
    langfuse = get_client()
    return langfuse.api.datasets.list()


@app.get("/datasets/{dataset_name}")
async def get_dataset(dataset_name: str):
    langfuse = get_client()
    # URL-encode the dataset name as per documentation for names with special characters
    encoded_name = quote(dataset_name, safe="")
    try:
        dataset = langfuse.get_dataset(encoded_name)
        return dataset
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Endpoints Template Datasets (BD local) ====================
@app.get("/template-datasets")
async def get_template_datasets(
    db: Session = Depends(get_db),
    is_builtin: bool = None,
):
    """
    Lista todos os template datasets da base de dados.

    Filtros opcionais:
    - is_builtin: True (só default), False (só uploaded), None (todos)
    """
    try:
        TemplateDatasets = Base.classes.template_datasets

        query = db.query(TemplateDatasets)

        # Filtrar por is_builtin se especificado
        if is_builtin is not None:
            query = query.filter(TemplateDatasets.is_builtin == is_builtin)

        # Filtrar por scenario se especificado
        datasets = query.all()

        result = []
        for ds in datasets:
            # scenario_obj = db.query(Scenarios).filter(Scenarios.id == ds.scenarios_id).first()
            result.append(
                {
                    "id": ds.id,
                    "name": ds.name,
                    "description": ds.description,
                    "storage_path": ds.storage_path,
                    "is_builtin": ds.is_builtin,
                    "created_at": ds.created_at.isoformat() if ds.created_at else None,
                }
            )

        return {"total": len(result), "datasets": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar datasets: {str(e)}"
        )


@app.get("/template-datasets/{dataset_id}")
async def get_template_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Obtém um template dataset específico por ID."""
    try:
        TemplateDatasets = Base.classes.template_datasets

        ds = (
            db.query(TemplateDatasets).filter(TemplateDatasets.id == dataset_id).first()
        )

        if not ds:
            raise HTTPException(status_code=404, detail="Dataset não encontrado")

        return {
            "id": ds.id,
            "name": ds.name,
            "description": ds.description,
            "storage_path": ds.storage_path,
            "is_builtin": ds.is_builtin,
            "created_at": ds.created_at.isoformat() if ds.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dataset: {str(e)}")


@app.get("/scenarios")
async def get_scenarios(db: Session = Depends(get_db)):
    """Lista todos os scenarios disponíveis."""
    try:
        Scenarios = Base.classes.scenarios
        scenarios = db.query(Scenarios).all()

        return [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "is_builtin": s.is_builtin,
                "storage_path": s.storage_path,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in scenarios
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar scenarios: {str(e)}"
        )


@app.post("/attack")
@limiter.limit("900/day")
async def attack(
    request: Request,
    attack_request: AttackRequest,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    try:
        Scenarios = Base.classes.scenarios
        scenario = (
            db.query(Scenarios)
            .filter(Scenarios.id == attack_request.scenario_id)
            .first()
        )
        current_user_id = _get_current_user_id(db, current_user_email)

        role_play_option = None
        if attack_request.role_play_option_id:
            RolePlayOptions = Base.classes.role_play_options
            role_play_option = (
                db.query(RolePlayOptions)
                .filter(RolePlayOptions.id == attack_request.role_play_option_id)
                .first()
            )

        if (
            attack_request.target_provider == "OPEN_AI"
            and attack_request.target_model_name not in AVAILABLE_EXTERNAL_TARGET_MODELS
        ):
            raise Exception("The target model is not supported by the external API")

        await launch_attack(
            attack_option=attack_request.attack_option.value,
            label=scenario.name,
            seed=attack_request.seed,
            temperature_judges=attack_request.temperature_judges,
            target_model_name=attack_request.target_model_name,
            attacker_model_name=attack_request.attacker_model_name,
            judge_model_name=attack_request.judge_model_name,
            jury_models=attack_request.jury_models,
            role_play_option=role_play_option if role_play_option.name else None,
            target_provider=attack_request.target_provider,
            api_key=attack_request.api_key,
            scenario_id=scenario.id,
            db=db,
            role_play_option_id=attack_request.role_play_option_id,
            user_id=current_user_id,
        )

        # Audit log
        AuditLog = Base.classes.audit_logs
        request_data = attack_request.model_dump()
        request_data.pop("api_key", None)  # Remove sensitive data
        audit_entry = AuditLog(
            user_id=current_user_id,
            endpoint="/attack",
            request_body=json.dumps(request_data, default=str),
            created_at=datetime.now(),
        )
        db.add(audit_entry)
        db.commit()

        return {"status": "success", "message": "Attack completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/attack-template")
@limiter.limit("900/day")
async def attack_template(
    request: Request,
    attack_template_request: AttackTemplateRequest,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    try:
        current_user_id = _get_current_user_id(db, current_user_email)
        Scenarios = Base.classes.scenarios
        scenario = (
            db.query(Scenarios)
            .filter(Scenarios.id == attack_template_request.scenario_id)
            .first()
        )

        TemplateDatasets = Base.classes.template_datasets
        template_dataset = (
            db.query(TemplateDatasets)
            .filter(TemplateDatasets.id == attack_template_request.template_dataset_id)
            .first()
        )

        await launch_attack_template(
            label=scenario.name,
            seed=attack_template_request.seed,
            temperature_judges=attack_template_request.temperature_judges,
            temperature_attacker=attack_template_request.temperature_attacker,
            temperature_target=attack_template_request.temperature_target,
            target_model_name=attack_template_request.target_model_name,
            jury_models=attack_template_request.jury_models,
            template_path=template_dataset.storage_path,
            target_provider=attack_template_request.target_provider,
            api_key=attack_template_request.api_key,
            db=db,
            template_dataset_id=template_dataset.id,
            scenario_id=scenario.id,
            user_id=current_user_id,
            # langfuse,
            # user
        )

        # Audit log
        AuditLog = Base.classes.audit_logs
        request_data = attack_template_request.model_dump()
        request_data.pop("api_key", None)  # Remove sensitive data
        audit_entry = AuditLog(
            user_id=current_user_id,
            endpoint="/attack-template",
            request_body=json.dumps(request_data, default=str),
            created_at=datetime.now(),
        )
        db.add(audit_entry)
        db.commit()

        return {"status": "success", "message": "Attack template completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/over-refusal-test")
@limiter.limit("900/day")
async def over_refusal_test(
    request: Request,
    over_refusal_request: OverRefusalTestRequest,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    try:
        current_user_id = _get_current_user_id(db, current_user_email)
        if (
            over_refusal_request.target_provider == "OPEN_AI"
            and over_refusal_request.target_model_name
            not in AVAILABLE_EXTERNAL_TARGET_MODELS
        ):
            raise Exception("The target model is not supported by the external API")

        await launch_over_refusal_test(
            seed=over_refusal_request.seed,
            temperature_judges=over_refusal_request.temperature_judges,
            temperature_attacker=over_refusal_request.temperature_attacker,
            temperature_target=over_refusal_request.temperature_target,
            target_model_name=over_refusal_request.target_model_name,
            jury_models=over_refusal_request.jury_models,
            target_provider=over_refusal_request.target_provider,
            api_key=over_refusal_request.api_key,
            db=db,
            user_id=current_user_id,
        )
        return {"status": "success", "message": "Over-refusal test completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api-key-configs")
async def create_api_key_config(
    request: ApiKeyConfigRequest,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Create a new API key configuration for the current user."""
    try:
        current_user_id = _get_current_user_id(db, current_user_email)

        ApiKeyConfigs = Base.classes.api_key_configs

        # Create the API key config with user_id directly
        api_config = ApiKeyConfigs(
            name=request.name,
            provider=request.provider,
            model_name=request.model_name,
            api_key=request.api_key,
            user_id=current_user_id,
        )
        db.add(api_config)
        db.commit()

        return {
            "id": api_config.id,
            "name": api_config.name,
            "provider": api_config.provider,
            "model_name": api_config.model_name,
            "message": "API key config created successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar config: {str(e)}")


@app.get("/api-key-configs/me")
async def get_user_api_key_configs(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Get all API key configurations for the current user."""
    try:
        user_id = _get_current_user_id(db, current_user_email)

        ApiKeyConfigs = Base.classes.api_key_configs

        # Query all api_key_configs for this user directly
        api_configs = (
            db.query(ApiKeyConfigs).filter(ApiKeyConfigs.user_id == user_id).all()
        )

        configs = [
            {
                "id": config.id,
                "name": config.name,
                "provider": config.provider,
                "model_name": config.model_name,
                "api_key_masked": f"***{config.api_key[-4:]}"
                if config.api_key
                else None,
            }
            for config in api_configs
        ]

        return {"user_id": user_id, "total": len(configs), "configs": configs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar configs: {str(e)}")


@app.get("/api-key-configs/{config_id}")
async def get_api_key_config_by_id(
    config_id: int,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Get a specific API key configuration by ID (must belong to user)."""
    try:
        user_id = _get_current_user_id(db, current_user_email)

        ApiKeyConfigs = Base.classes.api_key_configs

        # Query config directly with user_id filter
        api_config = (
            db.query(ApiKeyConfigs)
            .filter(ApiKeyConfigs.id == config_id, ApiKeyConfigs.user_id == user_id)
            .first()
        )

        if not api_config:
            raise HTTPException(
                status_code=404, detail="API key config not found for this user"
            )

        return {
            "id": api_config.id,
            "name": api_config.name,
            "provider": api_config.provider,
            "model_name": api_config.model_name,
            "api_key_masked": f"***{api_config.api_key[-4:]}"
            if api_config.api_key
            else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter config: {str(e)}")


@app.put("/api-key-configs/{config_id}")
async def update_api_key_config(
    config_id: int,
    request: ApiKeyConfigRequest,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Update an API key configuration (must belong to user)."""
    try:
        user_id = _get_current_user_id(db, current_user_email)

        ApiKeyConfigs = Base.classes.api_key_configs

        # Query config directly with user_id filter
        api_config = (
            db.query(ApiKeyConfigs)
            .filter(ApiKeyConfigs.id == config_id, ApiKeyConfigs.user_id == user_id)
            .first()
        )

        if not api_config:
            raise HTTPException(
                status_code=404, detail="API key config not found for this user"
            )

        # Update fields
        api_config.name = request.name
        api_config.provider = request.provider
        api_config.model_name = request.model_name
        api_config.api_key = request.api_key

        db.commit()

        return {
            "id": api_config.id,
            "name": api_config.name,
            "provider": api_config.provider,
            "model_name": api_config.model_name,
            "message": "API key config updated successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar config: {str(e)}"
        )


@app.delete("/api-key-configs/{config_id}")
async def delete_api_key_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    """Delete an API key configuration (must belong to user)."""
    try:
        user_id = _get_current_user_id(db, current_user_email)

        ApiKeyConfigs = Base.classes.api_key_configs

        # Query config directly with user_id filter
        api_config = (
            db.query(ApiKeyConfigs)
            .filter(ApiKeyConfigs.id == config_id, ApiKeyConfigs.user_id == user_id)
            .first()
        )

        if not api_config:
            raise HTTPException(
                status_code=404, detail="API key config not found for this user"
            )

        db.delete(api_config)
        db.commit()

        return {
            "message": "API key config deleted successfully",
            "deleted_id": config_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar config: {str(e)}")


@app.get("/runs-metrics/me")
async def get_my_runs_metrics(
    attack_type: Optional[List[str]] = Query(None),
    attack_model: Optional[List[str]] = Query(None),
    target_model: Optional[List[str]] = Query(None),
    scenario: Optional[List[str]] = Query(None),
    template: Optional[List[str]] = Query(None),
    metric: Optional[List[str]] = Query(None),
    role_play: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user),
):
    user_id = _get_current_user_id(db, current_user_email)

    RunsMetrics = Base.classes.runs_metrics
    Scenarios = Base.classes.scenarios
    Templates = Base.classes.template_datasets
    RolePlays = Base.classes.role_play_options

    query = (
        db.query(RunsMetrics)
        .options(
            joinedload(RunsMetrics.scenarios),
            joinedload(RunsMetrics.template_datasets),
            joinedload(RunsMetrics.users),
            joinedload(RunsMetrics.role_play_options),
        )
        .filter(RunsMetrics.users_id == user_id)  # 👈 only MY runs
    )

    # Helper to normalize scenario names
    def normalize_name_list(names: List[str]) -> List[str]:
        return [name.strip().lower().replace(" ", "_") for name in names]

    # ---------- Basic filters ----------
    if attack_type:
        query = query.filter(RunsMetrics.attack_type.in_(attack_type))

    if attack_model:
        query = query.filter(RunsMetrics.attack_model.in_(attack_model))

    if target_model:
        query = query.filter(RunsMetrics.target_model.in_(target_model))

    # ---------- Scenario filter ----------
    if scenario:
        normalized = normalize_name_list(scenario)
        has_custom = "custom" in normalized
        selected = [s for s in normalized if s != "custom"]

        query = query.join(RunsMetrics.scenarios)

        conditions = []
        if selected:
            conditions.append(Scenarios.name.in_(selected))
        if has_custom:
            conditions.append(Scenarios.is_builtin.is_(False))

        query = query.filter(or_(*conditions))

    # ---------- Template filter ----------
    if template:
        has_custom = "custom" in template
        selected = [t for t in template if t != "custom"]

        query = query.join(RunsMetrics.template_datasets)

        conditions = []
        if selected:
            conditions.append(Templates.description.in_(selected))
        if has_custom:
            conditions.append(Templates.is_builtin.is_(False))

        query = query.filter(or_(*conditions))

    # ---------- Role play filter ----------
    if role_play:
        has_custom = "custom" in role_play
        selected = [r for r in role_play if r != "custom"]

        query = query.join(RunsMetrics.role_play_options)

        conditions = []
        if selected:
            conditions.append(RolePlays.description.in_(selected))
        if has_custom:
            conditions.append(RolePlays.is_builtin.is_(False))

        query = query.filter(or_(*conditions))

    # ---------- Metric filter (HAS VALUE, INCLUDING 0) ----------
    if metric:
        metric_column_map = {
            "AOR": RunsMetrics.metrics_aor,
            "ORR": RunsMetrics.metrics_orr,
            "ASR": RunsMetrics.metrics_asr,
            "Static Metric": RunsMetrics.static_metric,  # frontend sends "SM"
        }

        metric_filters = []
        for m in metric:
            col = metric_column_map.get(m)
            if col is not None:
                metric_filters.append(col.isnot(None))

        if metric_filters:
            query = query.filter(or_(*metric_filters))

    return query.all()


@app.get("/runs-metrics")
async def get_all_runs_metrics(db: Session = Depends(get_db)):
    RunsMetrics = Base.classes.runs_metrics
    return (
        db.query(RunsMetrics)
        .options(
            joinedload(RunsMetrics.scenarios),
            joinedload(RunsMetrics.template_datasets),
            joinedload(RunsMetrics.users),
            joinedload(RunsMetrics.role_play_options),
        )
        .all()
    )


@app.get("/runs-metrics/{run_id}")
async def get_runs_metrics(
    run_id: int,
    db: Session = Depends(get_db),
):
    RunsMetrics = Base.classes.runs_metrics

    run_metrics = (
        db.query(RunsMetrics)
        .options(
            joinedload(RunsMetrics.scenarios),
            joinedload(RunsMetrics.template_datasets),
            joinedload(RunsMetrics.users),
            joinedload(RunsMetrics.role_play_options),
            joinedload(RunsMetrics.role_play_options),
        )
        .filter(RunsMetrics.id == run_id)
        .one_or_none()
    )

    return run_metrics


@app.get("/role-play-options")
async def get_all_role_play_options(db: Session = Depends(get_db)):
    RolePlayOptions = Base.classes.role_play_options
    return db.query(RolePlayOptions).all()
