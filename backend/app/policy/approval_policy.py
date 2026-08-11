from app.domain import OpsTask, TaskState, recommendation_hash


class ApprovalPolicy:
    """策略执行的最小安全边界。"""

    def validate_execution(self, task: OpsTask) -> None:
        if task.state != TaskState.APPROVED or task.recommendation is None:
            raise ValueError("approved task required")
        if task.approval_hash != recommendation_hash(task.recommendation):
            raise ValueError("recommendation changed after approval")
