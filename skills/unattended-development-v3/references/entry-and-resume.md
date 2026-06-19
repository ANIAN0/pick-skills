# 入口与恢复

## 入口选择

| 模式 | 合法入口 | 最小子图 |
|---|---|---|
| `full` | User Story | 已确认故事范围到发布门禁。 |
| `extension` | 既有 User Story/Requirement/Capability/Decision/Contract | 新增/变化分支及可执行影响。 |
| `task` | Ready Task | 任务、所属变更契约、验证、前置、证据和验收影响。 |
| `bug` | Root Cause 或缺陷 Task | 复现、责任修复节点、验证、回归和验收。 |

入口节点类型不兼容时拒绝该模式。缺必要上游节点时创建 Finding 或路由到责任 Skill，不得凭空生成完整阶段树。

## 确认复用

调用阶段前重算输入哈希。必需决策哈希有效时直接消费；stale 时在责任节点暂停并计算局部影响。

## 暂停记录

将 Workflow Run 设为 blocked，并记录：带门禁码和具体缺失/失败条件的 `pause_reason`；停止位置 `current_node`；通常为最早责任或受影响未完成节点的 `resume_node`；`finding_ids` 和完整 `finding_impact_set`；排除 report-only 弱引用后的可执行恢复 ID；适用时记录证据/错误路径和所需人工决策。

## 恢复

问题解决后校验责任节点、重算影响、验证 Finding 关闭证据，并从 resume_node 继续。不得重新进入可执行影响集之外的已完成节点；新影响必须先更新 Workflow Run。
