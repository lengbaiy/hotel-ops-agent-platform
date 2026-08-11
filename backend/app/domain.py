from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskState(StrEnum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"


class TaskCreate(BaseModel):
    tenant_id: str = Field(min_length=1)
    property_id: str = Field(min_length=1)
    objective: str = Field(min_length=5, max_length=500)
    task_type: str = "revenue_recommendation"


class Recommendation(BaseModel):
    action: str
    parameters: dict[str, str | int | float]
    rationale: str
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str]
    requires_approval: bool = True


class OpsTask(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    state: TaskState = TaskState.PENDING
    request: TaskCreate
    recommendation: Recommendation | None = None
    approval_hash: str | None = None
    events: list[str] = Field(default_factory=list)


def recommendation_hash(recommendation: Recommendation) -> str:
    return sha256(recommendation.model_dump_json().encode()).hexdigest()
