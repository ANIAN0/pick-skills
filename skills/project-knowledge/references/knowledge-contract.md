# OKF 知识契约

任何 OKF 初始化、结构设计、概念写入、迁移或严格校验都读取。

## Bundle

```text
<okf-root>/
├── index.md              # 根 frontmatter: okf_version: "0.1"
├── purpose.md            # 读者、问题、范围、优先级、可用里程碑
├── INSTRUCTIONS.md       # Agent 查询、写入和维护规则
├── log.md                # 日期倒序的有效变更
└── _meta/
    ├── schema.md         # 类型、字段、关系、状态、路径
    ├── state.json        # design/growing 阶段与设计门槛
    ├── sources.md        # 多来源时的范围与优先级
    ├── coverage.json     # 完整来源清单
    ├── capture-registry.json # Capture 身份与不可变来源指纹
    ├── ingest-queue.json # 持久化摄入与 review backlog
    ├── ingest/           # 逐来源 analysis artifact
    └── milestones/       # 可用范围、来源指纹与审查证据
```

分类目录及其 `index.md` 只在有内容时创建。现有 Wiki 作为独立发布视图保留；它的导航和 frontmatter 不改变 OKF bundle，发布页与 OKF 概念页维护明确映射。

## 概念页

普通概念页使用 YAML frontmatter：

```yaml
---
type: Knowledge Type
title: 稳定标题
description: 页面回答的问题。
state: active
updated_at: 2026-07-16
sources: [path/to/source]
---
```

公共必填字段为 `type/title/description/state/updated_at/sources`。`sources` 使用可访问的精确来源；原创经验使用项目记录、实验结果或作者声明。schema 可增加 `id`、`tags`、`created_at`、`review_after` 和 profile 字段；更新时保留未知字段。

公共 `state`：`draft` 未核验；`active` 当前有效；`superseded` 已被替代并链接替代项；`deprecated` 不再推荐并说明原因；`archived` 仅供历史检索。业务状态使用独立字段。

## 身份、关系与来源

- 一个稳定概念只有一个规范路径；标题变化不改变身份。
- 原始来源、当前结论和历史版本是不同对象，以普通 Markdown 链接和 schema 定义的强关系连接。
- 移动概念前更新入链、索引和替代关系；弱相关不机械补反链。
- `_meta/sources.md` 声明来源的权威范围、版本、日期、所有者和敏感性。冲突先比较适用版本与范围；无法裁决时保留冲突并使用 `draft`。

`purpose.md` 定义主要读者、3–7 个关键问题、来源/知识边界、队列优先级和 operational 条件。`INSTRUCTIONS.md` 让新 Agent 定位根入口、schema、查询顺序、稳定身份、可用状态、单来源事务、索引/日志同步项和公开边界。

对话 Capture 属于 OKF 根外的原始来源；registry 在控制面绑定其身份和原始指纹，`inbox/` 只是可选的人类浏览投影。查询时同时检查来源任务状态和 claim 的资格，不能把 `reported` 内容回答成技术事实，也不能用 `normative` 证明当前实现。

## 读写兼容

读取外部 OKF 时使用宽容消费契约：概念页只要求可解析 frontmatter 和非空 `type`；未知字段/类型原样保留，缺少入口或断链只报告 warning。本 skill 的写入仍必须通过上述严格契约，宽容读取不能作为交付证据。
