from sqlalchemy.orm import Session
from models import Course
from .base_repository import BaseRepository

class CourseRepository(BaseRepository):
    def __init__(self):
        super().__init__(Course)

    def get_expensive_courses(self, db: Session, min_price: int):
        return db.query(Course).filter(Course.price >= min_price).all()

course_repo = CourseRepository()