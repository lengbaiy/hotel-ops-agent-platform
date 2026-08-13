# Docker 启动与运维手册

本项目通过 Docker Compose 启动完整平台，不要求在宿主机安装 Python、Node.js、PostgreSQL、Redis、Qdrant 或 MinIO。

## 1. 服务清单

| 服务 | 容器职责 | 宿主机端口 |
| --- | --- | --- |
| `web` | Vue PC 运营管理端 | `5173` |
| `api` | FastAPI、任务、审批和 Agent API | `8000` |
| `agent-worker` | Agent 异步任务 Worker | 无 |
| `scheduler` | 定时调度任务 | 无 |
| `db` | PostgreSQL 16 业务数据库 | `5432` |
| `redis` | 缓存与异步任务基础设施 | `6379` |
| `qdrant` | 向量检索服务 | `6333` |
| `minio` | 对象存储及控制台 | `9000`、`9001` |

## 2. 前置条件

1. Windows 10/11 已启用虚拟化。
2. 已安装并启动 Docker Desktop（推荐 WSL 2 后端）。
3. Docker Desktop 状态为 Running，且 PowerShell 可执行以下命令：

```powershell
docker --version
docker compose version
```

若未安装 Docker Desktop，可使用 Windows 包管理器安装：

```powershell
winget install -e --id Docker.DockerDesktop
```

安装后重启 Windows，启动 Docker Desktop，接受其 WSL 2 初始化提示；确认 `docker --version` 有版本输出后再继续。

## 3. 首次启动

在项目根目录 `C:\Users\33793\Desktop\酒店项目` 执行：

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

首次构建会下载基础镜像和依赖，耗时取决于网络。随后检查全部服务：

```powershell
docker compose ps
docker compose logs --tail=100
```

正常情况下，`web`、`api`、`db`、`redis`、`qdrant` 与 `minio` 均应处于运行状态。`api` 只有在 PostgreSQL 与 Redis 健康后才会启动，`web` 只有在 API 健康后才会启动。

`agent-worker` 与 `scheduler` 是预留的后台进程配置，待 Redis 队列、LangGraph Checkpoint 与定时任务落地后启用；当前 Agent 任务由 API 同步编排。不要把占位进程误认为生产异步任务能力。

## 4. 访问地址

| 功能 | 地址 |
| --- | --- |
| 运营平台 | `http://localhost:5173` |
| Swagger API 文档 | `http://localhost:8000/docs` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| MinIO 控制台 | `http://localhost:9001` |
| Qdrant 健康检查 | `http://localhost:6333/healthz` |

本地演示环境的 MinIO 用户名与密码均为 `minioadmin`。生产环境必须通过密钥服务覆盖默认值，且不得使用示例密码。

## 5. 日常运维命令

```powershell
# 后台启动（镜像已构建时）
docker compose up -d

# 查看容器状态
docker compose ps

# 跟踪全部日志
docker compose logs -f

# 只跟踪 API 或前端日志
docker compose logs -f api
docker compose logs -f web

# 仅重建并重启前端或 API
docker compose up --build -d web
docker compose up --build -d api

# 停止并保留数据库、向量库和对象存储数据
docker compose down

# 停止并删除所有本地容器数据（不可恢复）
docker compose down -v
```

## 6. 配置说明

首次启动生成的 `.env` 是本机环境配置，不应提交到 Git。可按需调整：

- `POSTGRES_PASSWORD`：本地数据库密码。
- `DATABASE_URL`：API、Worker 与 Scheduler 使用的数据库连接。
- `REDIS_URL`、`QDRANT_URL`、`MINIO_ENDPOINT`：容器网络内服务地址。

不要将生产数据库地址、真实第三方密钥、Cookie 或未脱敏数据填入仓库中的 `.env.example`。

## 7. 验收检查

```powershell
# 平台首页
Invoke-WebRequest http://localhost:5173

# API 文档
Invoke-WebRequest http://localhost:8000/docs

# 查看 API 健康及启动错误
docker compose logs --tail=200 api
```

创建经营任务后，应在响应事件中看到 `supervisor:routed_to:<专项-agent>`、`agent:<专项-agent>:recommendation_generated` 和 `policy_judge:approval_required`；任务状态应为 `WAITING_APPROVAL`。

## 8. 常见问题

### `docker` 不是内部或外部命令

Docker Desktop 未安装或未启动。安装后重新打开 PowerShell；若仍无效，重启 Windows 并确认 Docker Desktop 正在运行。

### 端口被占用

先检查端口占用：

```powershell
Get-NetTCPConnection -LocalPort 5173,8000,5432,6379,6333,9000,9001 -ErrorAction SilentlyContinue
```

停止冲突程序，或在 `docker-compose.yml` 中调整宿主机端口后重新执行 `docker compose up -d`。

### 容器启动后退出

按服务查看日志定位：

```powershell
docker compose logs api
docker compose logs agent-worker
docker compose logs db
```

若是首次构建失败，执行 `docker compose build --no-cache` 后再启动；不要使用 `docker compose down -v`，除非确认可以清空所有本地数据。
