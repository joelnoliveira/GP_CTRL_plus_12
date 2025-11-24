from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .database import get_db
from .models import reflect_tables, Base
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from langfuse import get_client
from urllib.parse import quote

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Reflect database tables when the app starts"""
    reflect_tables()
    yield

app = FastAPI(lifespan=lifespan)

class DatasetRequest(BaseModel):
    name: str
    description: str = None
    metadata: dict = None

@app.post("/dataset")
async def create_dataset(dataset: DatasetRequest):
    langfuse = get_client()
    langfuse.create_dataset(name=dataset.name, description=dataset.description, metadata=dataset.metadata)
    return {"message": "Dataset created successfully", "name": dataset.name}

@app.get("/dataset/{dataset_name}")
async def get_dataset(dataset_name: str):
    host = os.getenv("LANGFUSE_HOST")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not host or not public_key or not secret_key:
         raise HTTPException(status_code=500, detail="Langfuse configuration missing")

    # Encode the dataset name to handle special characters like slashes
    encoded_name = quote(dataset_name, safe="")
    url = f"{host}/api/public/datasets/{encoded_name}"
    
    try:
        response = requests.get(url, auth=(public_key, secret_key))
        if response.status_code == 404:
             raise HTTPException(status_code=404, detail="Dataset not found")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets():
    host = os.getenv("LANGFUSE_HOST")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not host or not public_key or not secret_key:
         raise HTTPException(status_code=500, detail="Langfuse configuration missing")

    url = f"{host}/api/public/datasets"
    try:
        response = requests.get(url, auth=(public_key, secret_key))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

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

