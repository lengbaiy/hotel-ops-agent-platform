from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_task_service
from app.domain import OpsTask, OpsTaskList, TaskCreate
from app.services import TaskService

router = APIRouter(prefix="/ops/tasks", tags=["经营任务"])
TaskServiceDependency = Annotated[TaskService, Depends(get_task_service)]


@router.post(
    "",
    response_model=OpsTask,
    status_code=status.HTTP_201_CREATED,
    summary="创建经营分析或策略任务",
)
def create_task(payload: TaskCreate, service: TaskServiceDependency) -> OpsTask:
    return service.create(OpsTask(request=payload))


@router.get("", response_model=OpsTaskList, summary="查询经营任务列表")
def list_tasks(
    service: TaskServiceDependency,
    limit: int = Query(default=50, ge=1, le=100),
    property_id: str | None = Query(default=None, min_length=1),
) -> OpsTaskList:
    tasks = service.list(limit, property_id)
    return OpsTaskList(items=tasks, total=len(tasks))


@router.get("/{task_id}", response_model=OpsTask, summary="查询任务状态和结果")
def get_task(task_id: str, service: TaskServiceDependency) -> OpsTask:
    try:
        return service.get(task_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="task not found") from error


@router.get("/{task_id}/events", response_model=list[str], summary="查询任务事件流")
def get_task_events(task_id: str, service: TaskServiceDependency) -> list[str]:
    try:
        return service.get(task_id).events
    except KeyError as error:
        raise HTTPException(status_code=404, detail="task not found") from error


@router.post("/{task_id}/approve", response_model=OpsTask, summary="批准策略参数快照")
def approve_task(task_id: str, service: TaskServiceDependency) -> OpsTask:
    try:
        return service.approve(task_id)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/{task_id}/execute", response_model=OpsTask, summary="执行已批准的受控动作")
def execute_task(task_id: str, service: TaskServiceDependency) -> OpsTask:
    try:
        return service.execute(task_id)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
