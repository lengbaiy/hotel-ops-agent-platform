# 腾讯云商业滑块验证码配置

平台已提供腾讯云验证码的前后端适配：前端加载腾讯云官方 `TCaptcha.js`，后端使用 `tencentcloud-sdk-python` 调用 `DescribeCaptchaResult` 校验官方返回的 `ticket` 与 `randstr`。账号密码和 JWT 会话只有在验证码服务端验证成功后才会继续执行。

## 1. 获取凭据

1. 在腾讯云验证码控制台创建业务应用并选择滑块验证。
2. 获取验证码应用 ID、腾讯云 API 密钥 ID 和密钥 Key。
3. 为 API 密钥授予最小权限，仅允许验证码结果查询；不要使用主账号密钥。

## 2. 配置环境变量

复制 `.env.example` 为 `.env`，填写以下配置：

```dotenv
AUTH_MODE=jwt
JWT_SECRET=<至少32字节的随机密钥>
JWT_AUDIENCE=hotel-ops-api

CAPTCHA_PROVIDER=tencent
TENCENT_CAPTCHA_APP_ID=<腾讯云验证码应用ID>
TENCENT_SECRET_ID=<腾讯云API密钥ID>
TENCENT_SECRET_KEY=<腾讯云API密钥Key>
```

重启 API 和前端后，登录页会显示“启动腾讯云滑块验证”。点击后由腾讯云官方组件展示验证窗口；成功返回的票据会提交给服务端复核。

## 3. 本地开发模式

没有商业凭据时使用：

```dotenv
CAPTCHA_PROVIDER=local_puzzle
```

该模式使用开源 `vue3-slide-verify` Canvas 拼图组件与本地一次性挑战，适合功能开发和接口联调，不等价于商业风控服务。

## 4. 验收清单

1. 未完成腾讯云滑块时，登录按钮不可用。
2. 滑块成功后，前端收到 `ticket` 与 `randstr`。
3. 服务端未配置 API 密钥时，登录返回配置错误，不签发 JWT。
4. 票据无效、过期或已使用时，登录失败。
5. 验证成功后，`/api/v2/auth/login` 返回 JWT；调用 `/api/v2/auth/me` 可读取身份；注销后旧 JWT 返回 `401`。

## 5. 安全要求

- `.env` 不提交 Git，生产密钥放入云密钥管理服务。
- 生产环境必须使用 HTTPS，并将 `CORS_ORIGINS` 限定为正式域名。
- 登录接口需要在网关增加 IP/账号速率限制、失败次数锁定、审计日志和异常告警。
- 验证码应用 ID 可给前端，腾讯云 API 密钥只能保存在后端环境变量或密钥服务中。

