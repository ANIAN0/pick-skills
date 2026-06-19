# 变更契约

## 必填字段

| 字段 | 含义 |
|---|---|
| `change_category` | backend、frontend、data、configuration、workflow、test-support 或 documentation。 |
| `change_type` | add、modify、remove 或 migrate。 |
| `target_files` | 已存在或计划新增的仓库相对路径。 |
| `target_symbols` | 将改变的函数、类、Schema、字段、命令或章节。 |
| `current_state` | 有证据支撑的变更前行为。 |
| `target_state` | 变更后的必需行为。 |
| `behavior_delta` | 精确的新增、删除、传递、持久化、错误及可观察变化。 |
| `input_confirmation_hashes` | 上游节点 ID 到确认哈希的映射。 |
| `verification_ids` | 证明该 Delta 的验证节点。 |
| `compatibility` | 必须保留的契约和有意破坏项。 |
| `risks` | 具体失败与回归风险。 |
| `rollback_or_containment` | 安全回退或故障隔离方式。 |

## 关系

- 变更契约以 `implements` 指向责任需求或能力。
- 以 `depends-on` 指向必要验证和前置变更契约。
- 只有实际用于决策的全局报告才使用 `uses-knowledge`。
- 不写反向关系；反向链接由索引派生。

## 计划充分性

计划 Skill 必须能在不重新设计的情况下确定精确文件、相邻接口、执行断言、测试、负向路径和依赖。不能做到时保持 blocked，并补齐缺失技术决策或调研。
