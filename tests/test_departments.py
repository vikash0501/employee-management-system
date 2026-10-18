
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


def test_update_department_name_preserves_description(client):
    original_description = "Keep this department description"
    department_name = f"Dept-{uuid4().hex[:8]}"

    create_response = client.post(
        "/api/v1/departments/",
        json={
            "name": department_name,
            "description": original_description,
        },
    )
    assert create_response.status_code == 201

    department_id = create_response.json()["id"]
    updated_name = f"Updated-{uuid4().hex[:8]}"

    update_response = client.put(
        f"/api/v1/departments/{department_id}",
        json={"name": updated_name},
    )

    assert update_response.status_code == 200
    updated_department = update_response.json()
    assert updated_department["name"] == updated_name
    assert updated_department["description"] == original_description


def test_delete_department_with_employees_returns_409(client):
    department_payload = {
        "name": f"Dept-{uuid4().hex[:8]}",
        "description": "Department with an employee",
    }

    department_response = client.post(
        "/api/v1/departments/",
        json=department_payload,
    )
    assert department_response.status_code == 201

    department_id = department_response.json()["id"]

    employee_payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "email": f"{uuid4().hex[:8]}@example.com",
        "phone": "9876543210",
        "designation": "Engineer",
        "department_id": department_id,
        "date_of_joining": "2026-01-15",
        "employment_status": "ACTIVE",
    }

    employee_response = client.post(
        "/api/v1/employees/",
        json=employee_payload,
    )
    assert employee_response.status_code == 201

    delete_response = client.delete(
        f"/api/v1/departments/{department_id}"
    )

    assert delete_response.status_code == 409
    assert delete_response.json()["detail"] == (
        "Cannot delete a department that has employees."
    )
