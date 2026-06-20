---
name: unattended-development-v3
description: 编排项目研发 v3 的 full、extension、task、bug 文档子图，把 Workflow Run 持久化到 graph/runs，并在 G-REQ、G-DESIGN、G-PLAN、G-ACCEPT 任一人工确认缺失或失效时暂停。
---

# 四闸门总控 v3

1. 选择 full/extension/task/bug 最小必要子图。
2. 使用 `scripts/orchestrate.py` 创建 Workflow Run，贯穿同一 run ID 和 scope_ref；可为每个 gate 提供 `stage_actions`，以无 shell 拼接的真实命令生成 package 并记录 stdout/stderr/exit code。
3. full/extension 检查四 gate；task/bug 从 G-PLAN 开始，但仍必须通过 G-ACCEPT。
4. 缺包、缺确认或 scope hash stale 时保存 current/resume gate 和 pause_reason，立即停止。
5. 用户真实确认后恢复同一 Run；有效 gate 直接复用，不重复询问。
6. 阶段 action 只能生成或更新决策包，不能记录确认；无人值守 Agent 不得填写 confirmed_by，不得把 blocked 降级为继续或 done。
