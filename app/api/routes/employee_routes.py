
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services import employee_service

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    existing_employee = employee_service.get_employee_by_email(
        db, str(employee_data.email)
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists.",
        )

    try:
        return employee_service.create_employee(db, employee_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee data conflicts with an existing record.",
        ) from exc


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return employee_service.get_employees(
        db, skip=skip, limit=limit
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = employee_service.get_employee_by_id(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = employee_service.get_employee_by_id(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    # Check duplicate email only when email is provided.
    if employee_data.email is not None:
        existing_employee = employee_service.get_employee_by_email(
            db, str(employee_data.email)
        )

        if existing_employee and existing_employee.id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An employee with this email already exists.",
            )

    try:
        return employee_service.update_employee(
            db, employee, employee_data
        )
    except ValueError as exc:
        if str(exc) == "Department not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee data conflicts with an existing record.",
        ) from exc


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = employee_service.get_employee_by_id(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    employee_service.delete_employee(db, employee)
    return None
