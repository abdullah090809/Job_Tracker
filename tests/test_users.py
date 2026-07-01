import pytest
from app.schemas.user import UserOut


def test_create_user(client):
    response = client.post("/users", json={
        "email": "newuser@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 201
    new_user = UserOut(**response.json())
    assert new_user.email == "newuser@gmail.com"


def test_create_user_duplicate_email(client):
    client.post("/users", json={"email": "dup@gmail.com", "password": "pass123"})
    response = client.post("/users", json={"email": "dup@gmail.com", "password": "pass123"})
    assert response.status_code == 400


def test_login_success(client, create_test_user):
    response = client.post("/login", data={
        "username": create_test_user["email"],
        "password": create_test_user["password"]
    })
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


def test_login_wrong_password(client, create_test_user):
    response = client.post("/login", data={
        "username": create_test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_wrong_email(client):
    response = client.post("/login", data={
        "username": "nonexistent@gmail.com",
        "password": "somepassword"
    })
    assert response.status_code == 401


def test_get_all_users(client, create_test_user):
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_update_password(authorized_client, create_test_user):
    response = authorized_client.put("/users", json={
        "old_password": create_test_user["password"],
        "new_password": "newpassword123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_update_password_wrong_old(authorized_client):
    response = authorized_client.put("/users", json={
        "old_password": "wrongoldpassword",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400


def test_delete_user(authorized_client, create_test_user):
    response = authorized_client.delete(f"/users/{create_test_user['id']}")
    assert response.status_code == 204