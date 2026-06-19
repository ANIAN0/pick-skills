# 文档生命周期

状态为 `draft`、`confirmed`、`ready`、`in_progress`、`blocked`、`done`、`stale`、`superseded`。

允许转换：

```text
draft -> confirmed | blocked | superseded
confirmed -> ready | stale | superseded
ready -> in_progress | blocked | stale | superseded
in_progress -> blocked | done | stale | superseded
blocked -> draft | ready | in_progress | stale | superseded
done -> stale | superseded
stale -> draft | confirmed | superseded
```

需求、设计、计划和验收分别受 `G-REQ`、`G-DESIGN`、`G-PLAN`、`G-ACCEPT` 控制。缺失、哈希失配或无人确认时必须 blocked/awaiting confirmation，不得推断批准。

`done` 还要求适用的 `T-*`、`V-*` 和真实 Evidence 在 Task List、Test Plan、Verification Report 中闭环。`not_verified` 是证据结果，不是生命周期状态。
