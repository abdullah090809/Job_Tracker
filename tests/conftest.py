from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.cores.config import settings
import pytest
from app.cores.database import get_db, Base
from app.cores.security import create_access_token
from app.models.application import Application
from app.main import app

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionMaker = sessionmaker(autoflush=False, autocommit=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionMaker()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def create_test_user(client):
    user_data = {
        "email": "abdullah@gmail.com",
        "password": "abdullah1234"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = "abdullah1234"
    return new_user


@pytest.fixture
def create_test_user2(client):
    user_data = {
        "email": "ali@gmail.com",
        "password": "ali1234"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = "ali1234"
    return new_user


@pytest.fixture()
def token(create_test_user):
    return create_access_token({"user_id": create_test_user["id"]})


@pytest.fixture()
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


def create_application(application_data):
    return Application(**application_data)


@pytest.fixture
def test_applications(create_test_user, session):
    applications_data = [
        {"company": "Google", "role": "Backend Engineer", "status": "applied", "applied_date": "2026-06-01", "user_id": create_test_user["id"]},
        {"company": "Meta", "role": "SWE", "status": "interview", "applied_date": "2026-06-10", "user_id": create_test_user["id"]},
        {"company": "Amazon", "role": "SDE", "status": "rejected", "applied_date": "2026-06-15", "user_id": create_test_user["id"]},
    ]
    applications = list(map(create_application, applications_data))
    session.add_all(applications)
    session.commit()
    return session.query(Application).all()