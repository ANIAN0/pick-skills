---
name: tech-design-v3
description: 将已通过 G-REQ 的完整需求文档按 Story、Module 或 F-* 独立闭环范围转换为同目录 tech-design.md，并通过 G-DESIGN 后交给实施计划。
---

# 范围化技术设计 v3

## 执行

1. 验证 G-REQ scope hash；缺失或 stale 时停止，不重复询问仍有效的需求结论。
2. 一次批量读取 requirements、知识引用和代码证据。
3. 无功能点拆分时在 Story/Module 目录写一份 `tech-design.md`；存在 `F-*` 时只在对应 Feature 目录写设计，禁止同时生成父范围空壳。
4. D/C/V 是 tech-design 正文内部条目，不各建 Markdown。
5. 使用 `scripts/generate_tech_design.py` 保证 `scope_ref`、同目录路径、输入哈希和知识引用贯通；已有不同内容必须进入显式 revision 更新，不静默覆盖。
6. 生成动作不记录 G-DESIGN；每个 Story/Module/F-* 技术范围返回独立 confirmation package。多 Feature 不得合并成 Story 级伪确认；重新调用只复用各范围有效确认。

不写生产代码，不绕过代码/知识证据，不自动确认。
