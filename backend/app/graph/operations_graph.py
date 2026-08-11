from datetime import UTC, datetime
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.base import SpecialistAgent
from app.agents.revenue import RevenueRecommendationAgent
from app.agents.specialist_agent import RuleBasedSpecialistAgent, SpecialistProfile
from app.agents.state import AgentState
from app.agents.supervisor import SupervisorAgent
from app.domain import OpsTask, Recommendation


class GraphContext(TypedDict):
    task: OpsTask
    agent_state: AgentState
    selected_agent: str
    recommendation: Recommendation | None
    events: list[str]


class OperationsGraph:
    """需求文档 6 章定义的受治理 Agent 编排入口。"""

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.agents: dict[str, SpecialistAgent] = {
            "revenue_management": RevenueRecommendationAgent(),
            "market_intelligence": self._specialist(
                "market_intelligence",
                "create_market_evidence",
                "生成同行与事件证据卡片",
                {"horizon_days": 120},
            ),
            "demand_forecast": self._specialist(
                "demand_forecast",
                "generate_demand_forecast",
                "生成需求区间、驱动因子与压缩夜判断",
                {"horizon_days": 120},
            ),
            "channel_operations": self._specialist(
                "channel_operations",
                "recommend_channel_allocation",
                "提出渠道库存与活动冲突处理建议",
                {"review_window_days": 14},
            ),
            "content_growth": self._specialist(
                "content_growth",
                "create_content_plan",
                "生成带素材权利与品牌审核要求的内容计划",
                {"planning_days": 7},
            ),
            "reputation_membership": self._specialist(
                "reputation_membership",
                "create_customer_strategy",
                "生成点评闭环或合规会员策略",
                {"frequency_limit_days": 7},
            ),
            "operating_efficiency": self._specialist(
                "operating_efficiency",
                "recommend_operating_capacity",
                "生成入住、清扫、早餐与前厅负荷建议",
                {"forecast_days": 14},
            ),
        }
        self.graph = self._build_graph()

    def run(self, task: OpsTask) -> AgentState:
        state = AgentState(
            task_id=str(task.id),
            tenant_id=task.request.tenant_id,
            property_id=task.request.property_id,
            objective=task.request.objective,
            data_cutoff=task.request.data_cutoff or datetime.now(UTC),
        )
        result = self.graph.invoke(
            {
                "task": task,
                "agent_state": state,
                "selected_agent": "",
                "recommendation": None,
                "events": [],
            }
        )
        task.recommendation = result["recommendation"]
        task.events.extend(result["events"])
        return result["agent_state"]

    def _build_graph(self):
        workflow = StateGraph(GraphContext)
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("policy_judge", self._policy_node)
        for agent_name in self.agents:
            workflow.add_node(agent_name, self._specialist_node(agent_name))
            workflow.add_edge(agent_name, "policy_judge")
        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges(
            "supervisor", lambda context: context["selected_agent"], list(self.agents)
        )
        workflow.add_edge("policy_judge", END)
        return workflow.compile()

    def _supervisor_node(self, context: GraphContext) -> GraphContext:
        selected_agent = self.supervisor.select(context["task"].request)
        context["agent_state"].selected_agent = selected_agent
        context["events"].append(f"supervisor:routed_to:{selected_agent}")
        context["selected_agent"] = selected_agent
        return context

    def _specialist_node(self, agent_name: str):
        def run_specialist(context: GraphContext) -> GraphContext:
            recommendation = self.agents[agent_name].recommend(context["task"].request)
            context["agent_state"].recommendations.append(recommendation)
            context["agent_state"].evidence_refs.extend(recommendation.evidence_refs)
            context["events"].append(f"agent:{agent_name}:recommendation_generated")
            context["recommendation"] = recommendation
            return context

        return run_specialist

    def _policy_node(self, context: GraphContext) -> GraphContext:
        recommendation = context["recommendation"]
        if recommendation is None:
            raise ValueError("specialist agent did not return a recommendation")
        if recommendation.requires_approval:
            context["agent_state"].approval_status = "WAITING_APPROVAL"
            context["events"].append("policy_judge:approval_required")
        return context

    @staticmethod
    def _specialist(
        name: str, action: str, rationale: str, parameters: dict[str, str | int | float]
    ) -> RuleBasedSpecialistAgent:
        return RuleBasedSpecialistAgent(SpecialistProfile(name, action, rationale, parameters))
