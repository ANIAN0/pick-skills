# 生命周期

v3 节点生命周期独立于 v2 计划任务状态。

| 状态 | 含义 |
|---|---|
| `draft` | 语义内容仍在形成。 |
| `confirmed` | 人工确认快照和哈希有效。 |
| `ready` | 上游确认和入口门禁有效。 |
| `in_progress` | 责任工作流正在处理。 |
| `blocked` | 明确决策、依赖、执行者或外部条件阻止推进。 |
| `done` | 节点专属验证和证据门禁全部通过。 |
| `stale` | 内容或相关依赖变化，旧确认/证据不足。 |
| `superseded` | 新节点替代该节点，历史仍可读。 |

## 允许转换

```text
draft -> confirmed | blocked | superseded
confirmed -> ready | stale | superseded
ready -> in_progress | blocked | stale | superseded
in_progress -> blocked | done | stale | superseded
blocked -> draft | ready | in_progress | stale | superseded
done -> stale | superseded
stale -> draft | confirmed | superseded
superseded -> 无
```

拒绝未声明转换。语义编辑者执行转换；校验和影响脚本只报告有效状态及所需动作。

## 有效 stale

存储确认哈希与当前语义哈希不一致时，即使 Frontmatter 写 confirmed/ready/done，也按有效 stale 处理，同时报告声明和有效状态；只读脚本不得改写 Markdown。

## 入口与完成门禁

- 必需上游确认缺失或无效时不得 ready。
- 核心/基础设施 Task 没有 senior 或明确审批时不得 in_progress。
- Capability 没有同父级且以 verifies 关联的 Verification 时不得完成。
- Task/Verification done 必须有直接关联的 passed Evidence。Acceptance/Workflow Run 以 depends-on 关联必要 Verification/Task，并要求每个目标有 passed Evidence。
- not_verified 是证据结果，不是生命周期状态；所属节点保持非 done。
- failed、缺失、模拟或未执行证据永远不能转为 done。
