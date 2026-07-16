# 产品 Wiki profile

整理产品资料、维护需求演进、分析影响或生成候选需求草稿时读取。本 profile 只扩展 OKF；PRD 目录和发布站点是来源或视图。

## 回答模型

产品库同时保存并连接：

1. 当前事实：术语、领域、模块、能力、规则和边界；
2. 演进：需求、迭代和决策如何引入、修改、替代或废弃事实；
3. 证据：PRD、设计、原型、发布记录和确认结论的原路径与版本。

## 类型与身份

| `type` | 稳定身份 | 核心关系 |
|---|---|---|
| `Product Term` | 规范术语 | belongs_to、related |
| `Product Domain` | 业务领域 | contains module/capability |
| `Product Module` | 稳定模块 | belongs_to、contains capability |
| `Product Capability` | 用户可感知能力 | implemented_by、changed_in |
| `Product Requirement` | 唯一需求 ID | affects、supersedes、related、delivered_in |
| `Product Iteration` | 发布/迭代 ID | includes requirement、changes capability |
| `Product Decision` | 唯一决策 ID | constrains |
| `Product Source` | 路径/URI + 版本 | supports |

需求页文件名为 `<ID>-<slug>.md`，并增加：

```yaml
id: REQ-20260716-001
requirement_status: proposed
products: [product-a]
modules: [rules-center]
capabilities: [rule-publishing]
iteration: v1.2.0
supersedes: []
related_requirements: []
```

schema 定义 `requirement_status` 枚举，至少包含 `proposed/confirmed/delivered/superseded/rejected`。无 ID 时按 schema 生成稳定临时 ID。每个需求有独立规范页；`requirements/index.md` 只导航。

## 单来源摄入与对账

处理一个产品文件时，完整提取其文档类型、ID、版本、日期、状态、模块、能力和显式关系；统一别名后按 ID、能力、目标和历史链合并规范对象，同时保留该来源。只更新本文件影响的 capability、requirement 替代链和 iteration；跨文件冲突进入 review backlog。

每个文档候选填写 `object_disposition: contains|none` 和 `objects`；顶层对象登记 `type/id/title/source_paths/target`。每次事务和里程碑都对账“来源识别对象 = coverage.objects = 非索引 OKF 规范对象”。

扫描发现的 REQ/PRD/RULE/DEC/ITER ID 必须登记为对象；仅为引用时用精确 evidence 记录 override。命中对象提示却标 `none` 的来源必须有依据并进入 review backlog。一个文件含多个对象时分别登记；重复 ID 或标题冲突不得静默合并。

## 新需求查询

1. 从新诉求提取用户、问题、产品、模块、能力、术语、约束和结果，以 glossary 展开别名；
2. 召回 module、capability、requirement、iteration、decision，读取当前事实和完整 `supersedes` 链；
3. 回到原始来源核验关键结论，识别重复、冲突、历史取舍、可复用范围和受影响能力；
4. 输出需求上下文包：现状、相关对象、迭代时间线、约束/非目标、可复用验收、冲突、缺口和来源；
5. 用户需要时再生成候选草稿，区分知识事实、建议和待确认项。草稿可存为 `draft`，但不改变库外需求状态。

只返回关键词命中文件列表不算完成；上下文和草稿的背景、范围与约束必须可回溯，替代链必须完整。
