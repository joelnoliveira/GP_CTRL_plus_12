from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .models import reflect_tables, Base
from .database import get_db
from .schemas import AttackRequest, AttackTemplateRequest, OverRefusalTestRequest
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from langfuse import get_client
from urllib.parse import quote
from .routers import auth, file_upload
from orchestrator import launch_attack, constants, launch_attack_template, launch_over_refusal_test


# Load .env from workspace root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path)

AVAILABLE_EXTERNAL_TARGET_MODELS = ["gpt-3.5-turbo", "gpt-5.2-codex", "gpt-4o-mini-tts-2025-12-15", "gpt-realtime-mini-2025-12-15"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Reflect database tables when the app starts"""
    reflect_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

#Uses auth router
app.include_router(auth.router)
app.include_router(file_upload.router)

# liveness test, performed on container that depend on this one, do not delete!
@app.get("/status/alive")
async def check_alive():
    return {"alive": "It would seem so!"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

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
    provider: str = "OPEN_AI"
    model_name: str = None
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
    dataset = langfuse.create_dataset(name=request.name, description=request.description, metadata=request.metadata)
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
            #scenario_obj = db.query(Scenarios).filter(Scenarios.id == ds.scenarios_id).first()
            result.append({
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "storage_path": ds.storage_path,
                "mime_path": ds.mime_path,
                "is_builtin": ds.is_builtin,
                "created_at": ds.created_at.isoformat() if ds.created_at else None,
            })
        
        return {
            "total": len(result),
            "datasets": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar datasets: {str(e)}")

@app.get("/template-datasets/{dataset_id}")
async def get_template_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Obtém um template dataset específico por ID."""
    try:
        TemplateDatasets = Base.classes.template_datasets
        
        ds = db.query(TemplateDatasets).filter(TemplateDatasets.id == dataset_id).first()
        
        if not ds:
            raise HTTPException(status_code=404, detail="Dataset não encontrado")
        
        return {
            "id": ds.id,
            "name": ds.name,
            "description": ds.description,
            "storage_path": ds.storage_path,
            "mime_path": ds.mime_path,
            "is_builtin": ds.is_builtin,
            "created_at": ds.created_at.isoformat() if ds.created_at else None
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
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in scenarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar scenarios: {str(e)}")

@app.post("/attack")
async def attack(request: AttackRequest, db: Session = Depends(get_db)):
    try:
        Scenario = Base.classes.scenarios
        scenario_id = (db.query(Scenario).filter(Scenario.name == request.label.value).first()).id
        goals_file_name = request.goals_file_name if request.goals_file_name is not None else f"{request.label.value}.json"

        if request.target_provider == "OPEN_AI" and request.target_model_name not in AVAILABLE_EXTERNAL_TARGET_MODELS:
            raise Exception("The target model is not supported by the external API")
        
        await launch_attack(
            attack_option=request.attack_option.value,
            label=request.label.value,
            seed=request.seed,
            temperature_judges=request.temperature_judges,
            target_model_name=request.target_model_name,
            attacker_model_name=request.attacker_model_name,
            judge_model_name=request.judge_model_name,
            jury_models=request.jury_models,
            role_play_option=request.role_play_option.value if request.role_play_option else None,
            goals_file_name=goals_file_name,
            target_provider=request.target_provider,
            api_key=request.api_key,
            scenario_id=scenario_id,
            db=db,
        )
        return {"status": "success", "message": "Attack completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attack-template")
async def attack_template(request: AttackTemplateRequest, db: Session = Depends(get_db)):
    try:
        template_path = None
        if request.template_path:
            # Procurar o dataset na tabela template_datasets
            if not hasattr(Base.classes, 'template_datasets'):
                reflect_tables()
            
            TemplateDatasets = Base.classes.template_datasets
            # Procura na BD pelo storage_path
            record = db.query(TemplateDatasets).filter(
                TemplateDatasets.storage_path == request.template_path
            ).first()
            
            if record:
                template_path = record.storage_path
            else:
                # Se não encontrar na BD, usa o path enviado diretamente
                template_path = request.template_path
        
        if request.target_provider == "OPEN_AI" and request.target_model_name not in AVAILABLE_EXTERNAL_TARGET_MODELS:
            raise Exception("The target model is not supported by the external API")
        
        Scenario = Base.classes.scenarios
        scenario_id = (db.query(Scenario).filter(Scenario.name == request.label.value).first()).id

        TemplateDatasets = Base.classes.template_datasets
        template_dataset_id = (db.query(TemplateDatasets).filter(TemplateDatasets.storage_path == template_path).first()).id
        

        print("Template Dataset ID:", template_dataset_id)
        await launch_attack_template(
            label=request.label.value,
            seed=request.seed,
            temperature_judges=request.temperature_judges,
            temperature_attacker=request.temperature_attacker,
            temperature_target=request.temperature_target,
            target_model_name=request.target_model_name,
            jury_models=request.jury_models,
            template_path=template_path,
            target_provider=request.target_provider,
            api_key=request.api_key,
            db=db,
            template_dataset_id=template_dataset_id,
            scenario_id=scenario_id,            
            #langfuse,
            #user
        )
        return {"status": "success", "message": "Attack template completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/over-refusal-test")
async def over_refusal_test(request: OverRefusalTestRequest):
    try:
        if request.target_provider == "OPEN_AI" and request.target_model_name not in AVAILABLE_EXTERNAL_TARGET_MODELS:
            raise Exception("The target model is not supported by the external API")
        
        await launch_over_refusal_test(
            seed=request.seed,
            temperature_judges=request.temperature_judges,
            temperature_attacker=request.temperature_attacker,
            temperature_target=request.temperature_target,
            target_model_name=request.target_model_name,
            jury_models=request.jury_models,
            target_provider=request.target_provider,
            api_key=request.api_key
        )
        return {"status": "success", "message": "Over-refusal test completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api-key-configs")
async def create_api_key_config(
    request: ApiKeyConfigRequest,
    db: Session = Depends(get_db),
    # current_user_email: str = Depends(get_current_user),  # TODO: Uncomment for JWT auth
):
    """Create a new API key configuration for the current user."""
    try:
        # TODO: Uncomment for JWT auth
        # User = Base.classes.users
        # user = db.query(User).filter(User.email == current_user_email).first()
        # if not user:
        #     raise HTTPException(status_code=401, detail="User not found")
        # current_user_id = user.id

        current_user_id = 1  # Hardcoded for testing - remove when enabling JWT auth

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


@app.get("/api-key-configs/{user_id}")
async def get_user_api_key_configs(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user_email: str = Depends(get_current_user),  # TODO: Uncomment for JWT auth
):
    """Get all API key configurations for a specific user."""
    try:
        # TODO: Uncomment for JWT auth
        # User = Base.classes.users
        # user = db.query(User).filter(User.email == current_user_email).first()
        # if not user or user.id != user_id:
        #     raise HTTPException(status_code=403, detail="Access denied")

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


@app.get("/api-key-configs/{user_id}/{config_id}")
async def get_api_key_config_by_id(
    user_id: int,
    config_id: int,
    db: Session = Depends(get_db),
    # current_user_email: str = Depends(get_current_user),  # TODO: Uncomment for JWT auth
):
    """Get a specific API key configuration by ID (must belong to user)."""
    try:
        # TODO: Uncomment for JWT auth
        # User = Base.classes.users
        # user = db.query(User).filter(User.email == current_user_email).first()
        # if not user or user.id != user_id:
        #     raise HTTPException(status_code=403, detail="Access denied")

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


@app.put("/api-key-configs/{user_id}/{config_id}")
async def update_api_key_config(
    user_id: int,
    config_id: int,
    request: ApiKeyConfigRequest,
    db: Session = Depends(get_db),
    # current_user_email: str = Depends(get_current_user),  # TODO: Uncomment for JWT auth
):
    """Update an API key configuration (must belong to user)."""
    try:
        # TODO: Uncomment for JWT auth
        # User = Base.classes.users
        # user = db.query(User).filter(User.email == current_user_email).first()
        # if not user or user.id != user_id:
        #     raise HTTPException(status_code=403, detail="Access denied")

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


@app.delete("/api-key-configs/{user_id}/{config_id}")
async def delete_api_key_config(
    user_id: int,
    config_id: int,
    db: Session = Depends(get_db),
    # current_user_email: str = Depends(get_current_user),  # TODO: Uncomment for JWT auth
):
    """Delete an API key configuration (must belong to user)."""
    try:
        # TODO: Uncomment for JWT auth
        # User = Base.classes.users
        # user = db.query(User).filter(User.email == current_user_email).first()
        # if not user or user.id != user_id:
        #     raise HTTPException(status_code=403, detail="Access denied")

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
