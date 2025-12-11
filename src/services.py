from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import User, Course, Module, UserRole, Enrollment
from models import Assignment, Submission
from sqlalchemy import func, desc

def create_user(db: Session, full_name: str, email: str, role: UserRole):
    """Створює простого користувача (студента або вчителя)"""
    user = User(full_name=full_name, email=email, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_course_with_modules(db: Session, instructor_id: int, title: str, price: int, module_titles: list[str]):

    try:
        new_course = Course(
            title=title,
            price=price,
            instructor_id=instructor_id
        )
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
        print(f"✅ Курс '{title}' успішно створено з {len(module_titles)} модулями.")
        return new_course

    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Помилка при створенні курсу! Відкат змін. Деталі: {e}")
        return None

def enroll_student(db: Session, student_id: int, course_id: int):
    try:
        enrollment = Enrollment(
            user_id=student_id,
            course_id=course_id
        )
        db.add(enrollment)
        db.commit()
        print(f"✅ Студент {student_id} записаний на курс {course_id}")
        return enrollment
    except SQLAlchemyError as e:
        db.rollback()   
        print(f"❌ Помилка запису на курс: {e}")

def create_assignment(db: Session, course_id: int, title: str, max_score: int):
    assignment = Assignment(course_id=course_id, title=title, max_score=max_score)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

def submit_homework(db: Session, assignment_id: int, student_id: int, content: str):
    submission = Submission(
        assignment_id=assignment_id, 
        student_id=student_id, 
        content=content
    )
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
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User {user_id} not found.")
            return False
        
        user.is_active = False
        db.commit()
        print(f"User {user_id} deactivated (Soft Delete).")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deactivating user: {e}")
        return False

def hard_delete_module(db: Session, module_id: int):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            print(f"Module {module_id} not found.")
            return False
            
        db.delete(module)
        db.commit()
        print(f"Module {module_id} permanently deleted (Hard Delete).")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deleting module: {e}")
        return False
def get_courses_by_price_range(db: Session, min_price: int, max_price: int):
    return db.query(Course).filter(
        Course.price >= min_price,
        Course.price <= max_price
    ).order_by(Course.price.desc()).all()

def get_student_average_scores(db: Session):
    results = db.query(
        User.full_name,
        func.avg(Submission.score).label("average_score"),
        func.count(Submission.id).label("submissions_count")
    ).join(Submission, User.id == Submission.student_id)\
     .group_by(User.id)\
     .having(func.count(Submission.id) > 0)\
     .order_by(desc("average_score"))\
     .all()
    
    return results

def get_instructor_revenue(db: Session):
    results = db.query(
        User.full_name,
        func.count(Enrollment.id).label("total_sales"),
        func.sum(Course.price).label("total_revenue")
    ).join(Course, User.id == Course.instructor_id)\
     .join(Enrollment, Course.id == Enrollment.course_id)\
     .group_by(User.id)\
     .all()
     
    return results