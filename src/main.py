from database import engine, Base, get_db
from models import UserRole, User, Course
import services

def main():
    db = next(get_db())
    print("--- DATA CHECK ---")

    instructor = services.user_repo.get_by_email(db, "ivan@teach.com")
    if not instructor:
        instructor = services.create_user(db, "Ivan Petrov", "ivan@teach.com", UserRole.INSTRUCTOR)
        print(f"Created Instructor: {instructor.full_name}")
    
    course = db.query(Course).filter_by(instructor_id=instructor.id).first()
    if not course:
        course = services.create_course_with_modules(
            db,
            instructor.id,
            "Enterprise Python Architecture",
            1500,
            ["Module 1: Intro", "Module 2: Patterns", "Module 3: Docker"]
        )

    student = services.user_repo.get_by_email(db, "oleg@student.com")
    if not student:
        student = services.create_user(db, "Oleg Student", "oleg@student.com", UserRole.STUDENT)
        print(f"Created Student: {student.full_name}")

    if not student.enrollments:
        services.enroll_student(db, student.id, course.id)
        
        assignment = services.create_assignment(db, course.id, "Final Project", 100)
        sub = services.submit_homework(db, assignment.id, student.id, "My code")
        services.grade_submission(db, sub.id, 95)
        print("Student graded with 95 points.")

    print("\n=== 1. SIMPLE QUERY: Expensive Courses (1000-2000) ===")
    courses = services.get_courses_by_price_range(db, 1000, 2000)
    for c in courses:
        print(f"Course: {c.title} | Price: {c.price}")

    print("\n=== 2. ANALYTICS: Student Performance ===")
    stats = services.get_student_average_scores(db)
    for name, avg, count in stats:
        print(f"Student: {name} | Average: {avg:.1f} | Works: {count}")

    print("\n=== 3. ANALYTICS: Instructor Revenue ===")
    revenue = services.get_instructor_revenue(db)
    for name, sales, total in revenue:
        print(f"Instructor: {name} | Sales: {sales} | Revenue: {total}")

if __name__ == "__main__":
    main()