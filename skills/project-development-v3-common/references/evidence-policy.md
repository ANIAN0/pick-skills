# 证据策略

## Evidence 节点

使用 `node_type: evidence`，并以 `evidences` 从 Evidence 指向被证明的 Verification 或 Task。

| 字段 | 规则 |
|---|---|
| `command` | 精确命令或具体观察步骤。 |
| `exit_code` | 命令执行后的真实退出码。 |
| `stdout` / `stderr` | 真实相关输出或其产物路径。 |
| `timestamp` | 带时区的 ISO 8601 观察时间。 |
| `result` | passed、failed、blocked 或 not_verified。 |
| `artifact_paths` | 持久日志、截图、报告或回归资产路径。 |
| `executor` | 实际执行观察的人员或环境。 |

不得编造输出、退出码、时间、执行者或产物路径。大型原始输出保存为产物，节点中只写摘要。

## 结果语义

- passed：检查真实运行或直接观察，且符合标准。
- failed：真实运行或观察，但不符合标准。
- blocked：明确前置条件阻止执行。
- not_verified：实现可能存在，但所需观察未完成。

## 完成门禁

- Task 至少关联一个适用 Verification，并有覆盖完成断言的 passed Evidence。
- Verification 的正向及必要负向路径均有 passed Evidence 才能 done。
- Acceptance/Workflow Run 以 depends-on 关联范围内每个 Verification/Task，且每个目标都有可追踪 passed Evidence；Evidence 仍只指向 Verification/Task。
- failed、blocked、not_verified、模拟、mock、硬编码或未执行观察不能满足 done。
- 失败和已替代 Evidence 作为历史保留；重试新增 Evidence，不改旧结果。

## 评审与责任

评审发现不清晰、矛盾或无依据断言时创建 review-finding，记录严重级别、责任方、来源节点、影响和所需修复。外部事实不确定时创建 Research Task，完整报告写入全局知识库，项目决策以 uses-knowledge 引用。执行失败时保存真实 Evidence 并关联责任 Finding/Root Cause，不得弱化 Verification。
