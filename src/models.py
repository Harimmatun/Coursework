from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class UserRole(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class EnrollmentStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True) 

    enrollments = relationship("Enrollment", back_populates="student")
    courses_created = relationship("Course", back_populates="instructor")
    submissions = relationship("Submission", back_populates="student")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Integer, default=0)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    instructor = relationship("User", back_populates="courses_created")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class Enrollment(Base):
    """Таблиця зв'язку: Який студент записаний на Який курс"""
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(150))
    content = Column(Text)
    order_index = Column(Integer)

    course = relationship("Course", back_populates="modules")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(150))
    max_score = Column(Integer, default=100)
    due_date = Column(DateTime(timezone=True), nullable=True)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text) 
    score = Column(Integer, nullable=True) 
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('score >= 0', name='check_score_positive'),
    )

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")