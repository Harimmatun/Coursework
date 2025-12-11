from sqlalchemy.orm import Session
from models import User
from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

user_repo = UserRepository()