"""
Pytest Configuration and Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides test fixtures and configuration for the test suite.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.employee import Employee


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    
    Yields:
        Database session
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Add test data
    test_employee = Employee(
        id=1,
        name="John Doe",
        email="john.doe@company.com",
        department="IT",
        video_1_completed=True,
        video_1_duration=15.5,
        video_2_completed=True,
        video_2_duration=20.0,
        video_3_completed=False,
        video_3_duration=0.0,
        video_4_completed=False,
        video_4_duration=0.0,
        video_5_completed=False,
        video_5_duration=0.0,
        total_time=35.5,
        completion_percentage=40.0
    )
    db.add(test_employee)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with database override.
    
    Yields:
        FastAPI test client
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

