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

load_dotenv()

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

@app.get("/datasets")
async def get_datasets():
    """List available datasets in Langfuse"""
    LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
    LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
    LANGFUSE_HOST = os.getenv('LANGFUSE_HOST', "http://langfuse-web:3000")

    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        return {"error": "Langfuse credentials not configured"}

    url = f"{LANGFUSE_HOST}/api/public/datasets"
    auth = HTTPBasicAuth(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    
    try:
        response = requests.get(url, auth=auth, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # The response can be a direct list or an object with 'data'
            items = data.get('data', data) if isinstance(data, dict) else data
            
            return [
                {"name": ds.get('name'), "items_count": len(ds.get('items', []))}
                for ds in items
            ]
        else:
            return {"error": f"Error fetching datasets: {response.status_code} - {response.text}"}

    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

class DatasetCreate(BaseModel):
    name: str
    description: str | None = None
    metadata: dict | None = None

@app.post("/datasets")
async def create_dataset(dataset: DatasetCreate):
    """Create a new dataset in Langfuse"""
    LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
    LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
    LANGFUSE_HOST = os.getenv('LANGFUSE_HOST', "http://langfuse-web:3000")

    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Langfuse credentials not configured")

    url = f"{LANGFUSE_HOST}/api/public/datasets"
    auth = HTTPBasicAuth(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    
    payload = {
        "name": dataset.name,
        "description": dataset.description,
        "metadata": dataset.metadata
    }
    
    try:
        response = requests.post(url, json=payload, auth=auth, timeout=5)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error creating dataset: {response.text}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


