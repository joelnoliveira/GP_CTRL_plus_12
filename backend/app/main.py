from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .database import get_db
from .models import reflect_tables, Base

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

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users from the database"""
    User = Base.classes.users
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    User = Base.classes.users
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return {"id": user.id, "username": user.username, "email": user.email}

@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    """Get all posts from the database"""
    Post = Base.classes.posts
    posts = db.query(Post).all()
    return [{"id": p.id, "user_id": p.user_id, "title": p.title, "content": p.content} for p in posts]

@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    """Get all posts by a specific user"""
    Post = Base.classes.posts
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return [{"id": p.id, "title": p.title, "content": p.content} for p in posts]

@app.get("/comments")
async def get_comments(db: Session = Depends(get_db)):
    """Get all comments from the database"""
    Comment = Base.classes.comments
    comments = db.query(Comment).all()
    return [{"id": c.id, "post_id": c.post_id, "user_id": c.user_id, "comment_text": c.comment_text} for c in comments]