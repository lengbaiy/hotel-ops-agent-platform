from app.adapters.channel import LocalChannelAdapter
from app.domain import OpsTask, TaskState, recommendation_hash
from app.graph.operations_graph import OperationsGraph
from app.policy import ApprovalPolicy
from app.repositories import InMemoryTaskRepository, TaskRepository


class TaskService:
    """经营任务应用服务，协调 Agent、策略和 Adapter。"""

    def __init__(
        self,
        repository: TaskRepository | None = None,
        operations_graph: OperationsGraph | None = None,
        approval_policy: ApprovalPolicy | None = None,
        channel_adapter: LocalChannelAdapter | None = None,
    ) -> None:
        self.repository = repository or InMemoryTaskRepository()
        self.operations_graph = operations_graph or OperationsGraph()
        self.approval_policy = approval_policy or ApprovalPolicy()
        self.channel_adapter = channel_adapter or LocalChannelAdapter()

    def create(self, task: OpsTask) -> OpsTask:
        task.state = TaskState.ANALYZING
        task.events.append("task_created")
        agent_state = self.operations_graph.run(task)
        if agent_state.approval_status != "WAITING_APPROVAL":
            raise ValueError("high-risk recommendation must require approval")
        task.state = TaskState.WAITING_APPROVAL
        task.events.append("task_waiting_for_human_approval")
        self.repository.add(task)
        return task

    def get(self, task_id: str) -> OpsTask:
        return self.repository.get(task_id)

    def list(self, limit: int = 50, property_id: str | None = None) -> list[OpsTask]:
        return self.repository.list(limit, property_id)

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
        self.approval_policy.validate_execution(task)
        assert task.recommendation is not None
        task.state = TaskState.EXECUTED
        idempotency_key = recommendation_hash(task.recommendation)
        task.events.append(self.channel_adapter.execute(task.recommendation, idempotency_key))
        return task
