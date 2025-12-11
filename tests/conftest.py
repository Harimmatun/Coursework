import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from database import Base, SQLALCHEMY_DATABASE_URL
from models import User, Course, Enrollment

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    
    Base.metadata.drop_all(bind=engine)