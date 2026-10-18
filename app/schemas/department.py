
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


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

    @model_validator(mode="after")
    def validate_name(self):
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Department name cannot be null.")
        return self


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
