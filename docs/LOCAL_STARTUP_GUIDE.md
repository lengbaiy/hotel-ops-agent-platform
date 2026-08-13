# 本地项目启动手册

本手册用于不使用 Docker 的本地开发与演示。当前项目已启动在以下地址：

| 服务 | 地址 |
| --- | --- |
| PC 运营平台 | `http://127.0.0.1:5179` |
| FastAPI 文档 | `http://127.0.0.1:8006/docs` |
| 前端代理 API 文档 | `http://127.0.0.1:5179/docs` |

本次使用 `5179` 和 `8006`，以避免占用其他项目正在使用的 `5173` 和 `8000`。

## 前置条件

- Python 3.11 或更高版本。
- Node.js 20 或更高版本。
- 已在 `backend/` 安装后端依赖，在 `frontend/` 安装前端依赖。

## 手工启动

打开两个 PowerShell 窗口，在项目根目录 `C:\Users\33793\Desktop\酒店项目` 分别执行。

### 启动 API

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8006 --reload
```

### 启动前端

```powershell
cd frontend
$env:VITE_API_PROXY_TARGET = "http://127.0.0.1:8006"
npm run dev -- --host 127.0.0.1 --port 5179
```

前端会把 `/api`、`/docs`、`/redoc` 和 `/openapi.json` 请求代理到 API 服务，因此浏览器可从 `http://127.0.0.1:5179` 直接访问平台与接口文档。

## 验收命令

```powershell
Invoke-WebRequest http://127.0.0.1:5179
Invoke-WebRequest http://127.0.0.1:8006/docs
```

创建市场情报任务后，响应状态应为 `WAITING_APPROVAL`，事件中应包含：

```text
supervisor:routed_to:market_intelligence
agent:market_intelligence:recommendation_generated
policy_judge:approval_required
```

## 日志与停止

通过 `scripts/Start-Local.ps1` 启动的日志保存在 `work/`。手工启动时日志直接输出在各自 PowerShell 窗口。

查找端口进程：

```powershell
Get-NetTCPConnection -LocalPort 5179,8006 -State Listen |
  Select-Object LocalPort, OwningProcess
```

确认进程归属后停止：

```powershell
Stop-Process -Id <进程ID>
```

不要停止不属于本项目的端口进程。若 `5179` 或 `8006` 已被占用，可替换为其他空闲端口，但前端的 `VITE_API_PROXY_TARGET` 必须与 API 端口一致。

