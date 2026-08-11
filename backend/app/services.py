from app.domain import OpsTask, Recommendation, TaskState, recommendation_hash


class TaskService:
    """In-memory teaching implementation; replace with repository + PostgreSQL in M1."""

    def __init__(self) -> None:
        self.tasks: dict[str, OpsTask] = {}

    def create(self, task: OpsTask) -> OpsTask:
        task.state = TaskState.ANALYZING
        task.events.append("task_created")
        task.recommendation = Recommendation(
            action="adjust_rate",
            parameters={"room_type": "Deluxe King", "suggested_rate": 688},
            rationale="模拟 Pickup 增长与活动信号；真实实现须绑定数据截止时间和证据。",
            confidence=0.72,
            evidence_refs=["demo://pickup/2026-08-11", "demo://event/concert-001"],
        )
        task.state = TaskState.WAITING_APPROVAL
        task.events.append("recommendation_generated_waiting_approval")
        self.tasks[str(task.id)] = task
        return task

    def get(self, task_id: str) -> OpsTask:
        return self.tasks[task_id]

    def approve(self, task_id: str) -> OpsTask:
        task = self.get(task_id)
        if task.state != TaskState.WAITING_APPROVAL or task.recommendation is None:
            raise ValueError("task is not waiting for approval")
        task.approval_hash = recommendation_hash(task.recommendation)
        task.state = TaskState.APPROVED
        task.events.append("approval_granted")
        return task

    def execute(self, task_id: str) -> OpsTask:
        task = self.get(task_id)
        if task.state != TaskState.APPROVED or task.recommendation is None:
            raise ValueError("approved task required")
        if task.approval_hash != recommendation_hash(task.recommendation):
            raise ValueError("recommendation changed after approval")
        task.state = TaskState.EXECUTED
        task.events.append("mock_channel_adapter_readback_success")
        return task
