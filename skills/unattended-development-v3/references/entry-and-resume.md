# 入口与恢复

| 模式 | 起点 | 最小范围 |
|---|---|---|
| full | User Story requirements | 四闸门完整闭环 |
| extension | 变化 requirements | 影响子图与四闸门 |
| task | 已规划 Task List | G-PLAN、执行、G-ACCEPT |
| bug | 缺陷任务/根因 | 复现、修复、回归、G-PLAN/G-ACCEPT |

暂停记录 run ID、scope_ref、current_gate、resume_gate、pause_reason 和每个 gate status。恢复时重算 scope hash，只进入 resume gate 及后续阶段；未受影响且仍有效的 gate 不重复询问。
