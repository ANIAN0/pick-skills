# 全局研究知识库

## 存储边界

从 `skillconfig.json` 的 `knowledge.global_dir` 解析全局根目录。字段缺失时建议展开后的 `~/personal-kb`；显式配置路径不可访问时停止调研复用并报告路径错误。

可复用完整报告存入全局根目录。项目只保存：

- 通过 `researches` 关联不确定节点的 Research Task；
- 简洁决策摘要；
- 指向稳定报告 ID 的 `uses-knowledge` 关系；
- 判断时效和来源所需的引用元数据。

不得把完整报告正文复制进项目图谱。

## Knowledge Report 契约

使用 `type: project-development/knowledge-report`，并要求：

- `id`、`title` 和非空 `topics`；
- 非空 `sources`；
- `updated_at` 和面向未来的 `review_after`；
- `confidence`: high、medium 或 low；
- 更新既有报告时填写 `change_summary`。

每个来源记录 `url`、`title`、`publisher`、`accessed_at` 和 `supports`。正文区分有来源发现、推断、限制、冲突和可复用结论。

## 来源与时效规则

- 不把搜索结果摘要当作来源或完整结论。
- 每项事实可追踪到一个或多个来源条目。
- `review_after` 早于评审日期时，消费项目节点视为 stale。
- 过期报告用于新决策前，创建带 `update_of: <report-id>` 的新 Research Task。
- 必需来源不可访问或不足以支撑结论时保持 blocked。

## 更新行为

主题不变时更新同一稳定报告 ID，记录 updated_at、新 review_after、来源变化和 change_summary。通过版本控制或明确历史保留旧版本，不静默替换已被项目引用的结论。
