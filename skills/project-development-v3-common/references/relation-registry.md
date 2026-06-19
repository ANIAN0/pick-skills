# 关系注册表

关系始终从源写向目标；反向来源通过扫描图谱派生。

| 关系 | 方向 | 范围 | 目标变化时的影响 |
|---|---|---|---|
| `depends-on` | 依赖方 → 依赖项 | project | 强：影响源，并沿反向强关系继续。 |
| `verifies` | Verification → Capability/Requirement | project | 强：重新评估验证。 |
| `implements` | Task/Change Contract → 定义节点 | project | 强：重新评估实现。 |
| `researches` | Research Task → 被调研节点 | project | 强：重新评估问题。 |
| `uses-knowledge` | 项目节点 → Knowledge Report | knowledge | 强：重新评估摘要或决策。 |
| `specifies` | UI Spec → Capability | project | 强：重新评估 UI 规格。 |
| `prototypes` | Prototype → UI Spec | project | 强：重新评估原型。 |
| `evidences` | Evidence → Verification/Task | project | 强：保留历史，但证据可能不再证明目标。 |
| `supersedes` | 新节点 → 旧节点 | project | 不传播；通过语义编辑将旧节点改为 superseded。 |
| `references` | 引用方 → 被引用项 | project/knowledge | 仅报告，不自动 stale。 |

除 supersedes/references 外，上述关系均为强关系。影响遍历沿反向强关系递归，使用 visited 集，无任意深度上限。

## 结构父级

`parent` 是结构字段，不是类型关系。内容变化时检查直接父级、直接子级和强关系反向来源，不自动遍历所有祖先和后代。

## 完整性

拒绝重复 ID、缺失项目目标、不可访问知识目标、未知关系、无效 scope、自我父级、冲突多父级事实和 parent 环。类型关系可以成环，但遍历必须用 visited 终止。

## 移动与删除

id 和语义字段不变的路径移动不改变语义；parent 变化属于语义修改，应检查节点、旧/新父级和直接子级。节点有结构子级或入向关系时阻止删除，必须先提供迁移、关系移除或明确级联方案。移动或删除后重建派生产物。
