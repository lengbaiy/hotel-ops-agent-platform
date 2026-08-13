from dataclasses import replace

import jwt
from fastapi.testclient import TestClient

from app.api import security
from app.main import app


def test_invalid_task_type_is_rejected() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v2/ops/tasks",
        json={
            "tenant_id": "demo",
            "property_id": "hotel-001",
            "objective": "校验不支持的任务类型",
            "task_type": "unknown_task",
        },
    )
    assert response.status_code == 422


def test_request_id_and_readiness_endpoints_are_available() -> None:
    client = TestClient(app)
    request_id = "regression-check-001"
    response = client.get("/healthz", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
    assert client.get("/readyz").status_code == 200


def test_jwt_enforces_role_tenant_and_property_scope(monkeypatch) -> None:
    secured_settings = replace(
        security.settings,
        auth_mode="jwt",
        jwt_secret="test-secret-that-is-at-least-thirty-two-bytes",
        jwt_audience="hotel-ops-api",
    )
    monkeypatch.setattr(security, "settings", secured_settings)
    client = TestClient(app)
    token = jwt.encode(
        {
            "sub": "operator-001",
            "jti": "legacy-auth-test-token",
            "aud": "hotel-ops-api",
            "tenant_id": "tenant-a",
            "property_ids": ["hotel-a"],
            "roles": ["operator"],
        },
        "test-secret-that-is-at-least-thirty-two-bytes",
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}
    allowed = client.post(
        "/api/v2/ops/tasks",
        headers=headers,
        json={
            "tenant_id": "tenant-a",
            "property_id": "hotel-a",
            "objective": "校验 JWT 允许范围内的任务创建",
        },
    )
    assert allowed.status_code == 201

    denied_property = client.post(
        "/api/v2/ops/tasks",
        headers=headers,
        json={
            "tenant_id": "tenant-a",
            "property_id": "hotel-b",
            "objective": "校验 JWT 酒店范围限制",
        },
    )
    assert denied_property.status_code == 403

    denied_tenant = client.post(
        "/api/v2/ops/tasks",
        headers=headers,
        json={
            "tenant_id": "tenant-b",
            "property_id": "hotel-a",
            "objective": "校验 JWT 租户范围限制",
        },
    )
    assert denied_tenant.status_code == 403

    no_token = client.post(
        "/api/v2/ops/tasks",
        json={
            "tenant_id": "tenant-a",
            "property_id": "hotel-a",
            "objective": "校验 JWT 缺失令牌拒绝",
        },
    )
    assert no_token.status_code == 401
