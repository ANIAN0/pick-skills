---
name: requirements-workshop-v3
description: 将项目想法或功能请求整理为自适应层级的完整 requirements 文档。先确认整体 User Story，再按真实边界可选拆分最多 3 个模块和模块内最多 10 个独立闭环功能点，并通过 G-REQ 后交给技术设计。
---

# 自适应需求工作坊 v3

保留用户要求的交付物形态，把 R/A/F 等条目写入少量完整需求文档，不拆成大量 Markdown。

## 必读

- 读取 `project-development-v3-common` 的文档节点、关系、层级和确认协议。
- 执行前读取 [自适应需求工作流](references/requirements-workflow.md)。

## 执行

1. 明确 deliverable 的 type、format、location、audience。
2. 创建并请求确认整体 Story requirements。
3. 仅按真实边界创建可选模块 requirements；`F-*` 保存在模块正文。
4. 使用内部脚本 `scripts/generate_requirements.py` 做路径、数量和 G-REQ 确定性门禁；重复生成只允许字节一致的幂等结果，已有内容不同则报告 revision conflict，禁止覆盖。
5. 生成动作不接受 G-REQ 身份；先返回 package document IDs，再由独立用户确认动作写入 G-REQ。哈希有效后重新调用会直接返回 ready，不重复提问。

## 禁止

- 不为每个 Requirement、Capability、Verification 或 F-* 创建 Markdown。
- 不预建空 modules/features。
- 不自动确认 Story、数量超限决策或 G-REQ。
- 不在需求阶段设计技术实现。
