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

#change to post later to handle the options that we pass on the funciton
@app.get("/attack")
async def attack():
    try:
        await launch_attack(attack_option=constants.TypesOfAttacks.MR_ROBOT_ATTACK.value, label=constants.Goals.VULNERABLE_GOALS.value)
    except Exception as e:
        error = str(e)
        error += str(os.listdir("/"))
        raise HTTPException(status_code=404, detail=str(e))

#change to post later to handle the options that we pass on the funciton
@app.get("/attack-template")
async def attack_template():
    try:
        await launch_attack_template(attack_option=constants.TypesOfAttacks.CRESCENDO_ATTACK.value, label=constants.Goals.MALICIOUS_GOALS.value)
    except Exception as e:
        error = str(e)
        error += str(os.listdir("/"))
        raise HTTPException(status_code=404, detail=str(e))
    
#change to post later to handle the options that we pass on the funciton
@app.get("/over-refusal-test")
async def over_refusal_test():
    try:
        await launch_over_refusal_test()
    except Exception as e:
        error = str(e)
        error += str(os.listdir("/"))
        raise HTTPException(status_code=404, detail=str(e))