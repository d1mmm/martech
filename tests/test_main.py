import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db import Base, get_session
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def test_session():
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_session] = lambda: TestingSessionLocal()
    with TestClient(app) as c:
        yield c

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text

def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert "Register" in response.text

def test_register_user(client, test_session):
    data = {
        "username": "testuser",
        "password": "testpassword",
        "name": "Test User"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

def test_login(client, test_session):
    data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_upload_page(client):
    response = client.get("/upload")
    assert response.status_code == 200
    assert "Upload" in response.text

def test_admin_page(client):
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Admin Panel" in response.text

def test_results_page(client):
    response = client.get("/results")
    assert response.status_code == 200
    assert "Aggregated Results" in response.text

def test_log_files_page(client):
    response = client.get("/admin/log-files")
    assert response.status_code == 200
    assert "Logs" in response.text

def test_full_data_page(client):
    response = client.get("/admin/full-data")
    assert response.status_code == 200
    assert "Full Data" in response.text
