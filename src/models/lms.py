import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class EnrollmentStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

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