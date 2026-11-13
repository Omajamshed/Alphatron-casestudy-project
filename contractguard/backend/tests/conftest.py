import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base
import app.db.session as session_module
from app.db.models.user import User
from app.core.security import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite:///./test_contractguard.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Point session_module.SessionLocal and engine to test engine
session_module.engine = test_engine
session_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    import uuid
    user = User(
        id=str(uuid.uuid4()),
        email=f"tenant_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("testpass123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_auth_headers(test_user):
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}
