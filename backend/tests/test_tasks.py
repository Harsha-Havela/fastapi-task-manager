import pytest


# ── helpers ──────────────────────────────────────────────────────────────────

def create_task(client, headers, title="Buy groceries", description="Milk and eggs"):
    return client.post("/tasks", json={"title": title, "description": description}, headers=headers)


# ── create ────────────────────────────────────────────────────────────────────

def test_create_task(client, auth_headers):
    resp = create_task(client, auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy groceries"
    assert data["completed"] is False


def test_create_task_unauthenticated(client):
    resp = client.post("/tasks", json={"title": "Test"})
    assert resp.status_code == 403


def test_create_task_empty_title(client, auth_headers):
    resp = client.post("/tasks", json={"title": "   "}, headers=auth_headers)
    assert resp.status_code == 422


# ── list ──────────────────────────────────────────────────────────────────────

def test_list_tasks(client, auth_headers):
    create_task(client, auth_headers, title="Task 1")
    create_task(client, auth_headers, title="Task 2")
    resp = client.get("/tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["tasks"]) == 2


def test_list_tasks_filter_completed(client, auth_headers):
    t1 = create_task(client, auth_headers, title="Task 1").json()
    create_task(client, auth_headers, title="Task 2")
    # Mark task 1 as completed
    client.put(f"/tasks/{t1['id']}", json={"completed": True}, headers=auth_headers)

    resp = client.get("/tasks?completed=true", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["tasks"][0]["completed"] is True


def test_list_tasks_pagination(client, auth_headers):
    for i in range(5):
        create_task(client, auth_headers, title=f"Task {i}")
    resp = client.get("/tasks?page=1&page_size=3", headers=auth_headers)
    data = resp.json()
    assert len(data["tasks"]) == 3
    assert data["total"] == 5
    assert data["total_pages"] == 2


# ── get single ────────────────────────────────────────────────────────────────

def test_get_task(client, auth_headers):
    task_id = create_task(client, auth_headers).json()["id"]
    resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


def test_get_task_not_found(client, auth_headers):
    resp = client.get("/tasks/9999", headers=auth_headers)
    assert resp.status_code == 404


# ── update ────────────────────────────────────────────────────────────────────

def test_update_task_title(client, auth_headers):
    task_id = create_task(client, auth_headers).json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"title": "Updated title"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"


def test_mark_task_completed(client, auth_headers):
    task_id = create_task(client, auth_headers).json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"completed": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


def test_update_task_not_found(client, auth_headers):
    resp = client.put("/tasks/9999", json={"title": "X"}, headers=auth_headers)
    assert resp.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_task(client, auth_headers):
    task_id = create_task(client, auth_headers).json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204
    # Confirm it's gone
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404


def test_delete_task_not_found(client, auth_headers):
    resp = client.delete("/tasks/9999", headers=auth_headers)
    assert resp.status_code == 404


# ── ownership isolation ───────────────────────────────────────────────────────

def test_user_cannot_access_other_users_task(client, auth_headers):
    task_id = create_task(client, auth_headers).json()["id"]

    # Register and login a second user
    client.post(
        "/register",
        json={"username": "bob", "email": "bob@example.com", "password": "bobpass1"},
    )
    token = client.post(
        "/login", json={"username": "bob", "password": "bobpass1"}
    ).json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {token}"}

    assert client.get(f"/tasks/{task_id}", headers=bob_headers).status_code == 404
    assert client.delete(f"/tasks/{task_id}", headers=bob_headers).status_code == 404
