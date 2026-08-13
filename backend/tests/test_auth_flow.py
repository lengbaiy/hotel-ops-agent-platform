from dataclasses import replace

from fastapi.testclient import TestClient

from app.api import security
from app.api.v2 import auth
from app.core import config
from app.main import app
from app.services import auth_service


def _enable_jwt(monkeypatch) -> None:
    secured_settings = replace(
        config.settings,
        auth_mode="jwt",
        jwt_secret="test-secret-that-is-at-least-thirty-two-bytes",
        jwt_audience="hotel-ops-api",
        jwt_expire_minutes=30,
    )
    monkeypatch.setattr(config, "settings", secured_settings)
    monkeypatch.setattr(security, "settings", secured_settings)
    monkeypatch.setattr(auth_service, "settings", secured_settings)
    security.revoked_token_ids.clear()
    auth.auth_service.captchas.clear()


def _captcha(client: TestClient) -> tuple[dict[str, int | str], int]:
    response = client.post("/api/v2/auth/captcha")
    assert response.status_code == 200
    payload = response.json()
    target_position, _ = auth.auth_service.captchas[payload["captcha_id"]]
    return payload, target_position


def test_login_requires_a_valid_one_time_slider_challenge(monkeypatch) -> None:
    _enable_jwt(monkeypatch)
    client = TestClient(app)
    challenge, target_position = _captcha(client)
    invalid = client.post(
        "/api/v2/auth/login",
        json={
            "username": "ops-admin",
            "password": "HotelOps@2026",
            "captcha_id": challenge["captcha_id"],
            "slider_position": target_position + 5,
        },
    )
    assert invalid.status_code == 401

    reused = client.post(
        "/api/v2/auth/login",
        json={
            "username": "ops-admin",
            "password": "HotelOps@2026",
            "captcha_id": challenge["captcha_id"],
            "slider_position": target_position,
        },
    )
    assert reused.status_code == 401


def test_login_me_role_enforcement_and_logout(monkeypatch) -> None:
    _enable_jwt(monkeypatch)
    client = TestClient(app)
    challenge, target_position = _captcha(client)
    login = client.post(
        "/api/v2/auth/login",
        json={
            "username": "ops-viewer",
            "password": "HotelOps@2026",
            "captcha_id": challenge["captcha_id"],
            "slider_position": target_position,
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/v2/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["roles"] == ["viewer"]
    assert (
        client.post(
            "/api/v2/ops/tasks",
            headers=headers,
            json={
                "tenant_id": "local",
                "property_id": "hotel-001",
                "objective": "观察员不应拥有创建经营任务权限",
            },
        ).status_code
        == 403
    )

    assert client.post("/api/v2/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/v2/auth/me", headers=headers).status_code == 401
