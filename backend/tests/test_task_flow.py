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
    events = client.get(f"/api/v2/ops/tasks/{task_id}/events")
    assert events.status_code == 200
    assert events.json() == [
        "task_created",
        "supervisor:routed_to:revenue_management",
        "agent:revenue_management:recommendation_generated",
        "policy_judge:approval_required",
        "task_waiting_for_human_approval",
    ]
    assert client.post(f"/api/v2/ops/tasks/{task_id}/execute").status_code == 409
    assert client.post(f"/api/v2/ops/tasks/{task_id}/approve").status_code == 200
    executed = client.post(f"/api/v2/ops/tasks/{task_id}/execute")
    assert executed.status_code == 200
    assert executed.json()["state"] == "EXECUTED"


def test_openapi_contains_core_contracts() -> None:
    client = TestClient(app)
    document = client.get("/openapi.json")
    assert document.status_code == 200
    paths = document.json()["paths"]
    assert "/api/v2/dashboard/overview" in paths
    assert "/api/v2/ops/tasks" in paths
    assert "/api/v2/ops/tasks/{task_id}/events" in paths


def test_task_list_is_scoped_to_property() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v2/ops/tasks",
        json={
            "tenant_id": "demo",
            "property_id": "hotel-002",
            "objective": "核验西湖门店的渠道库存状态",
        },
    )
    assert created.status_code == 201
    response = client.get("/api/v2/ops/tasks?property_id=hotel-002")
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_supervisor_routes_market_task_to_market_agent() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v2/ops/tasks",
        json={
            "tenant_id": "demo",
            "property_id": "hotel-001",
            "objective": "分析未来七天同行价格和大型活动变化",
            "task_type": "market_intelligence",
        },
    )
    assert created.status_code == 201
    task = created.json()
    assert task["state"] == "WAITING_APPROVAL"
    assert task["recommendation"]["action"] == "create_market_evidence"
    events = client.get(f"/api/v2/ops/tasks/{task['id']}/events").json()
    assert "supervisor:routed_to:market_intelligence" in events
