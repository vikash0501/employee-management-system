
from uuid import uuid4


def test_create_department(client):
    department_name = f"QA-{uuid4().hex[:8]}"
    payload = {
        "name": department_name,
        "description": "Department created by automated test",
    }

    response = client.post(
        "/api/v1/departments/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == department_name
    assert data["description"] == payload["description"]
    assert "id" in data


def test_list_departments(client):
    department_name = f"Test-Department-{uuid4().hex[:8]}"

    create_response = client.post(
        "/api/v1/departments/",
        json={
            "name": department_name,
            "description": "Department for list endpoint test",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/api/v1/departments/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        department["name"] == department_name
        for department in response.json()
    )


def test_create_duplicate_department_returns_409(client):
    payload = {
        "name": f"Duplicate-{uuid4().hex[:8]}",
        "description": "Duplicate department test",
    }

    first_response = client.post(
        "/api/v1/departments/",
        json=payload,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/departments/",
        json=payload,
    )
    assert second_response.status_code == 409


def test_get_nonexistent_department_returns_404(client):
    response = client.get("/api/v1/departments/999999999")

    assert response.status_code == 404
