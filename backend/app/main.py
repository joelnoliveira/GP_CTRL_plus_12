from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .models import reflect_tables, Base
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from langfuse import get_client
from urllib.parse import quote
from .routers import auth
from orchestrator import launch_attack, constants, launch_attack_template, launch_over_refusal_test

from fastapi.middleware.cors import CORSMiddleware

# Load .env from workspace root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Reflect database tables when the app starts"""
    reflect_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],  # <-- THIS enables OPTIONS
    allow_headers=["*"],
)

#Uses auth router
app.include_router(auth.router)

# liveness test, performed on container that depend on this one, do not delete!
@app.get("/status/alive")
async def check_alive():
    return {"alive": "It would seem so!"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/history/mock_filters")
def get_mock_history_filters():
    return [
        {
            "key": "attack_type",
            "placeholder": "Attack Type",
            "items": ["FGSM", "PGD", "CW"]
        },
        {
            "key": "attack_model",
            "placeholder": "Attack Model",
            "items": ["ResNet50", "ConvNeXt", "EfficientNet-B3", "MobileNetV3", "ResNet18"]
        },
        {
            "key": "target_model",
            "placeholder": "Target Model",
            "items": ["EfficientNet-B0", "ViT-B16", "ResNet101", "DenseNet121", "EfficientNet-B1"]
        },
        {
            "key": "jury_model",
            "placeholder": "Jury Model",
            "items": ["EfficientNet-B0", "ViT-B16", "ResNet101", "DenseNet121", "EfficientNet-B1"]
        },
        {
            "key": "workload",
            "placeholder": "Workload",
            "items": ["Workload A", "Workload B", "Workload C"]
        },
        {
            "key": "scenario",
            "placeholder": "Scenario",
            "items": ["Scenario A", "Scenario B", "Scenario C"]
        },
        {
            "key": "status",
            "placeholder": "Status",
            "items": ["Ongoing", "Loading", "Finished"]
        }
    ]

from fastapi import Query
from typing import Optional, List

@app.get("/history/mock_runs")
def get_mock_history_runs(
    attack_type: Optional[str] = Query(None),
    attack_model: Optional[str] = Query(None),
    target_model: Optional[str] = Query(None),
    jury_model: Optional[str] = Query(None),
    workload: Optional[str] = Query(None),
    scenario: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    runs = [
        {
            "run_name_id": "RUN-001",
            "username": "joao.carvalho",
            "attack_type": "FGSM",
            "date": "2025-01-10",
            "status": "Finished",
            "attack_model": "ResNet50",
            "target_model": "EfficientNet-B0",
            "isPublicValue": False,
        },
        {
            "run_name_id": "RUN-002",
            "username": "joao.carvalho",
            "attack_type": "PGD",
            "date": "2025-01-12",
            "status": "Ongoing",
            "attack_model": "ConvNeXt",
            "target_model": "ViT-B16",
            "isPublicValue": True,
        },
        {
            "run_name_id": "RUN-003",
            "username": "maria.silva",
            "attack_type": "CW",
            "date": "2025-01-15",
            "status": "Loading",
            "attack_model": "EfficientNet-B3",
            "target_model": "ResNet101",
            "isPublicValue": True,
        },
        {
            "run_name_id": "RUN-004",
            "username": "pedro.oliveira",
            "attack_type": "FGSM",
            "date": "2025-01-18",
            "status": "Finished",
            "attack_model": "MobileNetV3",
            "target_model": "DenseNet121",
            "isPublicValue": True,
        },
        {
            "run_name_id": "RUN-005",
            "username": "ana.rodrigues",
            "attack_type": "PGD",
            "date": "2025-01-20",
            "status": "Finished",
            "attack_model": "ResNet18",
            "target_model": "EfficientNet-B1",
            "isPublicValue": True,
        },
    ]

    def matches(run):
        return (
            (attack_type is None or run["attack_type"] == attack_type) and
            (attack_model is None or run["attack_model"] == attack_model) and
            (target_model is None or run["target_model"] == target_model) and
            (jury_model is None or run["jury_model"] == jury_model) and
            (workload is None or run["workload"] == workload) and
            (scenario is None or run["scenario"] == scenario) and
            (status is None or run["status"] == status) 
        )

    return [run for run in runs if matches(run)]

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

#change to post later to handle the options that we pass on the funciton
@app.get("/attack")
async def attack():
    try:
        await launch_attack(attack_option=constants.TypesOfAttacks.MR_ROBOT_ATTACK.value, label=constants.Goals.VULNERABLE_GOALS.value)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

#change to post later to handle the options that we pass on the funciton
@app.get("/attack-template")
async def attack_template():
    try:
        await launch_attack_template(attack_option=constants.TypesOfAttacks.CRESCENDO_ATTACK.value, label=constants.Goals.MALICIOUS_GOALS.value)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
#change to post later to handle the options that we pass on the funciton
@app.get("/over-refusal-test")
async def over_refusal_test():
    try:
        await launch_over_refusal_test()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))