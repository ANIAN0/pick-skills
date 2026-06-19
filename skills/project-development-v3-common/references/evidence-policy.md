# 证据策略

## 存放位置

Evidence 是 Verification Report 内部的不可伪造执行记录，不是独立 Markdown/图节点。大型日志、截图和报告作为真实文件产物被报告引用。

每条执行记录至少包含：关联 `T-*`/`V-*`、精确命令或观察步骤、真实退出码、stdout/stderr 摘要或产物路径、带时区时间、结果、artifact paths 和实际 executor。

结果只允许 `passed`、`failed`、`blocked`、`not_verified`。重试追加记录，不覆盖历史失败。

## 完成门禁

- Task List 中的任务只有在关联验证有真实 passed 记录后才能 done。
- Test Plan 的正向和必要负向路径均有 passed 记录后，Verification Report 才能形成通过结论。
- failed、blocked、not_verified、mock、固定回复、硬编码或未执行观察不能满足完成。
- G-ACCEPT 必须确认包含真实证据的 Verification Report；确认不能替代测试，测试也不能替代用户验收。

评审发现和根因作为 Review/Root Cause Report 内部条目保存并引用责任文档，不为每条 Finding/Evidence 建文件。
