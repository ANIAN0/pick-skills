# 优先级与执行者契约

## 依赖优先

拒绝任务依赖环。前置任务始终先于依赖它的任务，即使后者更核心或风险更高。

当前依赖就绪任务按以下 `priority_tuple` 升序排列：

```text
(0 if infrastructure else 1,
 0 if criticality == core else 1,
 {high: 0, medium: 1, low: 2}[risk],
 task_id)
```

即基础设施优先，其次其他核心工作，再到支撑工作；同类按风险和稳定 task_id 排序。

## 执行者门禁

`criticality: core`、`infrastructure: true` 或需要资深判断时设置 `executor_requirement: senior`。进入 in_progress 前必须具备 `executor_profile: senior`，或 `approval.approved: true` 且有真实 `approved_by`、`approved_at`。否则任务保持 blocked 并记录具体原因，不得编造执行者或审批。

依赖和验证均通过后，支撑任务可由 standard 执行者处理。

## 分配输出

报告就绪队列、阻塞队列、排序原因、执行者要求、所选执行者/审批和前置 ID。每次任务完成或上游 stale 后重新计算。
