
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_TOKEN = "test-secret-token-for-employee-api"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_employee_endpoint_without_token_returns_401():
    response = client.get("/api/v1/employees/")

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or missing authentication token."
    )


def test_employee_endpoint_with_invalid_token_returns_401():
    response = client.get(
        "/api/v1/employees/",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or missing authentication token."
    )


def test_employee_endpoint_with_valid_token_is_allowed():
    response = client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
    )

    assert response.status_code == 200


def test_department_endpoint_without_token_returns_401():
    response = client.get("/api/v1/departments/")

    assert response.status_code == 401


def test_department_endpoint_with_invalid_token_returns_401():
    response = client.get(
        "/api/v1/departments/",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401


def test_database_is_test_database():
    from app.db.session import engine

    assert engine.url.database == "employee_management_test_db"
