from typing import Any

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    tenant_id: str
    property_id: str
    trace_id: str
    data_cutoff: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    source_versions: dict[str, str] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)
    data: dict[str, Any] = Field(default_factory=dict)
    degraded: bool = False
