
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def get_department_by_id(db: Session, department_id: int) -> Department | None:
    return db.get(Department, department_id)


def get_department_by_name(db: Session, name: str) -> Department | None:
    statement = select(Department).where(Department.name == name)
    return db.scalar(statement)


def get_departments(db: Session, skip: int = 0, limit: int = 100) -> list[Department]:
    statement = select(Department).order_by(Department.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_department(db: Session, department_data: DepartmentCreate) -> Department:
    department = Department(**department_data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def update_department(
    db: Session,
    department: Department,
    department_data: DepartmentUpdate,
) -> Department:
    for field, value in department_data.model_dump().items():
        setattr(department, field, value)

    db.commit()
    db.refresh(department)
    return department

def department_has_employees(db: Session, department_id: int) -> bool:
    statement = select(Employee.id).where(
        Employee.department_id == department_id
    ).limit(1)

    return db.scalar(statement) is not None

def delete_department(db: Session, department: Department) -> None:
    db.delete(department)
    db.commit()
