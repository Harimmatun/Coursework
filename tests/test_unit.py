import pytest
from pydantic import ValidationError
from src.utils import calculate_letter_grade, format_full_name
from src.schemas import UserCreate

def test_calculate_letter_grade_valid():
    assert calculate_letter_grade(95) == "A"
    assert calculate_letter_grade(85) == "B"
    assert calculate_letter_grade(75) == "C"
    assert calculate_letter_grade(65) == "D"
    assert calculate_letter_grade(50) == "F"
    assert calculate_letter_grade(0) == "F"
    assert calculate_letter_grade(100) == "A"

def test_calculate_letter_grade_invalid():
    with pytest.raises(ValueError):
        calculate_letter_grade(-1)
    
    with pytest.raises(ValueError):
        calculate_letter_grade(101)

def test_format_full_name():
    assert format_full_name("john", "doe") == "John Doe"
    assert format_full_name("  ALICE ", "smith  ") == "Alice Smith"

def test_user_create_schema_validation():
    user = UserCreate(email="test@example.com", full_name="Test User", role="student")
    assert user.email == "test@example.com"
    assert user.role == "student"

def test_user_create_schema_missing_field():
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", role="student")

def test_user_create_schema_invalid_types():
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", full_name=12345)