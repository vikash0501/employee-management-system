
from uuid import uuid4


def test_create_employee(client):
    # Create a department first.
    department_name = f"Engineering-{uuid4().hex[:8]}"

    department_response = client.post(
        "/api/v1/departments/",
        json={
            "name": department_name,
            "description": "Department for employee tests",
        },
    )

    assert department_response.status_code == 201
    department_id = department_response.json()["id"]

    # Create an employee in that department.
    email = f"employee-{uuid4().hex[:8]}@example.com"

    employee_response = client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Test",
            "last_name": "Employee",
            "email": email,
            "designation": "Python Developer",
            "department_id": department_id,
            "date_of_joining": "2025-01-15",
        },
    )

    assert employee_response.status_code == 201

    data = employee_response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Employee"
    assert data["email"] == email
    assert data["department_id"] == department_id
    assert "id" in data


def test_list_employees(client):
    # Create a department first.
    department_response = client.post(
        "/api/v1/departments/",
        json={
            "name": f"QA-{uuid4().hex[:8]}",
            "description": "Department for employee list test",
        },
    )

    assert department_response.status_code == 201
    department_id = department_response.json()["id"]

    # Create an employee.
    email = f"list-test-{uuid4().hex[:8]}@example.com"

    create_response = client.post(
        "/api/v1/employees/",
        json={
            "first_name": "List",
            "last_name": "Tester",
            "email": email,
            "designation": "QA Engineer",
            "department_id": department_id,
            "date_of_joining": "2025-01-15",
        },
    )

    assert create_response.status_code == 201

    # Verify the employee appears in the list.
    response = client.get("/api/v1/employees/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        employee["email"] == email
        for employee in response.json()
    )



def test_create_employee_with_duplicate_email_returns_409(client):
    # Create a department.
    department_response = client.post(
        "/api/v1/departments/",
        json={
            "name": f"Duplicate-Test-{uuid4().hex[:8]}",
            "description": "Department for duplicate email test",
        },
    )
    assert department_response.status_code == 201
    department_id = department_response.json()["id"]

    email = f"duplicate-{uuid4().hex[:8]}@example.com"

    payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "email": email,
        "designation": "Python Developer",
        "department_id": department_id,
        "date_of_joining": "2025-01-15",
    }

    first_response = client.post(
        "/api/v1/employees/",
        json=payload,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/employees/",
        json=payload,
    )
    assert second_response.status_code == 409


def test_create_employee_with_invalid_department_returns_404(client):
    response = client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Test",
            "last_name": "Employee",
            "email": f"invalid-dept-{uuid4().hex[:8]}@example.com",
            "designation": "Python Developer",
            "department_id": 999999999,
            "date_of_joining": "2025-01-15",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Department not found."
