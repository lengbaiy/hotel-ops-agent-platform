from typing import Protocol

from app.domain import OpsTask


class TaskRepository(Protocol):
    def add(self, task: OpsTask) -> None: ...

    def get(self, task_id: str) -> OpsTask: ...

    def list(self, limit: int, property_id: str | None = None) -> list[OpsTask]: ...


class InMemoryTaskRepository:
    """开发环境实现；M1 替换为 SQLAlchemy/PostgreSQL 仓储。"""

    def __init__(self) -> None:
        self.tasks: dict[str, OpsTask] = {}

    def add(self, task: OpsTask) -> None:
        self.tasks[str(task.id)] = task

    def get(self, task_id: str) -> OpsTask:
        return self.tasks[task_id]

    def list(self, limit: int, property_id: str | None = None) -> list[OpsTask]:
        tasks = sorted(self.tasks.values(), key=lambda task: task.created_at, reverse=True)
        if property_id:
            tasks = [task for task in tasks if task.request.property_id == property_id]
        return tasks[:limit]
