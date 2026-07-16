# 单来源摄入事务

只在处理 ingest queue 时读取。一个事务只有一个 primary source；可以读取依赖和现有 OKF 以理解上下文，但不能顺便把其他来源标记为已处理。

## 队列状态

`_meta/ingest-queue.json` 由脚本维护：

- `pending/analyze`：等待或重新分析；
- `in_progress/analyze`：只读来源与知识库，不写正文；
- `in_progress/write`：analysis artifact 已固定，可以合并页面；
- `in_progress/validate`：页面已写，等待来源级验证；
- `done/done`：当前来源指纹已提交；
- `not_verified/review`：写入通过确定性校验，但仍有 blocker review item；
- `blocked`：写入中断、回滚不确定或其他不能安全重试的情况。

队列按 `priority`、来源路径稳定排序。恢复时，分析阶段中断可回到 pending；write/validate 中断必须 blocked，防止部分写入被当作新起点。

## Analysis artifact

claim 后先写 `_meta/ingest/<stable-id>.json`，不修改概念页。最低结构：

```json
{
  "source_path": "docs/example.md",
  "source_sha256": "当前 coverage 指纹",
  "summary": "只陈述来源实际包含的内容",
  "disposition": "mapped",
  "claims": [
    {"text": "进入正文的结论", "evidence": "docs/example.md#标题", "target": "concepts/example.md"}
  ],
  "proposed_targets": [],
  "shared_targets": ["index.md", "log.md"],
  "review_items": []
}
```

`claims` 逐条绑定正文结论、精确 evidence 和 target；每条都必须在对应页面出现。`proposed_targets` 列当前来源贡献的规范页；`shared_targets` 穷举本事务会改动的索引、日志和关系对端，使快照覆盖完整 write set。没有长期知识贡献时使用有证据的 `ignored/duplicate/superseded/...` disposition。

对话 Capture 的每条 claim 额外填写 `assertion_type`。`user-decision` 只能使用 `normative`；其他 Capture 只能使用 `reported`。普通项目来源默认按已验证证据处理，不需要该字段。

Review item 使用稳定 `id`，并包含 `type`、`severity: blocker|warning`、`summary`、`evidence`。矛盾、身份冲突、缺失权威事实进入 backlog，不在正文中静默裁决。

## 事务顺序

1. 运行 queue `next`，只 claim 返回的一个来源。
2. 核对文件仍存在且 SHA-256 与任务一致；读取全文或完整转换结果。超长文件可分块分析，但仍是一个来源事务，并保存可恢复 checkpoint。
3. 读取 purpose、schema、相关 OKF 页面和解释该来源必需的依赖；输出 analysis artifact。此阶段不写正文。
4. 复核 artifact 的对象身份、evidence、冲突和 proposed targets；记录 analysis 后才进入 write。
5. 对每个 target 先读取当前页面。合并正文与 `sources/tags/relations`，保留其他来源贡献；只替换由当前来源独占且已被当前版本证伪的内容。
6. record-analysis 固定 artifact 指纹，保存 coverage 与完整 write set 快照，并记录 OKF 基线 manifest；随后维护共享索引、关系和当前来源 coverage。record-write/finish 检出任何未声明写入时阻塞事务。
7. record-write 后运行来源级 validator。验证 source hash、disposition、claims、目标正文、反向 sources、对象身份和受影响链接；其他 pending 来源不阻塞本事务。
8. validator 通过后 finish。无 blocker review 时任务为 done；有 blocker 时为 not_verified。只有 done 指纹可用于跳过未变化来源。

## 命令

严格顺序是 `sync → next → claim → record-analysis → record-write → finish`。失败使用 `fail`；write 后用 `fail --rollback` 由工具恢复固定快照。review item 只能用带 resolution/evidence 的 `resolve-review` 关闭，关闭时重新校验来源指纹、artifact 和目标页。

## 单次执行停止点

完成一个来源事务后队列关闭当前 cycle，停止并报告总数、done/pending/not_verified/blocked、修改页面和下一来源。下一次用户明确要求继续后先运行 `continue`；未重新开启 cycle 时工具拒绝 claim。
