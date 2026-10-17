
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    designation: str = Field(min_length=2, max_length=100)
    department_id: int = Field(gt=0)
    date_of_joining: date
    employment_status: Literal["ACTIVE", "INACTIVE", "ON_LEAVE"] = "ACTIVE"


class EmployeeCreate(EmployeeBase):
    pass 


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
