from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import randbelow, token_urlsafe
from typing import Any

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
        if settings.captcha_provider == "tencent":
            if not settings.tencent_captcha_app_id:
                raise ValueError("腾讯云验证码未配置 TENCENT_CAPTCHA_APP_ID")
            captcha_id = token_urlsafe(24)
            self.captchas[captcha_id] = (
                0,
                datetime.now(UTC) + timedelta(seconds=settings.captcha_expire_seconds),
            )
            return {
                "provider": "tencent",
                "captcha_id": captcha_id,
                "app_id": settings.tencent_captcha_app_id,
                "expires_in": settings.captcha_expire_seconds,
            }
        if settings.captcha_provider != "local_puzzle":
            raise ValueError("CAPTCHA_PROVIDER must be local_puzzle or tencent")
        captcha_id = token_urlsafe(24)
        target_position = 68 + randbelow(210)
        self.captchas[captcha_id] = (
            target_position,
            datetime.now(UTC) + timedelta(seconds=settings.captcha_expire_seconds),
        )
        return {
            "provider": "local_puzzle",
            "captcha_id": captcha_id,
            "track_length": 100,
            "canvas_width": 350,
            "canvas_height": 150,
            "puzzle_offset": target_position,
            "expires_in": settings.captcha_expire_seconds,
        }

    def login(self, payload: dict[str, Any]) -> dict[str, object]:
        self._validate_captcha(payload)
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

    def _validate_captcha(self, payload: dict[str, Any]) -> None:
        captcha_id = str(payload["captcha_id"])
        challenge = self.captchas.pop(captcha_id, None)
        if challenge is None:
            raise ValueError("滑块挑战不存在或已使用")
        target_position, expires_at = challenge
        if datetime.now(UTC) > expires_at:
            raise ValueError("滑块挑战已过期")
        if settings.captcha_provider == "tencent":
            self._validate_tencent_captcha(
                str(payload.get("captcha_ticket") or ""), str(payload.get("captcha_randstr") or "")
            )
            return
        slider_position = payload.get("slider_position")
        if not isinstance(slider_position, int):
            raise ValueError("缺少滑块验证位置")
        if abs(slider_position - target_position) > 4:
            raise ValueError("滑块验证失败")

    @staticmethod
    def _validate_tencent_captcha(ticket: str, randstr: str) -> None:
        if not ticket or not randstr:
            raise ValueError("缺少腾讯云验证码凭据")
        if not settings.tencent_secret_id or not settings.tencent_secret_key:
            raise ValueError("腾讯云验证码服务端密钥未配置")
        try:
            from tencentcloud.captcha.v20190722 import captcha_client, models
            from tencentcloud.common import credential
        except ImportError as error:
            raise ValueError("腾讯云验证码 SDK 不可用") from error
        client = captcha_client.CaptchaClient(
            credential.Credential(settings.tencent_secret_id, settings.tencent_secret_key),
            "ap-guangzhou",
        )
        request = models.DescribeCaptchaResultRequest()
        request.CaptchaType = 9
        request.Ticket = ticket
        request.UserIp = "127.0.0.1"
        request.Randstr = randstr
        result = client.DescribeCaptchaResult(request).CaptchaCode
        if result != 1:
            raise ValueError("腾讯云验证码校验失败")

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
