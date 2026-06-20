# 范围化设计工作流

只消费 G-REQ 包内 requirements 和直接必要知识。简单 Story/Module 产生一个同目录 tech-design；模块存在独立 `F-*` 时，每个实际功能点产生一个 Feature 目录内 tech-design，父范围不再生成重复设计。

每份文档正文维护 D/C/V、代码证据、知识来源、兼容和失败模型。Frontmatter 保存 `scope_ref`、需求语义哈希、G-REQ 包哈希、knowledge refs 和 deliverable。

G-DESIGN 包同时覆盖输入 requirements 与设计文档。输入、知识或设计变化使包 stale；缺失真实用户确认时暂停。
