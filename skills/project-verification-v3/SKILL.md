---
name: project-verification-v3
description: 为每个技术范围在执行前生成同目录 Test Plan，执行后聚合真实 Task List 记录和资产形成 Verification Report，并通过 G-ACCEPT 完成验收。
---

# 范围化项目验证 v3

1. 设计完成后立即调用 `scripts/verification_documents.py` 的 `create_test_plans`，为每个 Tech Design 创建同目录同 scope_ref Test Plan。
2. Test Plan 的 `V-*` 是正文和结构化字段，不为每个验证建文件。
3. 执行后调用 `finalize_verification`，只消费真实 Task List execution records，并重新检查 artifact paths。
4. 每个 V-* 必须有可区分的 `positive` 和 `negative` passed 记录；不能用同一条记录同时满足两种场景。
5. `finalize_verification` 只生成报告和 G-ACCEPT package，不接受确认身份；随后由独立 `accept_verification` 用户确认动作记录 G-ACCEPT。

不以“已调用测试 Skill”代替结果，不创建 Acceptance/Evidence 条目文件，不放宽断言。
