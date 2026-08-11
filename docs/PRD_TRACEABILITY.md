# 需求追踪矩阵

| 需求范围 | 后端模块 | 前端模块 | 数据对象 | 验收关键点 |
| --- | --- | --- | --- | --- |
| OP-FR-001 至 004 经营驾驶舱与任务 | `modules/ops` | `modules/ops` | `ops_task`、`ops_step`、`ops_event` | owner、priority、状态、证据、审计 |
| OP-FR-010 至 013 市场情报 | `modules/market_intelligence` | `modules/market-intelligence` | `compset`、`competitor_rate_snapshot` | 来源、快照、匹配置信度 |
| OP-FR-020 至 023 事件与预测 | `modules/demand_forecast` | `modules/demand-forecast` | `market_event`、`demand_forecast` | 120 天、区间、驱动、版本 |
| OP-FR-030 至 033 收益策略 | `modules/revenue_management` | `modules/revenue-management` | `strategy_recommendation` | 净 ADR、硬规则、审批 |
| OP-FR-040 至 043 渠道运营 | `modules/channel_operations` | `modules/channel-operations` | `channel_rate_inventory`、`promotion` | 冲突、幂等、回读 |
| OP-FR-050 至 053 内容增长 | `modules/content_growth` | `modules/content-growth` | `content_asset`、`content_plan`、`publish_record` | 权利、AI 标识、发布审批 |
| OP-FR-060 至 063 口碑会员效率 | `modules/reputation_membership`、`operating_efficiency` | 对应业务模块 | `review_topic`、`audience_segment` | 同意、频控、仅建议 |
| 审批、实验、归因 | `modules/strategy_governance`、`knowledge_measurement` | 策略与复盘视图 | `approval`、`execution`、`measurement` | 参数哈希、观察窗、归因 |

## API 追踪

`/api/v2/ops/tasks` 已实现最小闭环；其他需求文档 API 已注册为明确的 `501` 契约，防止未实现能力被误用于生产。实施模块后，必须同时补充 Schema、应用服务、仓储、Adapter、测试、审计与 Trace。

## 数据建模原则

所有业务对象关联 `tenant_id`、`property_id`、`trace_id`；指标携带口径版本、币种、时区与数据截止时间；策略、审批和执行不可变版本；外部写操作携带 `idempotency_key` 并回读真实状态。
