from fastapi import FastAPI, HTTPException

from app.domain import OpsTask, TaskCreate
from app.services import TaskService

app = FastAPI(title="Hotel Operations Intelligence Agent API", version="0.1.0")
service = TaskService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v2/ops/tasks", response_model=OpsTask, status_code=201)
def create_task(payload: TaskCreate) -> OpsTask:
    return service.create(OpsTask(request=payload))


@app.get("/api/v2/ops/tasks/{task_id}", response_model=OpsTask)
def get_task(task_id: str) -> OpsTask:
    try:
        return service.get(task_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="task not found") from error


@app.post("/api/v2/ops/tasks/{task_id}/approve", response_model=OpsTask)
def approve_task(task_id: str) -> OpsTask:
    try:
        return service.approve(task_id)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/api/v2/ops/tasks/{task_id}/execute", response_model=OpsTask)
def execute_task(task_id: str) -> OpsTask:
    try:
        return service.execute(task_id)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
