from datetime import UTC, datetime

from app.schemas.dashboard import DashboardOverview, MetricCard, OperatingAlert


class DashboardService:
    """经营概览应用服务；M1 接入统一指标语义层后替换数据提供器。"""

    def overview(self, property_id: str, pending_approval_count: int) -> DashboardOverview:
        now = datetime.now(UTC)
        return DashboardOverview(
            property_id=property_id,
            data_cutoff=now,
            metrics=[
                MetricCard(
                    code="occ",
                    label="入住率 OCC",
                    value=72.4,
                    display_value="72.4%",
                    change_display="较昨日 +3.1%",
                    trend="up",
                ),
                MetricCard(
                    code="adr",
                    label="平均房价 ADR",
                    value=538,
                    display_value="¥538",
                    change_display="较预算 +¥18",
                    trend="up",
                ),
                MetricCard(
                    code="revpar",
                    label="单房收益 RevPAR",
                    value=390,
                    display_value="¥390",
                    change_display="较去年 +6.8%",
                    trend="up",
                ),
                MetricCard(
                    code="pickup",
                    label="未来 7 天 Pickup",
                    value=18,
                    display_value="+18 间夜",
                    change_display="较同提前量 +5",
                    trend="up",
                ),
            ],
            alerts=[
                OperatingAlert(
                    severity="high",
                    title="周六压缩夜需复核价格梯度",
                    description="预计入住率超过 89%，建议完成房型梯度与限制条件审批。",
                    module="收益管理",
                    occurred_at=now,
                ),
                OperatingAlert(
                    severity="medium",
                    title="渠道价盘存在待核验差异",
                    description="已发现 2 个房型的渠道净 ADR 口径需要重新校验。",
                    module="渠道运营",
                    occurred_at=now,
                ),
            ],
            pending_approval_count=pending_approval_count,
        )
