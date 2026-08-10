import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import main
from main import app, get_session

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture
def client():
    SQLModel.metadata.create_all(test_engine)

    def get_test_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    # Prevent the application's normal PostgreSQL startup
    # from running during tests.
    original_create_db_and_tables = main.create_db_and_tables
    main.create_db_and_tables = lambda: None

    with TestClient(app) as test_client:
        yield test_client

    main.create_db_and_tables = original_create_db_and_tables
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)
