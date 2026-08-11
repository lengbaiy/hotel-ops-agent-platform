from app.domain import TaskCreate


class SupervisorAgent:
    """仅负责路由与汇总，禁止直接访问连接器或执行写操作。"""

    task_type_routes = {
        "revenue_recommendation": "revenue_management",
        "market_intelligence": "market_intelligence",
        "demand_forecast": "demand_forecast",
        "channel_recommendation": "channel_operations",
        "content_plan": "content_growth",
        "reputation_response": "reputation_membership",
        "membership_strategy": "reputation_membership",
        "efficiency_recommendation": "operating_efficiency",
    }

    def select(self, task: TaskCreate) -> str:
        try:
            return self.task_type_routes[task.task_type]
        except KeyError as error:
            raise ValueError(f"unsupported task type: {task.task_type}") from error
