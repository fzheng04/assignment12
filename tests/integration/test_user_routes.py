
from uuid import uuid4

from app.models import User
from app.security import verify_password


def new_user():
    suffix = uuid4().hex[:10]

    return {
        "username": f"user_{suffix}",
        "email": f"{suffix}@example.com",
        "password": "SecurePassword123!",
    }


def test_register(client_and_db):
    client, db = client_and_db
    payload = new_user()

    response = client.post("/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    user = db.query(User).filter_by(
        username=payload["username"]
    ).one()

    assert user.password_hash != payload["password"]
    assert verify_password(
        payload["password"], user.password_hash
    )


def test_duplicate_registration(client_and_db):
    client, _ = client_and_db
    payload = new_user()

    assert client.post(
        "/users/register", json=payload
    ).status_code == 201

    response = client.post("/users/register", json=payload)

    assert response.status_code == 409


def test_invalid_registration(client_and_db):
    client, _ = client_and_db
    payload = new_user()
    payload["email"] = "invalid-email"

    response = client.post("/users/register", json=payload)

    assert response.status_code == 400


def test_login_success(client_and_db):
    client, _ = client_and_db
    payload = new_user()

    assert client.post(
        "/users/register", json=payload
    ).status_code == 201

    response = client.post("/users/login", json={
        "username": payload["username"],
        "password": payload["password"],
    })

    assert response.status_code == 200
    assert response.json()["username"] == payload["username"]
    assert "password_hash" not in response.json()


def test_login_wrong_password(client_and_db):
    client, _ = client_and_db
    payload = new_user()

    assert client.post(
        "/users/register", json=payload
    ).status_code == 201

    response = client.post("/users/login", json={
        "username": payload["username"],
        "password": "WrongPassword123!",
    })

    assert response.status_code == 401


def test_login_nonexistent_user(client_and_db):
    client, _ = client_and_db

    response = client.post("/users/login", json={
        "username": f"missing_{uuid4().hex[:10]}",
        "password": "SecurePassword123!",
    })

    assert response.status_code == 401


def test_login_invalid_data(client_and_db):
    client, _ = client_and_db

    response = client.post("/users/login", json={
        "username": "testuser",
    })

    assert response.status_code == 400
