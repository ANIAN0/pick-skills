# 四闸门编排

顺序固定为 `G-REQ → G-DESIGN → G-PLAN → G-ACCEPT`。每个 gate 都使用公共 scope hash 和真实 confirmed_by。任何缺失或 stale 均将 Workflow Run 持久化为 blocked；没有连续自动跨过阶段确认的路径。

Workflow Run 是 `graph/runs/*.json` 运行记录，不是业务图节点。各阶段交接必须携带 run ID、scope_ref、gate package document IDs 和 pause/resume reason。
