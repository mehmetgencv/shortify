import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.main import app
from app.database.database import get_db

# Test database settings
TEST_POSTGRES_USER = os.getenv("TEST_POSTGRES_USER", "postgres")
TEST_POSTGRES_PASSWORD = os.getenv("TEST_POSTGRES_PASSWORD", "postgres")
TEST_POSTGRES_HOST = os.getenv("TEST_POSTGRES_HOST", "localhost")
TEST_POSTGRES_PORT = os.getenv("TEST_POSTGRES_PORT", "5433")
TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB", "url_shortener_test")

# Test database URL
TEST_DATABASE_URL = f"postgresql://{TEST_POSTGRES_USER}:{TEST_POSTGRES_PASSWORD}@{TEST_POSTGRES_HOST}:{TEST_POSTGRES_PORT}/{TEST_POSTGRES_DB}"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db():
    """Get test database session"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """Get test client with database session"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]