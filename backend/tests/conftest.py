from dataclasses import replace

import pytest

from app.api import security
from app.core import config


@pytest.fixture(autouse=True)
def local_auth_mode(monkeypatch):
    """业务流程测试默认使用本地开发权限；认证测试自行切换到 JWT 模式。"""
    local_settings = replace(config.settings, auth_mode="disabled")
    monkeypatch.setattr(config, "settings", local_settings)
    monkeypatch.setattr(security, "settings", local_settings)
    security.revoked_token_ids.clear()
