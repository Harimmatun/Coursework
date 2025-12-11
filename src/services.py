from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from models import User, Course, Module, UserRole, Enrollment, Assignment, Submission
from repositories.user_repository import user_repo
from repositories.course_repository import course_repo

def create_user(db: Session, full_name: str, email: str, role: UserRole):
    return user_repo.create(db, {
        "full_name": full_name,
        "email": email,
        "role": role
    })

def create_course_with_modules(db: Session, instructor_id: int, title: str, price: int, module_titles: list[str]):
    try:
        new_course = Course(title=title, price=price, instructor_id=instructor_id)
        db.add(new_course)
        db.flush() 

        for index, mod_title in enumerate(module_titles, start=1):
            new_module = Module(
                title=mod_title,
                course_id=new_course.id,
                order_index=index,
                content=f"Content for {mod_title}"
            )
            db.add(new_module)

        db.commit()
        print(f"Course '{title}' created successfully.")
        return new_course

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error creating course: {e}")
        return None

def enroll_student(db: Session, student_id: int, course_id: int):
    try:
        enrollment = Enrollment(user_id=student_id, course_id=course_id)
        db.add(enrollment)
        db.commit()
        print(f"Student {student_id} enrolled in course {course_id}")
        return enrollment
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error enrolling student: {e}")

def create_assignment(db: Session, course_id: int, title: str, max_score: int):
    assignment = Assignment(course_id=course_id, title=title, max_score=max_score)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

def submit_homework(db: Session, assignment_id: int, student_id: int, content: str):
    submission = Submission(assignment_id=assignment_id, student_id=student_id, content=content)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

def grade_submission(db: Session, submission_id: int, score: int):
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            print(f"Submission {submission_id} not found.")
            return None

        assignment = submission.assignment
        if score < 0 or score > assignment.max_score:
            print(f"Error: Score {score} is invalid. Max allowed: {assignment.max_score}")
            return None

        submission.score = score
        db.commit()
        print(f"Submission {submission_id} graded. Score: {score}/{assignment.max_score}")
        return submission

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error grading submission: {e}")
        return None

def soft_delete_user(db: Session, user_id: int):
    try:
        user = user_repo.get_by_id(db, user_id)
        if not user:
            print(f"User {user_id} not found.")
            return False
        
        user.is_active = False
        db.commit()
        print(f"User {user_id} deactivated.")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deactivating user: {e}")
        return False

def hard_delete_module(db: Session, module_id: int):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            return False
        db.delete(module)
        db.commit()
        print(f"Module {module_id} deleted.")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        return False

def get_courses_by_price_range(db: Session, min_price: int, max_price: int):
    return course_repo.get_expensive_courses(db, min_price)

def get_student_average_scores(db: Session):
    return db.query(
        User.full_name,
        func.avg(Submission.score).label("average_score"),
        func.count(Submission.id).label("submissions_count")
    ).join(Submission, User.id == Submission.student_id)\
     .group_by(User.id)\
     .having(func.count(Submission.id) > 0)\
     .order_by(desc("average_score"))\
     .all()

def get_instructor_revenue(db: Session):
    return db.query(
        User.full_name,
        func.count(Enrollment.id).label("total_sales"),
        func.sum(Course.price).label("total_revenue")
    ).join(Course, User.id == Course.instructor_id)\
     .join(Enrollment, Course.id == Enrollment.course_id)\
     .group_by(User.id)\
     .all()