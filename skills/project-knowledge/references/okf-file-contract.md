# OKF 文件契约

只在创建、更新、迁移或修复 OKF bundle Markdown 文件时读取。

本 skill 使用两层契约：

- OKF 基础层用于应用对接和外部 bundle 宽容读取。非保留概念文档只要求可解析 YAML frontmatter 和非空 `type`；`title`、`description`、`resource`、`tags`、`timestamp` 和未知字段都按可选扩展处理。
- 项目 profile 层用于本 skill 新写入的 `project-kb/`。为了让人和 agent 稳定复用，普通概念必须额外包含非空 `title`、`description`；`Project Code` 还必须包含非空 `source_path`。

## 普通概念文档

每个非 `index.md`、非 `log.md` 的 Markdown 概念文档必须以 YAML frontmatter 开头。项目 profile 写入时包含非空 `type`、`title`、`description`：

```yaml
---
type: Project Workflow
title: 订单导入流程
description: 描述订单文件从上传到结果反馈的完整处理流程。
tags: [orders, import]
timestamp: 2026-06-21T10:00:00+08:00
---
```

正文按概念类型组织，没有固定必需章节；需要模板时从 `SKILL.md` 直接进入项目知识模板参考文件。读取外部 OKF bundle 时，不得因为缺少 `title`、`description` 或未知 `type` 拒绝消费。

## 路径与身份

- 文件在 bundle 内的相对路径就是概念身份。不要无理由移动或复制同一概念。
- 项目 profile 的 `type: Project Code` 必须含 `source_path` 保存项目相对路径；正文至少说明文件承担的可验证能力、关键逻辑与边界、强关联文件及原因、相关测试及覆盖内容、修改风险和验证建议。不要只复述类名、函数名或目录结构。
- `quickstart.md` 是项目 profile 的阅读入口，使用 `type: Project Overview`，负责解释项目知识版图并链接主要分类；它仍是普通 OKF 概念文档，不是保留文件。

## 链接与证据

- 使用普通 Markdown 链接表达关系，不使用 `[[wiki link]]`。
- 优先采用从当前文件可解析的相对链接，并在链接周围文字说明关系。
- 只有强关联需要补反向链接；引用、导航和来源链接不机械补反链。
- 不堆叠没有语义说明的链接。
- 外部事实和项目结论必须能追溯到来源。项目文件、阶段文档和调研报告使用普通链接作为项目证据；`# Citations` 是推荐写法，不是固定必需章节。

## 索引与日志

- 外部 OKF bundle 的 `index.md` 和 `log.md` 是可选文件；消费侧不能因为缺失而拒绝 bundle。
- 项目 profile 的根 `index.md` 推荐使用 `okf_version: "0.1"` 声明版本并提供渐进导航；外部 bundle 没有该声明时只提示 warning。
- 子目录 `index.md` 不使用 frontmatter，只列出现有概念及一句话摘要。
- 项目 profile 的 `log.md` 按 `YYYY-MM-DD` 倒序记录有意义的创建、更新、移动和废弃，不记录读取操作。
