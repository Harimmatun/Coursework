from database import engine, Base, get_db
from models import User, Course, UserRole, Enrollment, Submission, Assignment
import services
from sqlalchemy import func

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_extra_data(db):
    new_student = services.create_user(db, "Anna Smith", "anna@test.com", UserRole.STUDENT)
    course = db.query(Course).first()
    
    if course:
        services.enroll_student(db, new_student.id, course.id)
        
        assignment = db.query(Assignment).filter_by(course_id=course.id).first()
        if assignment:
            sub = services.submit_homework(db, assignment.id, new_student.id, "Anna's work")
            services.grade_submission(db, sub.id, 98)

def main():
    init_db()
    db = next(get_db())

    try:
        seed_extra_data(db)
        print("--- Extra data seeded ---")
    except Exception:
        db.rollback()
        print("--- Data already exists, skipping seed ---")

    print("\n=== 1. SIMPLE QUERY: Expensive Courses ===")
    courses = services.get_courses_by_price_range(db, 1000, 2000)
    for c in courses:
        print(f"Course: {c.title} | Price: {c.price}")

    print("\n=== 2. ANALYTICS: Student Performance (AVG Score) ===")
    stats = services.get_student_average_scores(db)
    for name, avg_score, count in stats:
        print(f"Student: {name} | Average: {avg_score:.1f} | Works: {count}")

    print("\n=== 3. ANALYTICS: Instructor Revenue ===")
    revenue = services.get_instructor_revenue(db)
    for name, sales, total in revenue:
        print(f"Instructor: {name} | Sales: {sales} | Revenue: {total}")

if __name__ == "__main__":
    main()