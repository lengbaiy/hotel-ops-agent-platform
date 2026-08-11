# 三端统一架构

本项目采用“统一领域契约 + 统一 API + 差异化体验层”的实现方式，避免将 PC 页面强行缩小到移动端。

| 终端 | 工程 | 技术 | 主要场景 |
| --- | --- | --- | --- |
| PC 运营中台 | `frontend/` | Vue 3 + Vite | 驾驶舱、策略配置、审批、复盘、系统管理 |
| 移动 H5 | `clients/mobile-ops/` | UniApp + Vue 3 | 告警处理、任务协同、快速审批、晨会查看 |
| 微信小程序 | `clients/mobile-ops/` | UniApp 编译至 `mp-weixin` | 轻量任务、消息触达、门店执行反馈 |

## 一套实现的边界

1. 后端仅维护一套版本化 `/api/v2` 服务、认证、权限、审计与领域规则。
2. `packages/shared-contracts` 存放三端复用的领域类型、请求/响应契约。
3. `packages/shared-api` 存放无 UI 依赖的 HTTP、认证、错误与 Trace 客户端。
4. PC 与移动端各自维护布局、导航和交互，避免响应式压缩破坏复杂运营体验。
5. 需要原生能力时，小程序/H5 通过 UniApp 适配层调用；领域规则仍不得下沉到客户端。

## 启动命令

```bash
# PC 中台
cd frontend && npm run dev

# 移动 H5
cd clients/mobile-ops && npm install && npm run dev:h5

# 微信小程序（安装依赖后导入微信开发者工具）
cd clients/mobile-ops && npm run dev:mp-weixin
```
