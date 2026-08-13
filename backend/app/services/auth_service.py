from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import randbelow, token_urlsafe

import jwt

from app.api.security import Actor
from app.core import settings


class AuthService:
    """本地认证实现；生产环境应由 SSO/OIDC 用户目录替换。"""

    _salt = b"hotel-ops-local-auth-v1"
    _users = {
        "ops-admin": {
            "password_hash": "91d48cb75ca3981336fb695406b6ac492526fd41200a9f13c63266014afe9e5c",
            "display_name": "运营管理员",
            "tenant_id": "local",
            "property_ids": ["hotel-001", "hotel-002"],
            "roles": ["viewer", "operator", "approver", "executor"],
        },
        "ops-viewer": {
            "password_hash": "91d48cb75ca3981336fb695406b6ac492526fd41200a9f13c63266014afe9e5c",
            "display_name": "运营观察员",
            "tenant_id": "local",
            "property_ids": ["hotel-001"],
            "roles": ["viewer"],
        },
    }

    def __init__(self) -> None:
        self.captchas: dict[str, tuple[int, datetime]] = {}

    def create_captcha(self) -> dict[str, int | str]:
        captcha_id = token_urlsafe(24)
        target_position = 68 + randbelow(210)
        self.captchas[captcha_id] = (
            target_position,
            datetime.now(UTC) + timedelta(seconds=settings.captcha_expire_seconds),
        )
        return {
            "captcha_id": captcha_id,
            "track_length": 100,
            "canvas_width": 350,
            "canvas_height": 150,
            "puzzle_offset": target_position,
            "expires_in": settings.captcha_expire_seconds,
        }

    def login(self, payload: dict[str, str | int]) -> dict[str, object]:
        self._validate_captcha(str(payload["captcha_id"]), int(payload["slider_position"]))
        username = str(payload["username"])
        user = self._users.get(username)
        if user is None or not self._verify_password(
            str(payload["password"]), user["password_hash"]
        ):
            raise ValueError("用户名、密码或滑块验证错误")
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
        claims = {
            "sub": username,
            "jti": token_urlsafe(18),
            "aud": settings.jwt_audience,
            "tenant_id": user["tenant_id"],
            "property_ids": user["property_ids"],
            "roles": user["roles"],
            "exp": expires_at,
        }
        token = jwt.encode(claims, settings.jwt_secret, algorithm="HS256")
        return {
            "access_token": token,
            "expires_in": settings.jwt_expire_minutes * 60,
            "user": self._profile(username, user),
        }

    def profile_for(self, actor: Actor) -> dict[str, object]:
        user = self._users.get(actor.subject)
        if user is None:
            return {
                "username": actor.subject,
                "display_name": actor.subject,
                "tenant_id": actor.tenant_id or "local",
                "property_ids": sorted(actor.property_ids),
                "roles": sorted(actor.roles),
            }
        return self._profile(actor.subject, user)

    def _validate_captcha(self, captcha_id: str, slider_position: int) -> None:
        challenge = self.captchas.pop(captcha_id, None)
        if challenge is None:
            raise ValueError("滑块挑战不存在或已使用")
        target_position, expires_at = challenge
        if datetime.now(UTC) > expires_at:
            raise ValueError("滑块挑战已过期")
        if abs(slider_position - target_position) > 4:
            raise ValueError("滑块验证失败")

    def _verify_password(self, password: str, expected_hash: str) -> bool:
        password_hash = pbkdf2_hmac("sha256", password.encode(), self._salt, 310_000).hex()
        return compare_digest(password_hash, expected_hash)

    @staticmethod
    def _profile(username: str, user: dict[str, object]) -> dict[str, object]:
        return {
            "username": username,
            "display_name": user["display_name"],
            "tenant_id": user["tenant_id"],
            "property_ids": user["property_ids"],
            "roles": user["roles"],
        }
