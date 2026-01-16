from fastapi import FastAPI, Depends, HTTPException
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Reflect database tables when the app starts"""
    reflect_tables()
    yield

app = FastAPI(lifespan=lifespan)

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

class CreateDatasetRequest(BaseModel):
    name: str
    description: str = None
    metadata: dict = None

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

# ==================== Endpoints Workload Datasets (BD local) ====================
@app.get("/workload-datasets")
async def get_workload_datasets(
    db: Session = Depends(get_db),
    is_builtin: bool = None,
    scenario: str = None
):
    """
    Lista todos os workload datasets da base de dados.
    
    Filtros opcionais:
    - is_builtin: True (só default), False (só uploaded), None (todos)
    - scenario: Nome do scenario para filtrar
    """
    try:
        WorkloadDatasets = Base.classes.workload_datasets
        Scenarios = Base.classes.scenarios
        
        query = db.query(WorkloadDatasets)
        
        # Filtrar por is_builtin se especificado
        if is_builtin is not None:
            query = query.filter(WorkloadDatasets.is_builtin == is_builtin)
        
        # Filtrar por scenario se especificado
        if scenario:
            scenario_obj = db.query(Scenarios).filter(Scenarios.name == scenario).first()
            if scenario_obj:
                query = query.filter(WorkloadDatasets.scenarios_id == scenario_obj.id)
        
        datasets = query.all()
        
        result = []
        for ds in datasets:
            scenario_obj = db.query(Scenarios).filter(Scenarios.id == ds.scenarios_id).first()
            result.append({
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "storage_path": ds.storage_path,
                "mime_path": ds.mime_path,
                "is_builtin": ds.is_builtin,
                "created_at": ds.created_at.isoformat() if ds.created_at else None,
                "scenario": scenario_obj.name if scenario_obj else None
            })
        
        return {
            "total": len(result),
            "datasets": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar datasets: {str(e)}")

@app.get("/workload-datasets/{dataset_id}")
async def get_workload_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Obtém um workload dataset específico por ID."""
    try:
        WorkloadDatasets = Base.classes.workload_datasets
        Scenarios = Base.classes.scenarios
        
        ds = db.query(WorkloadDatasets).filter(WorkloadDatasets.id == dataset_id).first()
        
        if not ds:
            raise HTTPException(status_code=404, detail="Dataset não encontrado")
        
        scenario = db.query(Scenarios).filter(Scenarios.id == ds.scenarios_id).first()
        
        return {
            "id": ds.id,
            "name": ds.name,
            "description": ds.description,
            "storage_path": ds.storage_path,
            "mime_path": ds.mime_path,
            "is_builtin": ds.is_builtin,
            "created_at": ds.created_at.isoformat() if ds.created_at else None,
            "scenario": scenario.name if scenario else None
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
        # Se goals_file_name for fornecido, verificar se existe na BD
        goals_path = None
        if request.goals_file_name:
            WorkloadDatasets = Base.classes.workload_datasets
            # Tentar encontrar pelo storage_path (se o user passou o path completo)
            record = db.query(WorkloadDatasets).filter(
                WorkloadDatasets.storage_path == request.goals_file_name
            ).first()
            
            if record:
                goals_path = record.storage_path
            else:
                # Tentar encontrar pelo nome
                record = db.query(WorkloadDatasets).filter(
                    WorkloadDatasets.name == request.goals_file_name
                ).first()
                if record:
                    goals_path = record.storage_path
                else:
                    # Fallback: usar como nome de ficheiro (compatibilidade)
                    goals_path = request.goals_file_name
        
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
            goals_file_name=goals_path,
        )
        return {"status": "success", "message": "Attack completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attack-template")
async def attack_template(request: AttackTemplateRequest, db: Session = Depends(get_db)):
    try:
        template_path = None
        if request.template_path:
            # Procurar o dataset na tabela workload_datasets
            if not hasattr(Base.classes, 'workload_datasets'):
                reflect_tables()
            
            WorkloadDatasets = Base.classes.workload_datasets
            # Procura na BD pelo storage_path
            record = db.query(WorkloadDatasets).filter(
                WorkloadDatasets.storage_path == request.template_path
            ).first()
            
            if record:
                template_path = record.storage_path
            else:
                # Se não encontrar na BD, usa o path enviado diretamente
                template_path = request.template_path

        await launch_attack_template(
            label=request.label.value,
            seed=request.seed,
            temperature_judges=request.temperature_judges,
            temperature_attacker=request.temperature_attacker,
            temperature_target=request.temperature_target,
            target_model_name=request.target_model_name,
            jury_models=request.jury_models,
            template_path=template_path
        )
        return {"status": "success", "message": "Attack template completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/over-refusal-test")
async def over_refusal_test(request: OverRefusalTestRequest):
    try:
        await launch_over_refusal_test(
            seed=request.seed,
            temperature_judges=request.temperature_judges,
            target_model_name=request.target_model_name,
            jury_models=request.jury_models,
        )
        return {"status": "success", "message": "Over-refusal test completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))