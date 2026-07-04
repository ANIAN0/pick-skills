---
name: project-knowledge
description: 维护当前项目的 OKF 兼容 `project-kb/`，并把它建设为项目文档站的源内容。用户要求初始化、迁移、查询、健康检查、生成文档站视图，或归档已验证项目结论时使用；不管理全局或跨项目知识库。
---

# 项目知识库

`project-knowledge` 只维护当前项目根目录下的 `project-kb/`。把它作为项目级 Open Knowledge Format（OKF）bundle 和项目文档站源内容：内容可由人直接阅读、由 Agent 解析、由版本控制比较、渲染成可浏览视图，并能脱离专用工具使用。

## 触发与边界

使用本 skill：

- 用户要求初始化、迁移、查询、读取、搜索、验证、健康检查或可视化当前项目的 `project-kb/`。
- 用户要求建设、刷新或审计当前项目的文档站导航内容。
- 当前任务明确要求把已验证的项目结论归档为长期知识。
- 其他 skill 需要复用或沉淀当前项目知识，并明确调用 `project-knowledge`。

不使用本 skill：

- 目标不是当前项目根目录下的 `project-kb/`。
- 待写入内容没有经过验证，或没有后续复用价值。
- 用户要处理的对象不是知识库，而是研发阶段文档、任务状态或确认流程。

## 存储与路径契约

默认 bundle 位于真实项目根目录的 `project-kb/`。最小结构只包含：

```text
project-kb/
├── index.md
├── log.md
└── code/
    └── index.md
```

按知识内容分类，不按需求、方案、任务、执行或验收阶段分类。出现对应知识时再创建目录及其 `index.md`：

- `domain/`：术语、业务规则、核心对象和长期有效的功能知识。
- `architecture/`：系统边界、模块职责、数据模型、接口契约和技术机制。
- `code/`：按源码相对路径镜像文件知识；`src/app.ts` 对应 `code/src/app.ts.md`。
- `decisions/`：重要且无法从当前代码直接推导的决策、理由和失效条件。
- `workflows/`：跨文件业务流、数据流、运行流和故障处理流程。

`type` 与目录的对应详见 [项目知识模板](references/project-templates.md) 的"概念类型"节；推荐 `Project Domain` / `Project Architecture` / `Project Code` / `Project Decision` / `Project Workflow` 五种，可按需扩展。frontmatter、链接、索引和日志规则见 [OKF 文件契约](references/okf-file-contract.md)。

文档站建设以 `project-kb/index.md` 和各级 `index.md` 作为导航源，以普通概念文档作为内容页。`viz.html` 是当前内置的单文件站点视图，可随时由 `viz` 重新生成；不要把 `viz.html` 当作知识源编辑。

## 执行步骤

命令示例中的 `<skill-dir>` 是本 skill 目录，也就是包含 `SKILL.md` 和 `scripts/` 的目录。

初始化当前项目知识库：

```text
python <skill-dir>/scripts/kb_cli.py init-project --project-root <真实项目根目录>
```

创建最小 bundle：`project-kb/index.md`、`project-kb/log.md`、`project-kb/code/index.md`。其他目录在写入第一个概念时按需创建。初始化不依赖项目根目录的 `PROJECT_RULES.md`；项目有规则文件时可手动加一条链接到 `project-kb/index.md`，本 skill 不做强制校验。

写入或更新概念：

1. 确认真实项目根目录；只有用户明确要求初始化，或当前任务明确要求归档且项目根已确认时，才自动初始化缺失的最小 `project-kb/`。
2. 读取根 `index.md`、相关目录 `index.md` 和已有概念；必要时搜索 `project-kb/**/*.md`，优先更新已有同主题条目。
3. 读取窄范围项目证据：源码、测试、配置、运行结果、已确认阶段文档或可靠调研材料。只验证会写入正文的关键事实。
4. 自动选择目录和路径；只有分类归属或事实冲突会导致错误写入时才提问。
5. 新建或更新概念。更新时先读取旧文件并语义合并，保留仍然有效的 frontmatter 扩展字段、正文结论、链接和证据。
6. 用 `write-concept` 落盘，或在迁移/修复场景手工编辑。
7. 检查本次新增或更新内容没有自己造成的本地断链。
8. 跑 `validate-project`；`errors` 非空时报告诊断，不自动重试。
9. 只有当前任务明确给出来源文档和归档状态块时，才回写来源文档；否则只在最终回复中简述路径和结果。

```text
python <skill-dir>/scripts/kb_cli.py write-concept \
  --project-root <真实项目根目录> \
  --path <子目录>/<slug>.md \
  --frontmatter '<JSON 或 YAML>' \
  --content '<Markdown 正文>' \
  --mode create|update
```

`write-concept` 会同步父目录 `index.md` 和 `log.md`。`--mode create` 目标已存在时报错；`--mode update` 目标不存在时报错。

读取与查询：

```text
python <skill-dir>/scripts/kb_cli.py list-kb   --project-root <真实项目根目录> --path <可选子目录>
python <skill-dir>/scripts/kb_cli.py read-kb   --project-root <真实项目根目录> --path <相对 project-kb>
python <skill-dir>/scripts/kb_cli.py search-kb --project-root <真实项目根目录> --query <正则> --path <可选>
```

只读子命令统一以 JSON 输出。简单情况也可直接读取 `project-kb/**/*.md`，不强制走 CLI。

健康检查、迁移和可视化：

```text
python <skill-dir>/scripts/kb_cli.py validate-project --project-root <真实项目根目录>
python <skill-dir>/scripts/kb_cli.py viz --project-root <真实项目根目录> --output <可选>
```

用户要求审计时读取 [质量标准](references/quality-criteria.md)。先运行 `validate-project` 检查 frontmatter、保留文件、wiki link、目录结构和本地链接，再抽查概念是否与当前项目一致。`viz` 默认写到 `<project-kb>/viz.html`；该文件是可删除重建的视图文件，不参与 `validate-project` 校验，也不视作概念文档。

建设或刷新项目文档站时：

1. 先按读取与查询步骤确认现有 `project-kb/` 内容，不为填页面数量创建低价值概念。
2. 补齐根 `index.md` 到主要分类的入口，确保新读者能从根入口进入代码、架构、领域、决策和工作流等已有内容。
3. 补齐各分类 `index.md` 的条目摘要；摘要必须说明页面用途，而不是只重复标题。
4. 对缺少长期价值内容的页面，优先合并到更宽的概念或目录索引，不制造薄页面。
5. 运行 `validate-project`；需要浏览视图时再运行 `viz` 生成或刷新 `viz.html`。

旧知识库迁移时：

1. 保留原文件，先建立迁移清单，不覆盖未知用户内容。
2. 将根 `README.md`、目录 `README.md` 和 `changelog.md` 分别迁移为 `index.md`、目录 `index.md` 和 `log.md`。
3. 为普通概念补充 `type` 等 frontmatter，将 wiki link 改为可解析的标准 Markdown 链接。
4. 把非代码知识归入正确目录；不为追求格式一次性制造空概念。
5. 校验链接和项目事实后再删除被完整替代的旧文件。

## 校验与门槛

写入知识前必须同时满足：

- 结论已由当前代码、配置、测试、运行结果、已确认阶段结论或可靠项目材料验证。
- 结论对后续需求、设计、修改、影响分析、维护或验收具有持续价值。
- 结论能归入一个稳定概念，而不是临时讨论、任务状态或未确认推断。

报告完成前逐项自检：

- 范围仅限当前项目。
- 概念有项目证据。
- 本 skill 要求的 frontmatter 字段完整。
- 本次写入没有新增断链。
- 未知字段被保留。
- 索引和日志已同步。
- 根入口和分类索引能作为项目文档站导航使用。
- 没有复制过程文档、写入临时状态或把推断冒充事实。

`validate-project` 必须能解析 YAML frontmatter；校验器需要 PyYAML，依赖声明位于 `scripts/requirements.txt`。缺少依赖时必须报告错误，不能用正则近似解析后返回有效。

## 失败与回退

`kb_cli.py` 任一子命令返回 `error` 非空或 `errors` 非空时即为失败；报告诊断信息，由当前任务决定重试、停止或标记阻塞。不要在失败处理中替研发阶段修改任务状态或用户确认。

如果 `project-knowledge` 被其他 skill 作为可选协作项调用但不可用，调用方应跳过沉淀或复用步骤并记录原因；本 skill 不要求调用方失败。

## 提问契约

能从项目文件、现有知识库和工具输出确认的信息自行检查。只有无法确定真实项目根目录、知识归属或事实冲突会导致错误写入时才提问；问题放在回复最后的 `## 需要你确认` 区块，一次只问一个并给出推荐处理和影响。

## 证据与完成定义

完成写入、迁移、文档站刷新或健康检查时，必须报告实际处理的 `project-kb/` 路径、运行过的校验命令或未能运行的原因、是否生成了 `viz.html`、以及仍存在的 errors/warnings。`done` 只能用于校验通过且写入结果已落盘的情况；写入已完成但校验无法运行或依赖缺失时，结果是 `not_verified`。

## 边界声明

- 不管理全局知识库、跨项目报告、时效传播、自动沉淀队列或外部 Web 服务；项目文档站只以 `project-kb/` 内容和内置 `viz.html` 视图为边界。
- 不替研发阶段修改入口结论、任务状态或用户确认。
- 不自动扫描并为全部代码生成低价值文档。
- 不把 OKF 的宽容读取规则误作写入质量标准；新写入内容必须满足本 skill 的证据和链接要求。
