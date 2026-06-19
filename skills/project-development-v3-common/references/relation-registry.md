# 文档关系注册表

只保存源到目标的正向关系；反向来源由索引派生。

| 关系 | 方向 | 范围 | 影响 |
|---|---|---|---|
| `derives-from` | Tech Design → Requirements | project | 强 |
| `plans` | Task List → Tech Design | project | 强 |
| `tests` | Test Plan → Tech Design | project | 强 |
| `verifies` | Verification Report → Test Plan/Requirements | project | 强 |
| `reviews` | Review Report → 被评审文档 | project | 强 |
| `depends-on` | 文档 → 依赖文档 | project | 强 |
| `uses-knowledge` | 项目文档 → Knowledge Report | knowledge | 强 |
| `specifies` | UI Spec → Requirements | project | 强 |
| `prototypes` | Prototype → UI Spec | project | 强 |
| `supersedes` | 新文档 → 旧文档 | project | 不传播 |
| `references` | 引用方 → 被引用文档 | project/knowledge | 仅报告 |

除 `supersedes`、`references` 外均沿反向关系传播影响。`parent` 是单一结构归属，不是关系。拒绝重复 ID、断链、自父级、多父级、parent 环、未知关系和无效 scope。

Evidence 不再是图节点或 `evidences` 关系；真实证据写入 Verification Report，并从内部 `V-*`/`T-*` 追踪到命令和产物。
