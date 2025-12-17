import services
from models import UserRole, Course, User, Assignment, Submission

def test_create_course_flow(db_session):
    instructor = services.create_user(
        db_session, 
        "Test Teacher", 
        "teacher@test.com", 
        UserRole.INSTRUCTOR
    )

    modules = ["Mod 1", "Mod 2", "Mod 3"]
    course = services.create_course_with_modules(
        db_session,
        instructor.id,
        "Pytest Course",
        2000,
        modules
    )

    assert course.id is not None
    assert course.title == "Pytest Course"
    
    saved_course = db_session.query(Course).filter_by(id=course.id).first()
    assert saved_course is not None
    assert len(saved_course.modules) == 3
    assert saved_course.modules[0].title == "Mod 1"

def test_enrollment_logic(db_session):
    student = services.create_user(db_session, "Student T", "s@t.com", UserRole.STUDENT)
    instructor = services.create_user(db_session, "Teach T", "t@t.com", UserRole.INSTRUCTOR)
    
    course = services.create_course_with_modules(db_session, instructor.id, "Course A", 100, ["M1"])

    enrollment = services.enroll_student(db_session, student.id, course.id)

    assert enrollment is not None
    assert enrollment.user_id == student.id
    assert enrollment.course_id == course.id

    user_in_db = db_session.query(User).filter_by(id=student.id).first()
    assert len(user_in_db.enrollments) == 1
    assert user_in_db.enrollments[0].course.title == "Course A"

def test_grade_validation_error(db_session):
    student = services.create_user(db_session, "Bad Student", "bad@test.com", UserRole.STUDENT)
    instructor = services.create_user(db_session, "Strict Teacher", "strict@test.com", UserRole.INSTRUCTOR)
    course = services.create_course_with_modules(db_session, instructor.id, "Math", 100, ["M1"])
    
    assignment = services.create_assignment(db_session, course.id, "Test", 100)
    submission = services.submit_homework(db_session, assignment.id, student.id, "Work")

    result = services.grade_submission(db_session, submission.id, 200)
    
    assert result is None
    
    saved_submission = db_session.get(Submission, submission.id)
    assert saved_submission.score is None