# 局部评审与恢复

Review Report 指向责任文档和可选内部条目。完整 impact_set 用于审计，剔除 `report-only:` 后形成 review_scope 和恢复输入。未受影响且哈希有效的决策或已完成任务不重放，不因局部问题把全图标记 stale。

外部事实不确定时在责任范围创建 Research Task；修复后只重新验证 review_scope，并用真实证据关闭 REV-*。
