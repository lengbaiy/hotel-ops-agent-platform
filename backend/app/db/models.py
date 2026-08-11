from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditRecord(Base):
    """所有领域表共享的租户、门店、追踪与审计字段。"""

    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    property_id: Mapped[str] = mapped_column(String(64), index=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OpsTaskRecord(AuditRecord):
    __tablename__ = "ops_task"

    state: Mapped[str] = mapped_column(String(32), index=True)
    objective: Mapped[str] = mapped_column(Text)
    task_type: Mapped[str] = mapped_column(String(64), index=True)
    state_version: Mapped[int] = mapped_column(default=1)


class ApprovalRecord(AuditRecord):
    __tablename__ = "approval"

    task_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    parameter_hash: Mapped[str] = mapped_column(String(64))
    approver_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class ExecutionRecord(AuditRecord):
    __tablename__ = "execution"

    task_id: Mapped[str] = mapped_column(String(36), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True)
    external_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    readback_status: Mapped[str] = mapped_column(String(32))
