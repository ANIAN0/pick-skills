# 项目知识模板

只在初始化、迁移或创建新类型概念时读取。所有链接使用普通 Markdown 链接。

## 最小 bundle

```text
project-kb/
├── index.md
├── log.md
└── code/
    └── index.md
```

根 `index.md`：

```markdown
---
okf_version: "0.1"
---

# 项目知识库

本知识库保存当前项目长期有效、经过验证的知识。

## 入口

- [代码知识](code/index.md) - 按源码路径维护的职责、逻辑和测试映射。
```

`log.md`：

```markdown
# 项目知识库更新记录

## YYYY-MM-DD

- **Creation**: 初始化项目级 OKF 知识库。
```

`code/index.md`：

```markdown
# 代码知识

按源码相对路径镜像项目代码知识。

## 条目

- [src/example.ts](src/example.ts.md) - 示例文件承担的项目能力。
```

## 概念类型

推荐使用以下自解释类型；必要时可以增加新类型：

| 目录 | 推荐 `type` | 内容 |
|---|---|---|
| `domain/` | `Project Domain` | 术语、业务规则、核心对象、功能能力 |
| `architecture/` | `Project Architecture` | 系统边界、模块职责、模型和接口契约 |
| `code/` | `Project Code` | 源码职责、逻辑、关联和测试映射 |
| `decisions/` | `Project Decision` | 决策、取舍、影响和失效条件 |
| `workflows/` | `Project Workflow` | 跨文件流程、分支、失败和验证 |

## 通用概念

```markdown
---
type: Project Domain
title: 概念标题
description: 一句话说明该知识是什么以及有什么作用。
tags: []
timestamp: YYYY-MM-DDTHH:MM:SS+08:00
---

# 概念标题

写入经过验证、长期有效的结论。

## 适用边界

说明适用和不适用条件。

## 关联知识

- [相关概念](../workflows/example.md) - 说明关系。

# Citations

- [项目证据](../../workplace/path/to/evidence.md)
```

## 代码概念

`src/example.ts` 对应 `project-kb/code/src/example.ts.md`：

```markdown
---
type: Project Code
title: src/example.ts
description: 一句话说明该文件承担的项目能力。
source_path: src/example.ts
tags: []
timestamp: YYYY-MM-DDTHH:MM:SS+08:00
---

# src/example.ts

## 功能与职责

## 关键逻辑与边界

## 关联知识

- [相关文件](related.ts.md) - 说明强关联原因。

## 测试与验证

## 修改注意事项

# Citations

- [源码](../../../src/example.ts)
```

## 决策概念

```markdown
---
type: Project Decision
title: 决策标题
description: 一句话说明作出的选择。
tags: []
timestamp: YYYY-MM-DDTHH:MM:SS+08:00
---

# 决策标题

## 背景

## 决策

## 替代方案与取舍

## 影响与失效条件

## 关联知识

# Citations
```

## 工作流概念

```markdown
---
type: Project Workflow
title: 流程标题
description: 一句话说明流程的入口和结果。
tags: []
timestamp: YYYY-MM-DDTHH:MM:SS+08:00
---

# 流程标题

## 目标与边界

## 参与概念

## 执行顺序

## 关键分支与失败行为

## 测试与验证

# Citations
```

## 命名与索引

- 概念使用稳定、简短、能表达主题的英文文件名；代码概念保留完整源码文件名并追加 `.md`。
- 新增概念后，在最近目录 `index.md` 添加标题、相对链接和一句话描述。
- 根 `index.md` 只导航到已有分类，不预建空目录。
- 从阶段文档沉淀知识时链接原文，不复制整份文档；能修改原文时补回知识概念链接。
