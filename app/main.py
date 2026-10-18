
from fastapi import Depends, FastAPI

from app.api.routes.department_routes import router as department_router
from app.api.routes.employee_routes import router as employee_router
from app.core.auth import verify_api_token

app = FastAPI(
    title="Employee Management System API",
    description="A professional REST API for managing employees and departments.",
    version="1.0.0",
)

app.include_router(
    department_router,
    prefix="/api/v1",
    dependencies=[Depends(verify_api_token)],
)

app.include_router(
    employee_router,
    prefix="/api/v1",
    dependencies=[Depends(verify_api_token)],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Check whether the API is running."""
    return {
        "status": "healthy",
        "service": "Employee Management System API",
    }


@app.get("/", tags=["Root"])
def root():
    """Return basic API information."""
    return {
        "message": "Welcome to Employee Management System API",
        "docs": "/docs",
    }
