
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


SORTABLE_FIELDS = {
    "id": Employee.id,
    "first_name": Employee.first_name,
    "last_name": Employee.last_name,
    "email": Employee.email,
    "designation": Employee.designation,
}


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def get_employee_by_email(db: Session, email: str) -> Employee | None:
    statement = select(Employee).where(Employee.email == email)
    return db.scalar(statement)


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    department_id: int | None = None,
    designation: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> list[Employee]:
    statement = select(Employee)

    if search and search.strip():
        search_term = search.strip()
        statement = statement.where(
            Employee.first_name.icontains(search_term, autoescape=True)
            | Employee.last_name.icontains(search_term, autoescape=True)
            | Employee.email.icontains(search_term, autoescape=True)
        )

    if department_id is not None:
        statement = statement.where(
            Employee.department_id == department_id
        )

    if designation and designation.strip():
        designation_term = designation.strip()
        statement = statement.where(
            Employee.designation.icontains(
                designation_term, autoescape=True
            )
        )

    sort_column = SORTABLE_FIELDS.get(sort_by)
    if sort_column is None:
        raise ValueError("Unsupported sort field.")

    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc(), Employee.id.asc())
    else:
        statement = statement.order_by(sort_column.asc(), Employee.id.asc())

    statement = statement.offset(skip).limit(limit)

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
    update_data = employee_data.model_dump(exclude_unset=True)

    if "department_id" in update_data:
        department = db.get(Department, update_data["department_id"])

        if department is None:
            raise ValueError("Department not found.")

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()
