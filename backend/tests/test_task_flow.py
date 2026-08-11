from fastapi.testclient import TestClient

from app.main import app


def test_write_action_requires_approval() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v2/ops/tasks",
        json={
            "tenant_id": "demo",
            "property_id": "hotel-001",
            "objective": "调整周末房价",
        },
    )
    assert created.status_code == 201
    task_id = created.json()["id"]
    assert client.post(f"/api/v2/ops/tasks/{task_id}/execute").status_code == 409
    assert client.post(f"/api/v2/ops/tasks/{task_id}/approve").status_code == 200
    executed = client.post(f"/api/v2/ops/tasks/{task_id}/execute")
    assert executed.status_code == 200
    assert executed.json()["state"] == "EXECUTED"
