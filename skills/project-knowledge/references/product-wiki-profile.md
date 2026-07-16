# 产品 Wiki profile

只在整理产品资料、维护需求与迭代关系、做需求影响分析或生成候选需求草稿时读取。

## 回答模型

产品 Wiki 必须同时保存三层信息：

1. **当前产品事实**：术语、领域、模块、能力、规则和边界。
2. **演进关系**：需求、迭代和决策如何引入、修改、替代或废弃当前事实。
3. **原始证据**：PRD、设计、原型、发布记录和确认结论的原路径与版本。

只按版本目录堆放 PRD 无法稳定回答“现在是什么”和“为什么变成这样”；只写当前能力又无法追溯历史。三层通过 ID 和关系链接连接。

## 推荐结构

```text
<kb-root>/
├── index.md
├── INSTRUCTIONS.md
├── log.md
├── _meta/
├── glossary/
├── domains/
├── modules/
├── capabilities/
├── requirements/
├── iterations/
├── decisions/
└── sources/
```

已有 PRD 仓库可以继续作为 `sources`，产品 Wiki 在独立目录建立规范页和关系索引；迁移时保留原目录与 Git 历史。

## 内容类型与关系

| `type` | 稳定身份 | 必须回答 | 关键关系 |
|---|---|---|---|
| `Product Term` | 规范术语 | 定义、别名、易混概念 | belongs_to、related |
| `Product Domain` | 业务领域 | 目标、参与者、核心规则与边界 | contains module/capability |
| `Product Module` | 稳定产品模块 | 职责、用户、入口、边界、当前能力 | belongs_to domain、contains capability |
| `Product Capability` | 用户可感知能力 | 当前行为、规则、状态、限制、验证方式 | implemented_by requirement、changed_in iteration |
| `Product Requirement` | 唯一需求 ID；无 ID 时生成稳定临时 ID | 问题、目标、范围、非目标、状态、验收、影响 | affects capability、supersedes、related、delivered_in |
| `Product Iteration` | 发布版本或有边界的迭代 ID | 时间、目标、需求清单、用户可见变化、遗留项 | includes requirement、changes capability |
| `Product Decision` | 唯一决策 ID | 背景、选择、取舍、影响、重评条件 | constrains module/capability/requirement |
| `Product Source` | 原文件路径或外部 URI + 版本 | 来源类型、日期、权威性、覆盖范围 | supports |

关系用正文中的语义化 Markdown 链接表达；需要稳定检索的强关系同时写入 schema 定义的字段。

## 需求元数据

需求规范页在通用字段之外至少包含：

```yaml
type: Product Requirement
id: REQ-20260715-001
requirement_status: proposed
products: [product-a]
modules: [rules-center]
capabilities: [rule-publishing]
iteration: v1.2.0
supersedes: []
related_requirements: []
sources:
  - ../sources/path-to-prd.md
```

`requirement_status` 的枚举由本库 schema 定义，至少区分 proposed、confirmed、delivered、superseded、rejected。文件名使用 `<ID>-<slug>.md`，标题或 PRD 文件名变化不改变身份。历史 PRD 的修订记录留在来源；知识库需求页维护当前状态、关系和必要演进摘要。它是来源事实的可检索投影，不修改知识库外的研发流程状态。

## 导入与维护

导入每批产品资料时：

1. 建立来源清单，提取文档类型、ID、版本、日期、状态、模块、能力和显式关联。
2. 统一别名与术语，但保留原文用词以支持检索。
3. 为无稳定 ID 的需求生成临时 ID，并在 `_meta/schema.md` 记录生成规则。
4. 搜索同 ID、同能力、同目标和同一历史链，合并规范页，链接所有原始来源。
5. 更新受影响 capability 的当前事实、requirement 的替代链和 iteration 清单。
6. 把未确认、相互冲突或无法归属的内容列为缺口，不强行合并。

每个具有稳定身份的需求都建立独立知识库需求页；`requirements/index.md` 只负责导航，不能代替单需求页。索引必须从全量来源账本生成或核对：逐项链接精确来源或规范页，不使用目录链接和“同上”冒充来源；同一 ID 对应多个标题时先记录身份冲突，不静默合并或重复列为唯一需求。

新 PRD、确认状态、发布结果或需求废弃发生变化时触发同样的增量维护。一个版本目录的新增不等于完成；关系和当前能力页必须同步。

## 新需求检索与候选草稿

收到新需求描述后执行：

1. 提取目标用户、问题、产品、模块、能力、术语、约束和期望结果；用 glossary 展开别名。
2. 搜索 ID、标题、description、tags、别名和正文，召回相关 module、capability、requirement、iteration 与 decision。
3. 阅读能力的当前事实、所有有效相关需求、最近相关迭代、决策约束和完整 `supersedes` 链；回到原始来源核验关键结论。
4. 比较新诉求与现状，识别可复用范围、已有实现、历史取舍、冲突、重复需求、受影响能力和待确认问题。
5. 先形成“需求上下文包”：当前状态、相关需求及关系、迭代时间线、约束/非目标、可复用验收、冲突与缺口、来源路径。
6. 用户要求知识库直接给出初稿时，基于上下文包生成**候选需求草稿**，明确区分知识库事实、从事实推导的建议和需要用户确认的内容。候选草稿可以作为 `draft` 知识页保存，但不修改知识库外的研发路线图、阶段入口或确认状态。

完成标准：不能只返回关键词命中的文件列表；上下文包或候选草稿中的背景、范围和约束都能回溯到规范页或原始来源，替代链没有遗漏。
