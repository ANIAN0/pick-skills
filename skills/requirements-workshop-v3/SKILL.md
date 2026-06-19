---
name: requirements-workshop-v3
description: 将项目想法、功能扩展或模糊请求拆分为项目研发 v3 的用户故事、需求、能力、验证、UI 规格和原型输入节点，同时保留用户要求的交付物形态。用于完整产品或 Skill 改造、已确认工作的扩展，以及技术设计前的需求澄清；当需求和验证已经明确时，识别 task/bug 快捷入口，不强制执行完整需求阶段。
---

# 需求工作坊 v3

保留用户要求的交付物，再把决策拆分为可独立确认的图谱节点。不要创建新的阶段级“需求简报”。

## 必读内容

- 读取 `project-development-v3-common` 的节点 Schema、关系注册表、生命周期和确认协议。
- 选择入口模式或确认节点前，读取 [需求工作流](references/requirements-workflow.md)。
- 仅在请求涉及页面、视觉状态、UI 文档或原型交付物时，读取 [UI 与原型适配](references/ui-prototype-adapter.md)。
- 节点包含可通过外部资料回答的不确定性时，调用 `project-research-v3`。

## 入口路由

- `full`：从新用户故事开始，拆分完整交付物。
- `extension`：在有效且已确认的既有用户故事或需求下新增需求节点；保留未受影响的确认，不重复确认。
- `task` / `bug`：需求和验证已经明确时转入快捷流程。只补缺失的责任节点，不制造完整故事树。

## 硬规则

- 拆分前记录 `deliverable_type`、`deliverable_components`、`entry_points` 和 `completion_boundary`。
- 用户要求创建或改造 Skill/Skill 套件时，保持 `deliverable_type: skill-suite`，不得改写为通用应用、CLI 或管理产品。
- 每个需求和能力节点只承担一个决策责任。
- 同时创建同父级的能力与验证节点；验证通过 `verifies` 指向能力。
- 有效确认哈希直接复用，只询问已变化或尚未解决的语义。
- 完整调研只进入全局知识报告；项目节点只保存摘要和稳定关系。
- 停在需求及 UI/原型输入，不设计生产架构、不写实现代码。

## 输出

将节点写入当前项目图谱，并报告新增或更新的节点 ID、剩余阻塞问题、调研分支、确认状态和下一个允许进入技术设计的节点。
