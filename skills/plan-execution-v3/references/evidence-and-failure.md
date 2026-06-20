# 文档内证据与失败责任

每次真实执行向 Task List 的 `execution_records` 追加记录，并由 Verification Report 引用。记录包含 task/verification/scope、命令或观察、exit code、stdout/stderr、timestamp、executor、result 和 artifact paths。失败不可覆盖；重试追加。

失败时在 Task List/Review Report 内增加 Root Cause/Finding 条目，保留实际行为、责任任务、修复条件和关闭证据。不创建 `node_type: evidence`、Evidence Markdown 或单 Finding 文件。
