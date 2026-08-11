from app.domain import Recommendation, TaskCreate


class RevenueRecommendationAgent:
    """收益建议的最小实现；后续可替换为 LangGraph 节点。"""

    def recommend(self, task: TaskCreate) -> Recommendation:
        return Recommendation(
            action="adjust_rate",
            parameters={"room_type": "Deluxe King", "suggested_rate": 688},
            rationale=(
                "收益建议待结合 Pickup、库存、渠道成本和活动信号计算；"
                "执行前必须绑定数据截止时间、来源版本和证据。"
            ),
            confidence=0.72,
            evidence_refs=["demo://pickup/2026-08-11", "demo://event/concert-001"],
        )

    name = "revenue_management"
