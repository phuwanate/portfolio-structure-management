import sys
from unittest.mock import MagicMock

# Mock psycopg2 before any import touches it
sys.modules["psycopg2"] = MagicMock()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override DATABASE_URL before importing app modules
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Now patch backend.database to use SQLite
import backend.database as db_module

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal

from backend.database import Base, get_db
from backend.main import app, _init_cashflow


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _init_cashflow(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
