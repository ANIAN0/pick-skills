---
name: implementation-planning-v3
description: 为已通过 G-DESIGN 的每份 tech-design.md 在同目录生成一个同 scope_ref 的 task-list.md，把 T-* 保存在正文，并通过资历门禁和 G-PLAN 后交给执行。
---

# 范围化实施计划 v3

1. 验证 G-DESIGN 及输入哈希。
2. 为每份 Tech Design 在同目录创建一个 Task List；单个 `T-*` 是正文条目，不建独立文件。
3. T-* 明确 C/V、无环依赖 DAG、文件、步骤、独立正负 verification commands、执行断言、证据路径、criticality/risk/infrastructure 和 executor。
4. 核心或基础设施任务没有 senior profile 或真实人工批准时保持 blocked。
5. 使用 `scripts/generate_task_list.py` 保证同目录、同 `scope_ref` 和 Tech hash 贯通。
6. G-PLAN package 必须包含同范围 Test Plan；生成动作不记录确认，由独立用户确认动作确认。缺失或 stale 时不执行。

不执行任务，不弱化 Verification，不为单个 T-* 建 Markdown。
