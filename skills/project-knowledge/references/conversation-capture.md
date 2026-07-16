# 对话 Capture 协议

只在用户要求“记录这个问题/决定/经验”，或当前对话产生了值得进入知识库的新信息时读取。Capture 是不可变的原始来源，不是概念页，也不绕过单来源摄入事务。

## 存储与类型

默认写入 `<project-root>/knowledge-sources/captures/YYYY-MM-DD/EVD-*.json`；路径必须位于项目根内、OKF 根外且能被 canonical inventory 扫描。编号使用证据前缀 `EVD-*`。

`_meta/capture-registry.json` 在创建时绑定来源路径、EVD ID、kind、scope 和 SHA-256。修改原 Capture、移除 schema 或复用路径都会使其变成 tampered，而不是降级为普通来源；修正和补充必须创建新 Capture。

`kind` 只使用：

| kind | 证明范围 | 摄入 claim 类型 |
|---|---|---|
| `user-decision` | 用户有权决定的规则、范围或取舍 | `normative` |
| `problem-report` | 用户报告过某个问题 | `reported` |
| `observation` | 对话中的待核观察 | `reported` |
| `experience` | 作者报告的经历及其当时理解 | `reported` |
| `resolution` | 用户报告某问题已处理；必须关联原 EVD | `reported` |

Capture 保存 `id/captured_at/kind/reporter/scope/summary/details/context/evidence_refs/requested_action/resolves/epistemic`。`evidence_refs` 只是调查线索，不因写进 Capture 自动成为已验证证据。

## 捕获流程

1. 根据用户原意写 `summary`，把推断放入 `details` 并明确标记；记录当前项目、相关路径和可用的 conversation reference。
2. 运行 `capture` 命令。命令只创建新文件，不覆盖旧 Capture，并拒绝 OKF 内路径、默认排除目录和当前 coverage 的用户排除目录；知识库已处于 `growing` 且队列存在时自动重跑 inventory 和 queue sync，其他阶段返回 `awaiting_inventory`，不擅自推进阶段。
3. 报告 Capture ID、来源路径、队列状态和真值边界。此时不得声称正式知识已更新。
4. 后续把它当作一个普通 primary source 摄入。问题报告只能写成“谁报告了什么/尚待验证”；技术事实必须由代码、日志、测试、扫描结果或调查记录等独立来源支持。
5. 修复或结论使用新的来源记录。`resolution` 用 `resolves` 关联原始 EVD，不修改或覆盖原记录；再摄入调查证据、修复和验证结果，形成 `报告 → 调查 → 决策 → 修复 → 验证 → 经验` 链路。

## 查询和可用性

- `reported` claim 即使来源事务为 `done`，也只证明“该陈述被报告”，不能回答成项目事实。
- `normative` claim 只在 Capture 的 `scope` 和用户权限范围内支持“用户作出了该决定”，不能证明系统当前实现已经遵守。
- 所有原始 Capture 都是 `fact_eligible: false`、`operational_eligible: false`；要进入 operational milestone，必须另有正式决定、调查、代码、日志、测试或验证记录作为来源。
- `sensitive` Capture 必须创建 blocker review item 并保持 `not_verified`，不能用空 claims/targets 无痕完成。
- 当正式证据证实或推翻报告时，保留报告历史，并由新的已提交来源支持技术结论。
- `inbox/` 可以投影待处理 Capture 供人浏览，但不是原始来源存储，也不能取代 coverage/queue。
