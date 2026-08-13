from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(api_v2_router)


@app.middleware("http")
async def request_trace(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/healthz", include_in_schema=False)
def liveness() -> JSONResponse:
    return JSONResponse({"status": "alive"})


@app.get("/readyz", include_in_schema=False)
def readiness() -> JSONResponse:
    if settings.auth_mode not in {"disabled", "jwt"}:
        return JSONResponse({"status": "not_ready"}, status_code=503)
    return JSONResponse({"status": "ready", "environment": settings.environment})
