# 文档节点 Schema

以下字段是项目研发 v3 扩展，不得描述为 OKF 标准字段。

## 事实粒度

一份可独立阅读的 Markdown 产物对应一个图节点。`R-*`、`A-*`、`F-*`、`D-*`、`C-*`、`T-*`、`V-*`、`REV-*` 是文档内部条目，不单独创建 Markdown 或图节点。

新项目文档位于 `graph/stories/US-*/...`；旧 `graph/nodes/` 仅只读兼容。文档 ID 来自 Frontmatter，与文件路径解耦。

## 必填字段

| 字段 | 类型 | 规则 |
|---|---|---|
| `type` | string | 固定为 `project-development/document-node`。 |
| `id` | string | 稳定、非空、图内唯一。 |
| `document_type` | enum | 使用下列完整文档类型之一。 |
| `title` | string | 非空、用户可读。 |
| `status` | enum | 使用公共生命周期状态。 |
| `revision` | integer | 从 1 开始，语义变化时递增。 |
| `parent` | string/null | 根需求可为空，其余指向一个文档节点。 |
| `scope_ref` | mapping | 包含 `document` 和可空的 `item`。 |
| `relations` | list | 只保存注册的正向关系。 |

允许的 `document_type`：

```text
requirements
tech-design
task-list
test-plan
verification-report
research-task
review-report
root-cause-report
ui-spec
prototype
```

允许的 `status`：`draft`、`confirmed`、`ready`、`in_progress`、`blocked`、`done`、`stale`、`superseded`。

## 范围引用（scope_ref）

```yaml
scope_ref:
  document: DOC-REQ-M-001
  item: F-001
```

- `document` 必须指向 requirements 文档；需求文档自身指向自己。
- `item: null` 表示整份需求范围；`F-*` 表示需求正文中的独立闭环功能点。
- 同一功能范围的 tech-design、task-list、test-plan、verification-report 必须使用完全相同的 `scope_ref`。
- `F-*` 不得单独制造占位 Markdown。

## 内部条目与证据

文档正文保存普通研发条目和追踪关系。Task List 内的 `T-*` 保存执行属性；Test Plan 内的 `V-*` 保存正负场景；Verification Report 内保存真实命令、结果、时间、产物和执行者。未知字段必须保留。

## 知识报告

全局 Knowledge Report 继续使用 `type: project-development/knowledge-report`，不受 Story 目录和项目生命周期约束。
