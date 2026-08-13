from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_dashboard_service, get_task_service
from app.api.security import Actor, require_roles
from app.domain import TaskState
from app.schemas.dashboard import DashboardOverview
from app.services import DashboardService, TaskService

router = APIRouter(prefix="/dashboard", tags=["经营驾驶舱"])
DashboardServiceDependency = Annotated[DashboardService, Depends(get_dashboard_service)]
TaskServiceDependency = Annotated[TaskService, Depends(get_task_service)]


@router.get("/overview", response_model=DashboardOverview, summary="查询经营驾驶舱概览")
def get_overview(
    service: DashboardServiceDependency,
    task_service: TaskServiceDependency,
    actor: Annotated[Actor, Depends(require_roles("viewer", "operator", "approver", "executor"))],
    property_id: str = Query(default="hotel-001", min_length=1),
) -> DashboardOverview:
    if not actor.can_access_property(property_id):
        raise HTTPException(status_code=403, detail="property scope denied")
    pending_approval_count = sum(
        task.state == TaskState.WAITING_APPROVAL
        for task in task_service.list(limit=100, property_id=property_id)
        if actor.tenant_id is None or task.request.tenant_id == actor.tenant_id
    )
    return service.overview(property_id, pending_approval_count)
