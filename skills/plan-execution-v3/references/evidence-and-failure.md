# 证据与失败责任

## 写入证据

每次有意义的执行都创建新 Evidence，以 `evidences` 关联任务及适用验证，记录 task_id、verification_id、精确命令或观察、真实 exit_code、stdout/stderr 或原始输出路径、timestamp、executor、result、artifact_paths、执行断言结果和变更文件。既有失败证据不可修改；重试创建新证据。

真实命令 exit_code 非零时结果必须为 failed，所属任务不能 done，并进入失败分类。不得把失败进程改写为通过证据。

## 失败分类

| 责任 | 动作 | 任务状态 |
|---|---|---|
| 实施缺陷或局部代码理解错误 | 创建关联失败证据和任务的 Root Cause；定义根因与回归后修复。 | in_progress/blocked |
| 需求、验证、变更契约或任务矛盾 | 针对责任节点创建 Finding 并运行局部影响分析。 | blocked |
| 缺环境、凭据、服务、工具或权限 | 记录 blocked/not_verified 证据及缺失条件。 | blocked |
| 产品行为未通过有效验证 | 保留失败，创建 Root Cause/Finding 并修复产品行为。 | 不得 done |

不得修改有效期望来迁就实现，也不得用替代响应或更弱状态隐藏失败。

## 根因关闭

根因记录失败证据 ID、复现、实际/预期行为、因果机制、受影响节点/文件、修复契约、回归验证和关闭证据。修复前可复现且修复后回归通过，才能 done。

## Finding 交接

责任在上游或跨节点时使用 Finding，记录严重级别、责任节点、影响集、所需修复和关闭证据。执行阶段不得直接批准高风险产品决策。
