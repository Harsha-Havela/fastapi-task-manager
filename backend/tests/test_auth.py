import pytest


def test_register_success(client):
    resp = client.post(
        "/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password1"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client):
    payload = {"username": "alice", "email": "alice@example.com", "password": "password1"}
    client.post("/register", json=payload)
    resp = client.post(
        "/register",
        json={"username": "alice", "email": "other@example.com", "password": "password1"},
    )
    assert resp.status_code == 400
    assert "Username already taken" in resp.json()["detail"]


def test_register_duplicate_email(client):
    client.post(
        "/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password1"},
    )
    resp = client.post(
        "/register",
        json={"username": "bob", "email": "alice@example.com", "password": "password1"},
    )
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_register_short_password(client):
    resp = client.post(
        "/register",
        json={"username": "alice", "email": "alice@example.com", "password": "abc"},
    )
    assert resp.status_code == 422


def test_login_success(client, registered_user):
    resp = client.post(
        "/login",
        json={"username": registered_user["username"], "password": registered_user["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post(
        "/login",
        json={"username": registered_user["username"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/login", json={"username": "nobody", "password": "password1"})
    assert resp.status_code == 401
