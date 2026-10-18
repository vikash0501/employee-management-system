
import os

# Configure the test environment before importing application modules.
os.environ["DB_NAME"] = "employee_management_test_db"
os.environ["API_ACCESS_TOKEN"] = "test-secret-token-for-employee-api"

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app
from app.models import Department, Employee


TEST_DATABASE_NAME = "employee_management_test_db"


def verify_test_database() -> None:
    """Prevent test fixtures from modifying a non-test database."""
    if engine.url.database != TEST_DATABASE_NAME:
        raise RuntimeError(
            "Unsafe test database configuration. "
            f"Expected '{TEST_DATABASE_NAME}', "
            f"got '{engine.url.database}'."
        )


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    verify_test_database()
    Base.metadata.create_all(bind=engine)

    yield

    # Check again before performing destructive cleanup.
    verify_test_database()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
@pytest.fixture
def client():
    verify_test_database()

    with TestClient(app) as test_client:
        test_client.headers.update(
            {"Authorization": "Bearer test-secret-token-for-employee-api"}
        )
        yield test_client
