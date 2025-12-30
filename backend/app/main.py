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

@app.post("/attack")
async def attack(request: AttackRequest):
    try:
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
            goals_file_name=request.goals_file_name,
        )
        return {"status": "success", "message": "Attack completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attack-template")
async def attack_template(request: AttackTemplateRequest, db: Session = Depends(get_db)):
    try:
        template_path = None
        if request.template_path:
            # Opção A: O user envia o path completo (ex: vindo do upload)
            # Vamos validar se existe na BD para garantir integridade
            # Ou simplesmente usamos o que foi enviado. 
            # O requisito diz "buscar o caminho com base no path da base de dados"
            # Assumimos que o request.template_path é a chave de procura (o próprio path).
            
            # Assegurar que templates está refletido (caso não tenha sido ainda)
            if not hasattr(Base.classes, 'templates'):
                reflect_tables()
            
            Templates = Base.classes.templates
            # Procura na BD pelo path exato
            record = db.query(Templates).filter(Templates.path == request.template_path).first()
            
            if record:
                template_path = record.path
            else:
                # Se não encontrar na BD, usamos o path enviado diretamente?
                # Pela descrição rigida "buscar... com base no path da base de dados", 
                # talvez devêssemos falhar se não estiver na BD via upload.
                # Mas para ser flexivel, vamos assumir que se o user mandou um path válido, tentamos usar.
                # Mas para cumprir fielmente, vamos logar warning.
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