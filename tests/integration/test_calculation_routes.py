
import pytest

from app.models import Calculation


def create_calculation(client):
    response = client.post("/calculations", json={
        "a": 10,
        "b": 5,
        "type": "add",
    })

    assert response.status_code == 201
    return response.json()


def test_create_calculation(client_and_db):
    client, db = client_and_db

    data = create_calculation(client)

    assert data["a"] == 10
    assert data["b"] == 5
    assert data["type"] == "add"
    assert data["result"] == 15

    saved = db.get(Calculation, data["id"])

    assert saved is not None
    assert saved.result == 15


def test_browse_calculations(client_and_db):
    client, _ = client_and_db
    data = create_calculation(client)

    response = client.get("/calculations")

    assert response.status_code == 200
    assert data in response.json()


def test_read_calculation(client_and_db):
    client, _ = client_and_db
    data = create_calculation(client)

    response = client.get(f"/calculations/{data['id']}")

    assert response.status_code == 200
    assert response.json() == data


def test_update_calculation(client_and_db):
    client, db = client_and_db
    data = create_calculation(client)

    response = client.put(
        f"/calculations/{data['id']}",
        json={
            "a": 20,
            "b": 5,
            "type": "multiply",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["id"] == data["id"]
    assert updated["a"] == 20
    assert updated["b"] == 5
    assert updated["type"] == "multiply"
    assert updated["result"] == 100

    db.expire_all()
    saved = db.get(Calculation, data["id"])
    assert saved.result == 100


def test_delete_calculation(client_and_db):
    client, db = client_and_db
    data = create_calculation(client)

    response = client.delete(
        f"/calculations/{data['id']}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/calculations/{data['id']}"
    )

    assert response.status_code == 404
    db.expire_all()
    assert db.get(Calculation, data["id"]) is None


def test_read_nonexistent_calculation(client_and_db):
    client, _ = client_and_db

    response = client.get("/calculations/-1")

    assert response.status_code == 404


def test_update_nonexistent_calculation(client_and_db):
    client, _ = client_and_db

    response = client.put("/calculations/-1", json={
        "a": 10,
        "b": 5,
        "type": "add",
    })

    assert response.status_code == 404


def test_delete_nonexistent_calculation(client_and_db):
    client, _ = client_and_db

    response = client.delete("/calculations/-1")

    assert response.status_code == 404


@pytest.mark.parametrize("payload", [
    {"a": 10, "b": 0, "type": "divide"},
    {"a": 10, "b": 5, "type": "invalid"},
    {"a": "hello", "b": 5, "type": "add"},
    {"a": 10, "type": "add"},
])
def test_invalid_calculation(client_and_db, payload):
    client, _ = client_and_db

    response = client.post(
        "/calculations", json=payload
    )

    assert response.status_code == 400
    assert "error" in response.json()


def test_invalid_update(client_and_db):
    client, _ = client_and_db
    data = create_calculation(client)

    response = client.put(
        f"/calculations/{data['id']}",
        json={
            "a": 10,
            "b": 0,
            "type": "divide",
        },
    )

    assert response.status_code == 400

    response = client.get(
        f"/calculations/{data['id']}"
    )

    assert response.json() == data
