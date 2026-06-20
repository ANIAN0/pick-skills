---
name: plan-execution-v3
description: 执行已通过 G-PLAN 且具备同范围 Test Plan 的 Task List 内部 T-*，运行真实命令并把状态、证据和失败根因回写闭环文档。
---

# 文档闭环执行 v3

1. 验证图、G-PLAN、scope_ref、同范围 Test Plan、依赖 DAG 和 executor 门禁；资历取自本次真实执行上下文，不信任任务文档自报。
2. 使用 `scripts/execute_task_list.py` 逐个执行结构化 T-* 的真实命令，禁止 shell 拼接和固定回复。
3. 实现命令必须改变声明产物并通过 must appear/disappear/propagate/persist 断言；随后为每个 V-* 分别运行 positive/negative verification command。
4. 把 task ID、verification IDs、verification case、scope、命令、exit code、stdout/stderr、时间、executor、artifact paths 和结果回写 Task List。
5. 非零退出码、产物未变化、断言失败、缺任一正负场景、未运行、not_verified 或 blocked 均不得写 done；失败作为内部 Root Cause 条目保留。
6. 已有有效 passed 记录的 done 任务恢复时不重跑；依赖失败只阻断下游。
7. 不创建 Evidence 或 Root Cause 文件节点；Verification Report 后续消费这些不可覆盖的执行记录。
