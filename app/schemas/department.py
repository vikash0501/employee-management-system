
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Engineering"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        examples=["Software engineering department"],
    )


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["Engineering"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        examples=["Software engineering department"],
    )


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
