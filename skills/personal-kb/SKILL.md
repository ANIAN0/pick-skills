---
name: personal-kb
description: 维护当前项目的 OKF 兼容 `project-kb`。用户要求初始化、迁移、查询、健康检查，或归档已验证项目结论时使用；不管理全局或跨项目知识库。
---

# 项目知识库

只维护当前项目根目录下的 `project-kb/`。把它作为一个项目级 Open Knowledge Format（OKF）bundle：内容可由人直接阅读、由 Agent 解析、由版本控制比较，并能脱离专用工具使用。

## 存储结构

```text
project-kb/
├── index.md
├── log.md
├── domain/
├── architecture/
├── code/
├── decisions/
└── workflows/
```

- `domain/`：术语、业务规则、核心对象和长期有效的功能知识。
- `architecture/`：系统边界、模块职责、数据模型、接口契约和技术机制。
- `code/`：按源码相对路径镜像文件知识；`src/app.ts` 对应 `code/src/app.ts.md`。
- `decisions/`：重要且无法从当前代码直接推导的决策、理由和失效条件。
- `workflows/`：跨文件业务流、数据流、运行流和故障处理流程。

根 `index.md`、`log.md` 和 `code/index.md` 是最小结构；其他目录及其 `index.md` 在出现对应知识时创建。按知识内容分类，不按需求、方案、任务、执行或验收阶段分类。

`type` 与目录的对应详见 [项目知识模板](references/project-templates.md) 的"概念类型"节；推荐 `Project Domain` / `Project Architecture` / `Project Code` / `Project Decision` / `Project Workflow` 五种，可按需扩展。

## 初始化

```text
python skills/personal-kb/scripts/kb_cli.py init-project --project-root <真实项目根目录>
```

创建最小 bundle：`project-kb/index.md`、`project-kb/log.md`、`project-kb/code/index.md`。其他目录在写入第一个概念时按需创建。**不依赖项目根目录的 `PROJECT_RULES.md`**；项目有规则文件时可手动加一条链接到 `project-kb/index.md`，本 skill 不做强制校验。

## 写入概念

当当前任务需要把已验证结论写入 `project-kb/` 时，按以下顺序处理：

1. 确认真实项目根目录；只有用户明确要求初始化，或当前任务明确要求归档且项目根已确认时，才自动初始化缺失的最小 `project-kb/`。
2. 读取根 `index.md`、相关目录 `index.md` 和已有概念；必要时搜索 `project-kb/**/*.md`，优先更新已有同主题条目。
3. 读取窄范围项目证据：源码、测试、配置、运行结果、已确认阶段文档或可靠调研材料。只验证会写入正文的关键事实。
4. 自动选择目录和路径；只有分类归属或事实冲突会导致错误写入时才提问。
5. 新建或更新概念。更新时先读取旧文件并语义合并，保留仍然有效的 frontmatter 扩展字段、正文结论、链接和证据。
6. 用 `kb_cli.py write-concept` 落盘，或在迁移/修复场景手工编辑。
7. 检查本次新增或更新内容没有自己造成的本地断链。
8. 跑 `validate-project`；`errors` 非空时报告诊断，不自动重试。
9. 只有当前任务明确给出来源文档和归档状态块时，才回写来源文档；否则只在最终回复中简述路径和结果。

正文按概念类型组织，没有固定必需章节；frontmatter、链接、引用等格式约束见 [OKF 文件契约](#okf-文件契约)。

`kb_cli.py write-concept` 是确定性落盘工具，会同步父目录 `index.md` 和 `log.md`：

```text
python skills/personal-kb/scripts/kb_cli.py write-concept \
  --project-root <真实项目根目录> \
  --path <子目录>/<slug>.md \
  --frontmatter '<JSON 或 YAML>' \
  --content '<Markdown 正文>' \
  --mode create|update
```

`--mode create` 目标已存在时报错；`--mode update` 目标不存在时报错。

## 读与查询

```text
python skills/personal-kb/scripts/kb_cli.py list-kb   --project-root <真实项目根目录> --path <可选子目录>
python skills/personal-kb/scripts/kb_cli.py read-kb   --project-root <真实项目根目录> --path <相对 project-kb>
python skills/personal-kb/scripts/kb_cli.py search-kb --project-root <真实项目根目录> --query <正则> --path <可选>
```

只读子命令统一以 JSON 输出。简单情况也可直接用 Read 工具读 `project-kb/**/*.md`，不强制走 CLI。

## 验证

```text
python skills/personal-kb/scripts/kb_cli.py validate-project --project-root <真实项目根目录>
```

检查 frontmatter、保留文件（旧 `README.md` / `changelog.md`）、`[[wiki link]]`、目录结构和本地链接。本 skill 管理的普通概念必须包含非空 `type`、`title`、`description`；warnings 中断链不阻塞校验（OKF v0.1 §9 允许消费侧不拒绝 bundle）。

## 可视化

```text
python skills/personal-kb/scripts/kb_cli.py viz --project-root <真实项目根目录> --output <可选>
```

把 `project-kb/` 渲染成单文件 HTML（cytoscape 图 + 详情面板），默认写到 `<project-kb>/viz.html`。`viz.html` 是视图文件，可随时删除重新生成；不参与 `validate-project` 校验，也不视作概念文档。

## OKF 文件契约

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

- 文件在 bundle 内的相对路径就是概念身份。不要无理由移动或复制同一概念。
- 使用普通 Markdown 链接表达关系，不使用 `[[wiki link]]`。优先采用从当前文件可解析的相对链接，并在链接周围文字说明关系。
- 只有强关联需要补反向链接；引用、导航和来源链接不机械补反链。
- 不堆叠没有语义说明的链接。
- 外部事实和项目结论必须能追溯到来源。项目文件、阶段文档和调研报告使用普通链接作为项目证据；`# Citations` 是推荐写法，不是固定必需章节。
- `type: Project Code` 必须含 `source_path` 保存项目相对路径；正文至少说明：文件承担的可验证能力、关键逻辑与边界、强关联文件及原因、相关测试及覆盖内容、修改风险和验证建议。不要只复述类名、函数名或目录结构。

根 `index.md` 使用 `okf_version: "0.1"` 声明版本并提供渐进导航。子目录 `index.md` 不使用 frontmatter，只列出现有概念及一句话摘要。`log.md` 按 `YYYY-MM-DD` 倒序记录有意义的创建、更新、移动和废弃，不记录读取操作。

## 写入门槛

只写入同时满足以下条件的知识：

- 已由当前代码、配置、测试、运行结果、已确认阶段结论或可靠项目材料验证。
- 对后续需求、设计、修改、影响分析、维护或验收具有持续价值。
- 能归入一个稳定概念，而不是临时讨论、任务状态或未确认推断。

不复制完整阶段入口、调研报告、审查报告、原始日志或一次性搜索结果。需要沉淀时，从来源中提取长期有效的结论，写入相应概念，并在正文链接原始证据；能修改来源文档时补回知识概念链接。

## 失败处理

`kb_cli.py` 任一子命令返回 `error` 非空或 `errors` 非空时即为非零退出码；报告诊断信息，由当前任务决定重试、停止或标记阻塞。本 skill 不替研发阶段修改任务状态或用户确认。

## 健康检查与迁移

用户要求审计时读取 [质量标准](references/quality-criteria.md)。先运行 `validate-project` 检查 frontmatter、保留文件、wiki link、目录结构和本地链接，再抽查概念是否与当前项目一致。

旧知识库迁移时：

1. 保留原文件，先建立迁移清单，不覆盖未知用户内容。
2. 将根 `README.md`、目录 `README.md` 和 `changelog.md` 分别迁移为 `index.md`、目录 `index.md` 和 `log.md`。
3. 为普通概念补充 `type` 等 frontmatter，将 wiki link 改为可解析的标准 Markdown 链接。
4. 把非代码知识归入正确目录；不为追求格式一次性制造空概念。
5. 校验链接和项目事实后再删除被完整替代的旧文件。

## 提问与完成

能从项目和知识库确认的信息自行检查。只有无法确定真实项目根目录、知识归属或事实冲突会导致错误写入时才提问；问题放在回复最后的 `## 需要你确认` 区块，一次只问一个并给出推荐处理和影响。

报告完成前自检：范围仅限当前项目；概念有项目证据；本 skill 要求的 frontmatter 字段完整；本次写入没有新增断链；未知字段被保留；索引和日志已同步；没有复制过程文档、写入临时状态或把推断冒充事实。

校验器需要 PyYAML；缺少依赖时必须报告错误，不能用正则近似解析后返回有效。依赖声明位于 `scripts/requirements.txt`。

## 边界

- 不管理全局知识库、跨项目报告、时效传播、自动沉淀队列、图谱或 Web 入口。
- 不替研发阶段修改入口结论、任务状态或用户确认。
- 不自动扫描并为全部代码生成低价值文档。
- 不把 OKF 的宽容读取规则误作写入质量标准；新写入内容必须满足本 Skill 的证据和链接要求。
