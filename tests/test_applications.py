import pytest
from app.models.application import ApplicationStatus


def test_create_application(authorized_client):
    response = authorized_client.post("/applications", json={
        "company": "Google",
        "role": "Backend Engineer",
        "status": "applied",
        "applied_date": "2026-06-01",
        "jd_text": "We need a Python developer",
        "notes": "Referred by a friend"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Google"
    assert data["role"] == "Backend Engineer"
    assert data["status"] == "applied"


def test_create_application_unauthorized(client):
    response = client.post("/applications", json={
        "company": "Google",
        "role": "Backend Engineer",
        "status": "applied",
        "applied_date": "2026-06-01"
    })
    assert response.status_code == 401


def test_get_all_applications(authorized_client, test_applications):
    response = authorized_client.get("/applications")
    assert response.status_code == 200
    assert len(response.json()) == len(test_applications)


def test_get_all_applications_unauthorized(client):
    response = client.get("/applications")
    assert response.status_code == 401


def test_get_one_application(authorized_client, test_applications):
    response = authorized_client.get(f"/applications/{test_applications[0].id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_applications[0].id
    assert data["company"] == test_applications[0].company


def test_get_one_application_not_found(authorized_client):
    response = authorized_client.get("/applications/-99999")
    assert response.status_code == 404


def test_get_one_application_unauthorized(client, test_applications):
    response = client.get(f"/applications/{test_applications[0].id}")
    assert response.status_code == 401


def test_update_application(authorized_client, test_applications):
    response = authorized_client.put(f"/applications/{test_applications[0].id}", json={
        "status": "interview",
        "notes": "Got a call back"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "interview"
    assert response.json()["notes"] == "Got a call back"


def test_update_application_not_found(authorized_client):
    response = authorized_client.put("/applications/-99999", json={
        "status": "interview"
    })
    assert response.status_code == 404


def test_update_application_unauthorized(client, test_applications):
    response = client.put(f"/applications/{test_applications[0].id}", json={
        "status": "interview"
    })
    assert response.status_code == 401


def test_delete_application(authorized_client, test_applications):
    response = authorized_client.delete(f"/applications/{test_applications[0].id}")
    assert response.status_code == 204


def test_delete_application_not_found(authorized_client):
    response = authorized_client.delete("/applications/-99999")
    assert response.status_code == 404


def test_delete_application_unauthorized(client, test_applications):
    response = client.delete(f"/applications/{test_applications[0].id}")
    assert response.status_code == 401