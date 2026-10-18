
from uuid import uuid4

import pytest


def create_department(client, name_prefix="Engineering"):
    response = client.post(
        "/api/v1/departments/",
        json={
            "name": f"{name_prefix}-{uuid4().hex[:8]}",
            "description": "Department for employee tests",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_employee(client, department_id, **overrides):
    payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "email": f"employee-{uuid4().hex[:8]}@example.com",
        "designation": "Python Developer",
        "department_id": department_id,
        "date_of_joining": "2025-01-15",
    }
    payload.update(overrides)

    response = client.post("/api/v1/employees/", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_employee(client):
    department_id = create_department(client)
    email = f"employee-{uuid4().hex[:8]}@example.com"

    employee = create_employee(
        client,
        department_id,
        email=email,
        designation="Python Developer",
        date_of_joining="2025-01-15",
    )

    assert employee["first_name"] == "Test"
    assert employee["last_name"] == "Employee"
    assert employee["email"] == email
    assert employee["designation"] == "Python Developer"
    assert employee["date_of_joining"].startswith("2025-01-15")
    assert employee["department_id"] == department_id
    assert "id" in employee


def test_list_employees(client):
    department_id = create_department(client, "QA")
    employee = create_employee(client, department_id)

    response = client.get("/api/v1/employees/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(item["id"] == employee["id"] for item in response.json())


def test_get_employee_by_id(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.get(f"/api/v1/employees/{employee['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == employee["id"]
    assert response.json()["email"] == employee["email"]


def test_get_nonexistent_employee_returns_404(client):
    response = client.get("/api/v1/employees/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


def test_update_employee_partial_data_preserves_other_fields(client):
    department_id = create_department(client)
    employee = create_employee(
        client,
        department_id,
        phone="9876543210",
        employment_status="INACTIVE",
    )

    response = client.put(
        f"/api/v1/employees/{employee['id']}",
        json={"phone": "9123456780"},
    )

    assert response.status_code == 200
    updated = response.json()

    assert updated["phone"] == "9123456780"
    assert updated["employment_status"] == "INACTIVE"
    assert updated["first_name"] == employee["first_name"]
    assert updated["email"] == employee["email"]
    assert updated["department_id"] == department_id


def test_update_employee_with_same_email_returns_200(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.put(
        f"/api/v1/employees/{employee['id']}",
        json={"email": employee["email"]},
    )

    assert response.status_code == 200
    assert response.json()["id"] == employee["id"]
    assert response.json()["email"] == employee["email"]


def test_update_employee_with_duplicate_email_returns_409(client):
    department_id = create_department(client)
    first = create_employee(client, department_id)
    second = create_employee(client, department_id)

    response = client.put(
        f"/api/v1/employees/{second['id']}",
        json={"email": first["email"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An employee with this email already exists."
    )


def test_update_employee_with_invalid_department_returns_404(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.put(
        f"/api/v1/employees/{employee['id']}",
        json={"department_id": 999999999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Department not found."


def test_update_employee_with_null_first_name_returns_422(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.put(
        f"/api/v1/employees/{employee['id']}",
        json={"first_name": None},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "first_name cannot be null."


def test_update_employee_with_null_last_name_returns_422(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.put(
        f"/api/v1/employees/{employee['id']}",
        json={"last_name": None},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "last_name cannot be null."


def test_update_employee_with_null_email_returns_422(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.put(
        f"/api/v1/employees/{employee['id']}",
        json={"email": None},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "email cannot be null."


def test_update_nonexistent_employee_returns_404(client):
    response = client.put(
        "/api/v1/employees/999999999",
        json={"first_name": "Updated"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


def test_create_employee_with_duplicate_email_returns_409(client):
    department_id = create_department(client)
    email = f"duplicate-{uuid4().hex[:8]}@example.com"

    create_employee(client, department_id, email=email)

    response = client.post(
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

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An employee with this email already exists."
    )


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


def test_delete_employee(client):
    department_id = create_department(client)
    employee = create_employee(client, department_id)

    response = client.delete(
        f"/api/v1/employees/{employee['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/employees/{employee['id']}"
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_employee_returns_404(client):
    response = client.delete("/api/v1/employees/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


def test_search_employees_by_name(client):
    department_id = create_department(client)

    employee = create_employee(
        client,
        department_id,
        first_name="Vikash",
        last_name="Kumar",
        email=f"vikash-{uuid4().hex[:8]}@example.com",
    )

    other_employee = create_employee(
        client,
        department_id,
        first_name="Rahul",
        last_name="Sharma",
        email=f"rahul-{uuid4().hex[:8]}@example.com",
    )

    response = client.get(
        "/api/v1/employees/",
        params={"search": "vikash"},
    )
    assert response.status_code == 200
    results = response.json()
    assert any(item["id"] == employee["id"] for item in results)
    assert all(item["id"] != other_employee["id"] for item in results)

    response = client.get(
        "/api/v1/employees/",
        params={"search": "Kumar"},
    )
    assert response.status_code == 200
    results = response.json()
    assert any(item["id"] == employee["id"] for item in results)
    assert all(item["id"] != other_employee["id"] for item in results)

    response = client.get(
        "/api/v1/employees/",
        params={"search": employee["email"]},
    )
    assert response.status_code == 200
    results = response.json()
    assert any(item["id"] == employee["id"] for item in results)
    assert all(item["id"] != other_employee["id"] for item in results)

    response = client.get(
        "/api/v1/employees/",
        params={"search": "nonexistent-employee-xyz"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_filter_employees_by_department(client):
    first_department_id = create_department(client, "Engineering")
    second_department_id = create_department(client, "Finance")

    employee = create_employee(client, first_department_id)
    create_employee(client, second_department_id)

    response = client.get(
        "/api/v1/employees/",
        params={"department_id": first_department_id},
    )

    assert response.status_code == 200
    results = response.json()
    assert results
    assert all(
        item["department_id"] == first_department_id
        for item in results
    )
    assert any(item["id"] == employee["id"] for item in results)


def test_filter_employees_by_designation(client):
    department_id = create_department(client)

    employee = create_employee(
        client,
        department_id,
        designation="Senior Python Developer",
    )
    create_employee(
        client,
        department_id,
        designation="Java Developer",
    )

    response = client.get(
        "/api/v1/employees/",
        params={"designation": "python"},
    )

    assert response.status_code == 200
    results = response.json()
    assert any(item["id"] == employee["id"] for item in results)
    assert all(
        "python" in item["designation"].lower()
        for item in results
    )


def test_search_with_nul_byte_returns_422(client):
    response = client.get(
        "/api/v1/employees/",
        params={"search": "\x00"},
    )

    assert response.status_code == 422


def test_designation_with_nul_byte_returns_422(client):
    response = client.get(
        "/api/v1/employees/",
        params={"designation": "\x00"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "sort_by",
    ["id", "first_name", "last_name", "email", "designation"],
)
@pytest.mark.parametrize("sort_order", ["asc", "desc"])
def test_sort_employees_by_field_and_order(client, sort_by, sort_order):
    department_id = create_department(client)

    create_employee(
        client,
        department_id,
        first_name="Zoya",
        last_name="Patel",
        email=f"zoya-{uuid4().hex[:8]}@example.com",
        designation="QA Engineer",
    )
    create_employee(
        client,
        department_id,
        first_name="Amit",
        last_name="Sharma",
        email=f"amit-{uuid4().hex[:8]}@example.com",
        designation="Python Developer",
    )
    create_employee(
        client,
        department_id,
        first_name="Neha",
        last_name="Verma",
        email=f"neha-{uuid4().hex[:8]}@example.com",
        designation="Data Engineer",
    )

    response = client.get(
        "/api/v1/employees/",
        params={"sort_by": sort_by, "sort_order": sort_order},
    )

    assert response.status_code == 200

    values = [employee[sort_by] for employee in response.json()]
    expected = sorted(values, reverse=(sort_order == "desc"))

    assert values == expected


def test_sort_employees_invalid_sort_field(client):
    response = client.get(
        "/api/v1/employees/",
        params={"sort_by": "password"},
    )

    assert response.status_code == 422


def test_sort_employees_invalid_sort_order(client):
    response = client.get(
        "/api/v1/employees/",
        params={"sort_order": "random"},
    )

    assert response.status_code == 422
