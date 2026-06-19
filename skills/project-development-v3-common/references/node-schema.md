# 节点 Schema

以下字段是项目研发 v3 扩展，不得描述为 OKF 标准字段。

## 项目节点

`workplace/<version>/graph/nodes/` 下每个文件都是带 YAML Frontmatter 的 UTF-8 Markdown。

| 必填字段 | 类型 | 规则 |
|---|---|---|
| `type` | string | 固定为 `project-development/node`。 |
| `id` | string | 稳定、非空、项目图谱内唯一，且与文件路径无关。 |
| `node_type` | enum | 使用下列节点类型之一。 |
| `title` | string | 非空、用户可读标题。 |
| `status` | enum | v3 生命周期状态。 |
| `revision` | integer | 从 1 开始；语义源内容变化时递增。 |

| 可选/条件字段 | 类型 | 规则 |
|---|---|---|
| `parent` | string/null | 仅根节点可为 null；非根节点只指向一个项目节点 ID。 |
| `relations` | list | 默认 `[]`，条目遵循关系 Schema。 |
| `confirmation` | mapping/null | 遵循确认协议；确认门禁消费者继续前必须有效。 |

允许的 `node_type`：

```text
user-story
requirement
capability
verification
research-task
ui-spec
prototype
technical-decision
change-contract
review-finding
root-cause
task
acceptance
evidence
workflow-run
```

允许的 `status`：

```text
draft
confirmed
ready
in_progress
blocked
done
stale
superseded
```

## 关系条目

每个关系包含：已注册的 `type`、稳定目标 ID `target`，以及与注册表一致的 `scope`（project/knowledge）。只保存源到目标关系，不把反向链接或子节点列表持久化为事实。

## 知识报告

全局 Knowledge Report 是 `type: project-development/knowledge-report` 的 UTF-8 Markdown，不是项目节点，因此没有 node_type、parent 或项目生命周期要求。必填字段：`type`、`id`、`title`、`topics`、`sources`、`updated_at`、`review_after`、`confidence`。每个来源必须可检索并具备可识别出处；正文保存可复用结论，修订记录变化摘要，不静默覆盖已被项目使用的结论。

## 保留与所有权

- 读取者必须接受并保留未知字段。
- backlinks、children、computed impact 和索引时间等派生字段只进入 `.derived/`。
- 内部图脚本对源 Markdown 只读。
- 语义编辑由人或阶段 Skill 负责，并递增 revision。

## 能力与验证配对

Capability 与其 Verification 共享 parent；至少一个 Verification 以 `verifies` 指向 Capability 后才能通过门禁。

## Task 扩展字段

Task 还需定义 `criticality`（core/supporting）、`infrastructure`、`risk`（high/medium/low）、`executor_requirement`（senior/standard）、`executor_profile` 和 `approval`。核心或基础设施任务进入 in_progress 前必须有 senior 或明确人工审批。
