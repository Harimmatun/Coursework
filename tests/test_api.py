import pytest
from fastapi.testclient import TestClient
from src.main_api import app
from src.database import get_db

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

def test_read_root_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Available Courses" in response.text

def test_create_user_api(client):
    user_data = {
        "email": "api_test@example.com",
        "full_name": "API Tester",
        "role": "student"
    }
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "api_test@example.com"
    assert "id" in data

def test_create_duplicate_user(client):
    user_data = {
        "email": "duplicate@example.com",
        "full_name": "First User",
        "role": "student"
    }
    client.post("/users/", json=user_data)
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_get_courses_list(client):
    response = client.get("/courses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_non_existent_user(client):
    response = client.get("/users/99999")
    assert response.status_code == 404