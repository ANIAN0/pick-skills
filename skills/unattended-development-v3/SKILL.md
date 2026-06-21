---
name: unattended-development-v3
description: 编排项目研发 v3 的 full、extension、task、bug 流程，复用真实阶段入口，把运行状态持久化到具体版本的 workflow-runs，并在任一阶段缺少独立审查或用户确认时暂停；不替阶段 skill 工作或自动确认。
---

# 五阶段总控 v3

无人值守表示在两个必须由用户决定的节点之间持续推进安全工作，不表示跳过用户确认。

## 流程

标准顺序与 `project-development-v3-common` 一致：

```text
requirements -> tech-design -> planning -> execution -> acceptance
```

- `full` / `extension` 从需求开始。
- `task` / `bug` 从已确认计划开始，但仍经过执行和验收。
- 需求、方案、计划、执行结果和验收分别要求独立审查通过及用户明确确认。
- 执行复用计划入口；planning 和 execution package 指向同一任务入口。

## 使用

先由对应阶段 skill 创建或更新入口，再使用确定性脚本检查入口状态并持久化 Run：

```text
python skills/unattended-development-v3/scripts/orchestrate.py start --project-root <真实项目根目录> --version <真实版本> --mode full --scope-ref <需求入口> --package requirements=<需求入口>
python skills/unattended-development-v3/scripts/orchestrate.py resume --project-root <真实项目根目录> --version <真实版本> --run-id <RUN-*>
```

后续入口产生后，使用重复的 `--package stage=path` 补充 package。脚本只读取入口和审查报告，不生成阶段结论、不写 `confirmed`、不运行实现，也不代表用户确认。

Run 保存在 `workplace/<真实版本>/workflow-runs/RUN-*.json`。它是编排记录，不是第五阶段之外的新业务入口。

## 暂停与恢复

缺少 package、阶段状态未确认、审查未通过或执行未确认时，保存 `blocked`、`current_stage`、`resume_stage` 和 `pause_reason` 后停止。用户确认后恢复同一 Run，不新建 Run。

已经通过的入口和审查报告发生变化时，脚本返回 `confirmation_stale`。只有用户重新检查并明确确认变更后，才能使用 `--reset-gate <stage>` 清除该阶段及其下游缓存并重新验证；无人值守 Agent 不得自行调用该参数来绕过确认。

验收缺陷触发执行或上游回退时，按公共回退契约重开责任阶段，并从最早失效阶段重置；不得只重跑验收。

## 完成条件

只有五阶段必要入口都存在、对应审查为 `passed`、阶段状态均由用户确认且当前文件未使确认失效时，Run 才能写为 `done`。`done` 仅表示编排闭环完成，不替代验收入口中的真实证据。
