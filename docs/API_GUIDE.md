# API 开发与文档规范

## 文档入口

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`

API 文档由 FastAPI 根据路由、Pydantic Schema、标签、摘要和描述自动生成。接口实现完成后无需手工维护另一份 Swagger 文档，但必须在代码中完整维护接口契约。

## 新增接口流程

1. 在对应业务域创建 `api`、`application`、`schemas`、`tests`。
2. 使用 `/api/v2` 下的领域路由；不得在 `main.py` 直接堆叠业务接口。
3. 为每个接口提供 `summary`、`response_model`、状态码和错误响应。
4. 请求与响应必须使用 Pydantic Schema，禁止裸 `dict` 作为对外契约。
5. 写接口必须记录 `trace_id`，经过策略校验、审批、幂等和回读。
6. 为正常、权限拒绝、参数异常、审批拒绝和外部回读失败增加测试。
7. 执行 `scripts/Export-OpenAPI.ps1`，将 `docs/openapi.json` 随 Pull Request 一并更新。

## 版本与兼容性

- 破坏性变更创建 `/api/v3`，不在同一版本中删除已发布字段。
- 字段废弃需先标记、发布迁移期和替代字段，再在下一主版本移除。
- 指标响应必须返回数据截止时间、口径版本、来源版本、币种与时区。
- 受控执行响应必须返回审批状态、执行令牌状态、幂等键和回读结果。

## 路由目录

| 路由 | 领域 | 当前状态 |
| --- | --- | --- |
| `/api/v2/dashboard/*` | 经营驾驶舱 | 已提供概览契约 |
| `/api/v2/ops/tasks/*` | 经营任务 | 已提供创建、查询、事件、审批、执行主链路 |
| `/api/v2/market/*` | 市场情报 | 契约已注册，待接入数据源 |
| `/api/v2/forecast/*` | 需求预测 | 契约已注册，待接入模型与回测 |
| `/api/v2/revenue/*` | 收益管理 | 契约已注册，待接入策略引擎 |
| `/api/v2/approvals`、`/executions` | 策略治理 | 契约已注册，待接入审批矩阵与执行令牌 |
| `/api/v2/content/*` | 内容增长 | 契约已注册，待接入素材与授权发布 |
| `/api/v2/knowledge/*` | 运营知识 | 契约已注册，待接入 RAG 与引用 |
