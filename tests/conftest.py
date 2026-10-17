
import os

# Set test environment before importing the application.
os.environ["DB_NAME"] = "employee_management_test_db"
os.environ["API_ACCESS_TOKEN"] = "test-secret-token-for-employee-api"

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app
from app.models import Department, Employee


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        test_client.headers.update(
            {"Authorization": "Bearer test-secret-token-for-employee-api"}
        )
        yield test_client
