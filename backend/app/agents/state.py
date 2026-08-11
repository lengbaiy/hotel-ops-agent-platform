from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain import Recommendation


class AgentState(BaseModel):
    """与需求文档 6.2 对齐的跨 Agent 最小状态。"""

    task_id: str
    session_id: str | None = None
    tenant_id: str
    property_id: str
    objective: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    horizon_days: int = Field(default=30, ge=1, le=120)
    data_cutoff: datetime | None = None
    source_versions: dict[str, str] = Field(default_factory=dict)
    metric_context: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    selected_agent: str | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    approval_status: str = "NOT_REQUIRED"
    execution_plan: list[dict[str, Any]] = Field(default_factory=list)
    degraded_flags: list[str] = Field(default_factory=list)
    final_result: dict[str, Any] = Field(default_factory=dict)
