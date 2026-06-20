# 阶段确认包协议

## 四个强制闸门

| Gate | 决策包 | 放行目标 |
|---|---|---|
| `G-REQ` | 已确认 User Story、模块边界、需求正文和功能点范围 | 技术设计 |
| `G-DESIGN` | 范围内 Tech Design | 实施计划 |
| `G-PLAN` | Task List、Test Plan 和执行边界 | 执行 |
| `G-ACCEPT` | Verification Report 与验收结论 | 完成 |

每个确认包记录：

```yaml
gate: G-REQ
scope_ref: {document: DOC-REQ-US-001, item: null}
document_ids: [DOC-REQ-US-001]
document_hashes: {DOC-REQ-US-001: sha256:<64 位小写十六进制>}
scope_hash: sha256:<64 位小写十六进制>
confirmed_at: <带时区 ISO 8601>
confirmed_by: <真实用户身份或明确人工确认标识>
```

## 范围哈希（scope hash）

按文档 ID 排序，对每份文档计算语义哈希，再对 `gate + scope_ref + [(id, digest)]` 的规范 UTF-8 JSON 计算 SHA-256。语义哈希排除路径、状态、确认时间和派生字段，包含正文、revision、parent、relations、document_type 和 scope_ref。

包内任一文档变化即使对应 gate stale；无关文档变化不失效。哈希匹配时恢复流程不得重复提问。只有用户真实确认后才能写 `confirmed_at/confirmed_by`；无人值守流程必须暂停，禁止自动确认。

`document_hashes` 用于证明较大决策包确实覆盖其中某一份未变化文档，例如 Story 初次确认后再展开模块。它不能代替整个 package 的 `scope_hash`；新增模块后仍需对完整 G-REQ package 再确认。
