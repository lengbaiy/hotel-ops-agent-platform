# GitHub 团队协作规范

## 仓库初始化

1. 在 GitHub 创建组织仓库（建议私有），并配置团队成员权限。
2. 推送本框架后，在仓库设置中保护 `main`：要求 Pull Request、至少 1 位代码所有者审查、CI 通过，禁止强制推送。
3. 在 Projects 中按 `M1` 至 `M5` 建立看板；每项需求创建 Issue，并写清验收条件。

## 开发流程

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feat/<issue-number>-<topic>
# 开发、测试后：
git add .
git commit -m "feat(scope): 完成 #123 的简要说明"
git push -u origin HEAD
```

随后从 GitHub 创建 Pull Request，关联 Issue。禁止直接推送 `main`，禁止提交密钥、生产数据、Cookie 或未脱敏客户数据。

## 提交约定

使用 Conventional Commits：`feat`、`fix`、`docs`、`test`、`refactor`、`chore`。每个 PR 保持单一目标，并在描述中填写测试方式、风险与回滚策略。
