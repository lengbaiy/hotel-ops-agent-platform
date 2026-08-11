# 酒店智能运营 Agent 平台

本仓库依据《酒店智能运营 Agent 平台项目需求规格说明书 V2.0》搭建，提供可运行的最小业务闭环，支持团队按 Issue 和分支迭代真实业务能力，而不是直接接入生产 OTA 或自动执行写操作。

## 已包含的最小闭环

`创建运营任务 -> 生成结构化建议 -> 等待人工审批 -> 受控执行模拟动作 -> 审计留痕`

- Web：Vue 3、TypeScript、Vite、Pinia、ECharts
- API：FastAPI、Pydantic、SQLAlchemy
- 运行依赖：PostgreSQL、Redis、Qdrant、MinIO（Docker Compose）
- 安全基线：所有写操作须经审批；执行参数和审批快照的 SHA-256 必须一致；模拟 Adapter 代替真实外部系统。

## 快速开始

### Docker（推荐演示环境）

```bash
cp .env.example .env
docker compose up --build
```

打开 `http://localhost:5173`，API 文档为 `http://localhost:8000/docs`。

### 本地开发

```bash
# 后端（Python 3.11+）
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# 前端（Node 20+）
cd frontend
npm install
npm run dev
```

## 实施路径

1. **M1 数据与指标**：实现 `property_metric_daily`、Pickup 快照及指标口径版本。
2. **M2 市场与事件**：替换模拟的 Rate Shop / Event Adapter，保留来源和置信度。
3. **M3 策略主链路**：实现 LangGraph 节点、规则引擎、审批与执行回读。
4. **M4 内容与口碑**：增加素材权利、AI 标识、审核和平台授权发布。
5. **M5 评测与试点**：补充固定评测集、故障注入、Trace 与验收报告。

每个 Issue 应聚焦单一纵向能力；不得绕开审批、策略治理和 Adapter 边界直接调用任何外部写操作。

## GitHub 协作

首次在 GitHub 创建空仓库后执行：

```bash
git remote add origin https://github.com/<组织>/<仓库>.git
git branch -M main
git push -u origin main
```

团队开发流程详见 [docs/GITHUB_WORKFLOW.md](docs/GITHUB_WORKFLOW.md)。CI 会在 Pull Request 上运行后端测试、静态检查、格式检查与前端构建。

## 目录

```text
backend/     FastAPI、领域服务、Agent/Tool 契约、测试
frontend/    Vue 驾驶舱与任务中心
docs/        总体架构、协作规范与 GitHub 规则
data/        脱敏样例和导入说明
docker/      本地容器配置
.github/     PR 模板与 CI
```
