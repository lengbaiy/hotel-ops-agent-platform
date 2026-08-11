from app.domain import Recommendation


class LocalChannelAdapter:
    """本地环境执行器；生产实现必须替换为已授权平台的受控 Adapter。"""

    def execute(self, recommendation: Recommendation, idempotency_key: str) -> str:
        if not idempotency_key:
            raise ValueError("idempotency key is required")
        return f"local_channel_readback:{recommendation.action}"
