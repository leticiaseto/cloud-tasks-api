import pytest
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_health(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.json["status"] == "ok"


def test_create_and_list(client):
    result = client.post("/tasks", json={"title": "Estudar GitHub Actions"})
    assert result.status_code == 201
    assert result.json["id"] == 1
    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.json) == 1
    assert listed.json[0]["title"] == "Estudar GitHub Actions"


def test_invalid_title(client):
    assert client.post("/tasks", json={"title": "  "}).status_code == 400


def test_mark_done(client):
    item = client.post("/tasks", json={"title": "Deploy"}).json
    result = client.patch(f'/tasks/{item["id"]}', json={"done": True})
    assert result.status_code == 200
    assert client.get("/tasks").json[0]["done"] is True


def test_not_found(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404


def test_delete_removes_only_requested_task(client):
    first = client.post("/tasks", json={"title": "Primeira"}).json
    second = client.post("/tasks", json={"title": "Segunda"}).json
    result = client.delete(f'/tasks/{first["id"]}')
    assert result.status_code == 204
    assert result.data == b""
    remaining = client.get("/tasks").json
    assert [task["id"] for task in remaining] == [second["id"]]


def test_delete_not_found(client):
    result = client.delete("/tasks/999")
    assert result.status_code == 404
    assert result.json["error"] == "tarefa nao encontrada"


def test_delete_twice_returns_404_on_second_call(client):
    item = client.post("/tasks", json={"title": "Remover uma vez"}).json
    assert client.delete(f'/tasks/{item["id"]}').status_code == 204
    assert client.delete(f'/tasks/{item["id"]}').status_code == 404


def test_version_endpoint(client):
    result = client.get("/version")
    assert result.status_code == 200
    assert result.json["service"] == "cloud-tasks-api"
    assert result.json["version"] == "1.0.0"
