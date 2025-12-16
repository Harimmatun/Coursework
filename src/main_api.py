from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import os

from database import get_db
import services
import schemas
from models import UserRole

app = FastAPI(title="LMS API System")

templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    courses = services.get_courses_by_price_range(db, 0, 100000)
    return templates.TemplateResponse("index.html", {"request": request, "courses": courses})

@app.get("/courses/", response_model=List[schemas.CourseResponse])
def get_courses(min_price: int = 0, max_price: int = 100000, db: Session = Depends(get_db)):
    return services.get_courses_by_price_range(db, min_price, max_price)

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = services.user_repo.get_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        role_enum = UserRole(user.role)
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid role. Use: student, instructor, admin")

    return services.create_user(db, user.full_name, user.email, role_enum)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = services.user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user