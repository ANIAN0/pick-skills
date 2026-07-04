# OKF 文件契约

只在创建、更新、迁移或修复 `project-kb/` Markdown 文件时读取。

## 普通概念文档

每个非 `index.md`、非 `log.md` 的 Markdown 概念文档必须以 YAML frontmatter 开头，并包含非空 `type`、`title`、`description`：

```yaml
---
type: Project Workflow
title: 订单导入流程
description: 描述订单文件从上传到结果反馈的完整处理流程。
tags: [orders, import]
timestamp: 2026-06-21T10:00:00+08:00
---
```

正文按概念类型组织，没有固定必需章节；需要模板时从 `SKILL.md` 直接进入项目知识模板参考文件。

## 路径与身份

- 文件在 bundle 内的相对路径就是概念身份。不要无理由移动或复制同一概念。
- `type: Project Code` 必须含 `source_path` 保存项目相对路径；正文至少说明文件承担的可验证能力、关键逻辑与边界、强关联文件及原因、相关测试及覆盖内容、修改风险和验证建议。不要只复述类名、函数名或目录结构。

## 链接与证据

- 使用普通 Markdown 链接表达关系，不使用 `[[wiki link]]`。
- 优先采用从当前文件可解析的相对链接，并在链接周围文字说明关系。
- 只有强关联需要补反向链接；引用、导航和来源链接不机械补反链。
- 不堆叠没有语义说明的链接。
- 外部事实和项目结论必须能追溯到来源。项目文件、阶段文档和调研报告使用普通链接作为项目证据；`# Citations` 是推荐写法，不是固定必需章节。

## 索引与日志

- 根 `index.md` 使用 `okf_version: "0.1"` 声明版本并提供渐进导航。
- 子目录 `index.md` 不使用 frontmatter，只列出现有概念及一句话摘要。
- `log.md` 按 `YYYY-MM-DD` 倒序记录有意义的创建、更新、移动和废弃，不记录读取操作。
