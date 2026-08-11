# 总体架构

平台采用“经营入口 - 任务编排 - 策略治理 - 业务能力 - 数据资产”的分层架构。Agent 负责感知、分析、规划与解释；所有确定性写操作只能经过策略治理、人工审批和受控 Workflow。

```mermaid
flowchart TB
  subgraph Experience[经营入口层]
    WEB[Web 驾驶舱与任务中心]
    API[OpenAPI / SSE]
  end
  subgraph Orchestration[任务与智能编排层]
    TASK[Ops Task 状态机]
    GRAPH[LangGraph Agent Worker]
    AGENTS[市场 / 收益 / 渠道 / 内容 / 口碑 / 会员 Agent]
  end
  subgraph Governance[策略治理层]
    POLICY[Policy Judge]
    APPROVAL[审批矩阵与令牌]
    EXPERIMENT[实验、归因与复盘]
  end
  subgraph Capabilities[业务能力与连接器层]
    READ[只读 Tool]
    WRITE[受控写 Workflow]
    ADAPTER[Adapter: PMS / CRS / OTA / CRM / 内容平台]
  end
  subgraph Data[数据与平台层]
    PG[(PostgreSQL)]
    REDIS[(Redis)]
    QDRANT[(Qdrant)]
    MINIO[(MinIO / S3)]
    OBS[OpenTelemetry / 日志 / 指标 / Trace]
  end
  WEB --> API --> TASK --> GRAPH --> AGENTS
  AGENTS --> READ --> ADAPTER
  AGENTS --> POLICY
  POLICY --> APPROVAL --> WRITE --> ADAPTER
  TASK --> EXPERIMENT
  TASK --> PG
  GRAPH --> REDIS
  AGENTS --> QDRANT
  READ --> MINIO
  TASK --> OBS
  WRITE --> OBS
```

## 服务职责

| 服务 | 主要职责 | 禁止事项 |
| --- | --- | --- |
| `frontend` | 驾驶舱、任务、审批与结果展示 | 直接调用外部业务平台 |
| `api` | 身份权限、任务、审批、查询 API | 由模型驱动直接写业务系统 |
| `agent-worker` | Agent 编排、结构化建议、Tool 选择 | 绕过 Policy Judge 或审批 |
| `scheduler` | 晨报、监控、复盘和重试调度 | 对未审批策略自动执行 |
| `adapter` | 屏蔽 PMS/OTA/内容平台差异 | 保存平台密钥到日志或 Prompt |
| `evaluation` | 固定评测、回归与质量报告 | 用未脱敏生产数据作为测试集 |

## 核心状态流转

```mermaid
stateDiagram-v2
  [*] --> PENDING
  PENDING --> ANALYZING
  ANALYZING --> WAITING_APPROVAL: 产生高风险建议
  ANALYZING --> COMPLETED: 只读分析完成
  WAITING_APPROVAL --> APPROVED: 参数快照哈希锁定
  WAITING_APPROVAL --> REJECTED
  APPROVED --> EXECUTING: 验证审批令牌与幂等键
  EXECUTING --> EXECUTED: 外部回读一致
  EXECUTING --> RECOVERY: 超时或回读不一致
  RECOVERY --> EXECUTING
  RECOVERY --> FAILED
  EXECUTED --> MEASURING
  MEASURING --> COMPLETED
```

## 部署拓扑

开发环境使用 `Docker Compose` 运行 Web、API、PostgreSQL、Redis、Qdrant 和 MinIO。生产环境将 API、Worker、Scheduler 和 Adapter 分别横向扩展；数据库、对象存储、密钥管理、监控和备份采用托管或高可用服务。外部平台仅通过已授权的 Adapter 访问。
