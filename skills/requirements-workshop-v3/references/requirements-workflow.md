# 自适应需求工作流

## 入口

- `full`：先形成并确认整体 User Story，再评估是否需要模块和功能点。
- `extension`：只更新受影响 requirements 文档，保留无关有效确认。
- `task/bug`：需求与验证已经明确时交给总控快捷入口，不伪造新需求节点。

## Story 确认与分解决策

1. 先创建 `stories/US-<id>-<slug>/requirements.md`，保留用户要求的 deliverable type、format、location、audience。
2. 存在真实独立业务边界时才拆模块，通常不超过 3 个。创建模块前必须取得整体 Story 的真实用户确认。
3. 模块 requirements 内仅在同时需要独立目标、实现、测试和验收闭环时定义 `F-*`，通常不超过 10 个。
4. 超过第 3 个模块或第 10 个功能点时暂停并请求 decomposition decision；不得自动放行。
5. 简单场景不创建 `modules/`、`features/` 或任何占位目录。

普通 Requirement、Capability、Verification 和验收条目写在 requirements 正文，不为每个条目创建 Markdown。`F-*` 也只存在于模块 requirements 正文，后续独立 Tech/Task/Test/Verification 通过同一 `scope_ref` 引用。

## G-REQ

G-REQ 决策包包含 Story 和实际模块 requirements、deliverable 字段及 decomposition decision。按公共确认协议计算 scope hash。缺失用户确认、无人值守或哈希失配时必须暂停；哈希有效时恢复流程不重复确认。通过后把 document IDs、scope_ref、scope hash 和 deliverable 交给技术设计。

## UI/原型

UI 和原型适配器接收 requirements document ID、内部 R/A/F 引用、scope_ref、页面/状态/交互要求及验收边界。产物只回链完整文档节点，不创建 Capability/Verification 文件。
