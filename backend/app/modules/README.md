# 业务模块

每个业务域保持相同的内部结构：`api`、`application`、`domain`、`infrastructure`、`schemas`、`tests`。跨域调用仅通过应用服务、Tool 契约或事件，不允许直接访问其他模块的仓储实现。
