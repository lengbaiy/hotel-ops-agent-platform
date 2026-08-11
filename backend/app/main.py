from fastapi import FastAPI

from app.api.v2 import api_v2_router
from app.core import settings

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description=(
        "酒店智能运营 Agent 平台 API。所有写操作遵循策略可解释、执行可审批、"
        "结果可归因、失败可恢复的治理原则。"
    ),
    openapi_tags=[
        {"name": "经营驾驶舱", "description": "经营概览、指标和告警。"},
        {"name": "经营任务", "description": "任务状态流转、审批和受控执行。"},
        {"name": "platform", "description": "平台能力和模块契约。"},
    ],
)
app.include_router(api_v2_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
