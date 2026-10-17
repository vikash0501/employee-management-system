
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def get_employee_by_email(db: Session, email: str) -> Employee | None:
    statement = select(Employee).where(Employee.email == email)
    return db.scalar(statement)


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Employee]:
    statement = select(Employee).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
    department = db.get(Department, employee_data.department_id)

    if department is None:
        raise ValueError("Department not found.")

    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(
    db: Session,
    employee: Employee,
    employee_data: EmployeeUpdate,
) -> Employee:
    department = db.get(Department, employee_data.department_id)

    if department is None:
        raise ValueError("Department not found.")

    for field, value in employee_data.model_dump().items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()
