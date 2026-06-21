# 五阶段编排

顺序固定为 `requirements → tech-design → planning → execution → acceptance`。planning 与 execution 复用同一任务入口，但分别检查 `plan_review` 和 `execution_review`。每个阶段都必须先由责任 skill 完成自检和独立审查，再由用户明确确认；Workflow Run 只验证并记录这些状态。
