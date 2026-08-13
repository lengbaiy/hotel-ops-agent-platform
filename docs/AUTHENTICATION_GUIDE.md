# 身份认证与权限管理

## 登录闭环

平台采用“账号密码 + 一次性 Canvas 拼图滑块 + JWT 会话”的登录闭环。前端使用 MIT 开源组件 [`vue3-slide-verify`](https://github.com/monoplasty/vue3-slide-verify)，组件提供 Canvas 拼图、滑动轨迹判断和成功/失败/异常回调；后端仍是最终裁决者。

1. 前端请求 `POST /api/v2/auth/captcha` 创建一次性滑块挑战。
2. 用户完成滑块并提交 `POST /api/v2/auth/login`。
3. 开源组件完成 Canvas 拼图和行为轨迹检测，成功回调返回实际滑动距离。
4. 服务端校验挑战未过期、未重复使用、滑动距离、账号和密码。
5. 校验成功后签发短期 JWT，前端仅存入浏览器 `sessionStorage`。
6. 每个受保护 API 校验 JWT、角色、租户和酒店范围。
7. `POST /api/v2/auth/logout` 撤销当前 JWT 的 `jti`，令牌立即失效。

## 本地演示账户

| 账号 | 密码 | 角色 | 酒店范围 |
| --- | --- | --- | --- |
| `ops-admin` | `HotelOps@2026` | 查看、运营、审批、执行 | `hotel-001`、`hotel-002` |
| `ops-viewer` | `HotelOps@2026` | 仅查看 | `hotel-001` |

演示账户仅用于本地开发，密码以 PBKDF2 哈希保存。生产环境不得保留演示账户或静态密码。

## 权限模型

| 角色 | 允许操作 |
| --- | --- |
| `viewer` | 查看驾驶舱、任务、事件 |
| `operator` | 创建经营分析或策略任务 |
| `approver` | 审批策略参数快照 |
| `executor` | 执行已审批的受控动作 |

所有业务接口还会验证 JWT 中的 `tenant_id` 与 `property_ids`。客户端提交的租户和酒店参数不能越过令牌范围。

## 生产接入要求

1. 将 `.env` 设置为 `AUTH_MODE=jwt`，并使用至少 32 字节的随机 `JWT_SECRET`。
2. 如使用腾讯云商业验证码，将 `CAPTCHA_PROVIDER=tencent`，并配置 `TENCENT_CAPTCHA_APP_ID`、`TENCENT_SECRET_ID` 与 `TENCENT_SECRET_KEY`。前端加载腾讯云官方 `TCaptcha.js`，服务端使用官方 SDK 校验 `ticket` 和 `randstr`。
3. 将本地 `AuthService` 替换为企业 SSO/OIDC 身份提供方；服务端只接受验证后的签名令牌。
4. 将挑战记录、登录失败次数、令牌撤销表存入 Redis/PostgreSQL；当前内存实现仅用于单进程本地演示。
5. 生产 API 仅使用 HTTPS，配置可信 CORS 域名、审计登录事件、设置速率限制与账户锁定策略。

## 当前安全边界

当前接入的开源 Canvas 组件用于本地 UI 和完整接口闭环验证。拼图偏移量需要传给浏览器渲染 Canvas，因此客户端组件本身不能作为唯一的反自动化防线；后端会校验一次性挑战、过期时间和提交距离，但恶意客户端仍可能模拟协议。

生产仍应采用经过采购、风控和 SLA 验证的验证码服务，并在服务端验证其签名令牌、行为风险评分和设备指纹。开源组件可保留为前端展示层或故障降级方案。
