---
name: workspace-setup
description: |
  快速配置和管理项目工作区。当用户提到工作区初始化、CLAUDE.md/AGENTS.md 管理、项目规则文件、项目知识库入口、项目研发 v3 图目录、全局研究知识库路径、配置文件同步、创建版本目录、归档旧版本或使用 npx skills 管理技能时触发此 skill。支持三层项目上下文结构并兼容初始化节点化研发目录。
---

# 工作区初始化 Skill

本 skill 管理所有项目都复用的工作区入口，并初始化项目独立维护的规则和知识库骨架。

## 三层结构

```
项目根目录/
├── AGENTS.md              ← 第 1 层：通用 AI 入口，所有项目内容一致
├── CLAUDE.md              ← 第 1 层：Claude 入口，通常只写 @AGENTS.md
├── PROJECT_RULES.md       ← 第 2 层：项目规则，每个项目独立维护
├── project-kb/            ← 第 3 层：项目知识库，每个项目独立维护
│   ├── README.md
│   └── code/              ← 按源码相对路径镜像的代码文件说明
│       └── README.md
├── workplace/             ← 需求、方案、计划、测试等过程文档
│   ├── global/            ← 跨迭代复用的过程资产、模板、脚本和说明
│   ├── test/              ← 跨迭代复用的测试方案、脚本、夹具和报告模板
│   ├── 1.0/
│   │   └── graph/
│   │       ├── stories/  ← Story/模块/功能点层级 Markdown 事实文档
│   │       └── .derived/ ← 可删除重建的索引和视图
│   └── archive/
├── skillconfig.json
└── skills/
    └── workspace-setup/
```

### 第 1 层：通用入口

`AGENTS.md` 和 `CLAUDE.md` 必须在所有项目保持一致，适合通过配置包统一同步。

职责：
- 声明通用协作、编码、验证和文档同步规则。
- 固定要求读取同级 `PROJECT_RULES.md`。
- 固定要求修改代码前读取 `project-kb/code/` 中对应的代码文件说明。

不应包含：
- 某个项目的目录说明。
- 某个项目的测试命令。
- 某个项目的业务、架构、依赖或部署规则。

### 第 2 层：项目规则

`PROJECT_RULES.md` 是每个项目独立维护的必读文档。

职责：
- 列出当前项目修改代码前必须知道的规则。
- 说明重要文件、重要目录和修改风险。
- 链接到第 3 层项目知识库。
- 记录项目级验证命令和定向测试策略。

### 第 3 层：项目知识库

`project-kb/` 是每个项目独立维护的知识库，由 `personal-kb` Skill 负责初始化、结构校验和持续维护。`workspace-setup` 必须调用 `personal-kb/scripts/kb_cli.py init-project`，不得复制知识库模板。

关键约定：
- `project-kb/code/` 按代码文件结构镜像。
- 每个代码文件对应一份说明文档。
- 说明文档记录功能点、相关文件、重要逻辑、测试文件和修改注意事项。
- 相关文件使用 Obsidian 双向链接。

## skillconfig.json

```json
{
  "workspace": {
    "current_version": "1.0",
    "workplace_dir": "workplace",
    "project_rules_file": "PROJECT_RULES.md",
    "project_kb_dir": "project-kb"
  },
  "knowledge": {
    "global_dir": "~/personal-kb"
  },
  "filebrowser": {
    "cli_config": "~/.config/filebrowser-cli/config.yaml"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `current_version` | string | 是 | 当前过程文档版本号 |
| `workplace_dir` | string | 否 | 过程文档目录，默认 `workplace` |
| `project_rules_file` | string | 否 | 项目规则文件，默认 `PROJECT_RULES.md` |
| `project_kb_dir` | string | 否 | 项目知识库目录，默认 `project-kb` |
| `knowledge.global_dir` | string | 否 | 全局研究知识库目录，默认建议 `~/personal-kb`；支持路径展开 |
| `filebrowser.cli_config` | string | 否 | `filebrowser-cli` 配置路径；不填时由 CLI 按自身优先级解析。 |

FileBrowser 操作统一调用 `filebrowser-cli`，不直接访问 HTTP API。先按 `filebrowser-skill` 完成 CLI 安装、`config validate` 和登录。`AGENTS.md`、`CLAUDE.md` 和可选 `skills/` 固定同步到云端根目录 `/`，不允许项目配置改写。旧配置中的 `instance_url`、`username`、`password` 仅作为兼容输入，适配器会创建进程内临时 CLI 配置，不在命令行回显密码；新配置不要继续保存这些字段。

## 全局配置同步边界

云端全局配置目录只同步第 1 层通用入口和通用 skills：

```
/
├── AGENTS.md
├── CLAUDE.md
└── skills/
```

项目独立文件不进入通用配置包：
- `PROJECT_RULES.md`
- `project-kb/`
- `workplace/`

这样可以让所有项目使用相同的入口命令，同时保留各项目独立规则和知识。旧配置中的 `workspace.config_pack` 不再参与路径计算。

## 脚本工具

| 脚本 | 文档 | 功能 |
|---|---|---|
| `init_workspace.py` | `references/init-workspace.md` | 初始化三层入口、过程文档目录，可下载通用配置 |
| `personal-kb/scripts/kb_cli.py` | `personal-kb` | 初始化项目知识库并检查全局知识库可用性 |
| 项目图与全局知识库 | `references/project-graph.md` | 说明节点事实源、派生目录和全局知识库可用性 |
| `sync_config.py` | `references/sync-config.md` | 同步第 1 层通用入口和可选 skills |
| `filebrowser_client.py` | `filebrowser-skill` | 将同步操作适配到 `filebrowser-cli`，不直接调用 HTTP API |
| `version_manager.py` | `references/version-manager.md` | 创建版本、归档版本 |
| `skills_manager.py` | `references/skills-manager.md` | 管理 npx skills 命令 |

## 快速命令

```bash
# 先验证 filebrowser-cli
filebrowser-cli --version
filebrowser-cli config validate
filebrowser-cli login

# 初始化工作区
python skills/workspace-setup/scripts/init_workspace.py --config skillconfig.json

# 从配置包下载通用 AGENTS.md/CLAUDE.md
python skills/workspace-setup/scripts/sync_config.py download --config skillconfig.json

# 上传通用 AGENTS.md/CLAUDE.md
python skills/workspace-setup/scripts/sync_config.py upload --config skillconfig.json

# 同步通用配置和 skills
python skills/workspace-setup/scripts/sync_config.py sync --config skillconfig.json --sync-skills
```

## 初始化流程

1. 读取 `skillconfig.json`。
2. 创建或保留 `workplace/{current_version}/` 过程文档目录。
3. 在实际版本目录创建 `graph/stories/` 和 `graph/.derived/`，不预建 Story、modules、features 或伪业务节点；已有 `graph/nodes/` 保留但不迁移。
4. 调用 `personal-kb check-global` 解析全局知识库；显式路径不可用时报告错误。
5. 下载或创建通用 `AGENTS.md`、`CLAUDE.md`。
6. 创建项目独立 `PROJECT_RULES.md`，如果已存在则不覆盖。
7. 调用 `personal-kb init-project` 创建/校验项目独立 `project-kb/`，如果已存在则不覆盖。
8. 更新 `skillconfig.json` 中的当前版本号。

## 日常维护规则

- 修改通用入口规则后，使用 `sync_config.py upload` 上传到配置包。
- 修改项目规则或项目知识库时，不要上传到通用配置包。
- 如果某条规则多个项目都需要，迁移到 `AGENTS.md`。
- 如果某条规则只对当前项目有效，保留在 `PROJECT_RULES.md`。
- 修改代码后，使用 `personal-kb` 的代码镜像知识库规则同步更新 `project-kb/code/`。

## 过程文档目录

`workplace/` 继续用于需求、方案、计划、测试和归档，不承担项目规则或代码知识库职责。默认将一次迭代内的材料放入版本目录，将跨迭代复用的材料沉淀到顶层全局目录。

| 顶层目录 | 用途 |
|---|---|
| `global/` | 跨迭代复用的过程资产、模板、脚本、说明和参考材料 |
| `test/` | 与 `test-suite-maintainer` 联动的跨迭代测试方案、测试脚本、夹具、测试数据说明和报告模板 |
| `archive/` | 已完成迭代的溯源归档，只保留仍有追溯价值的需求、技术、计划、评审和结论文档 |

每个版本目录包含：

| 目录 | 用途 |
|---|---|
| `requirements/` | 需求文档 |
| `references/` | 参考文档 |
| `prototypes/` | 原型设计 |
| `tech-design/` | 技术方案 |
| `plan/` | 实施计划 |
| `tests/` | 测试文件和测试计划 |

## 归档流程

归档不是简单移动整个版本目录，应分成三步完成：

1. 清理无用文件：删除临时草稿、重复副本、缓存、生成产物、一次性调试文件和已失效截图。删除前确认没有后续追溯或复用价值。
2. 沉淀可复用内容：可复用的过程资产放到 `workplace/global/`；可复用的测试方案、脚本、夹具和报告模板放到 `workplace/test/`；稳定的项目知识、代码影响关系、测试映射和设计决策写入 `project-kb/`。
3. 溯源归档：将仍需要保留历史背景的需求、技术方案、实施计划、评审记录、测试结论和关键取舍归档到 `workplace/archive/{version}/`。

`version_manager.py archive` 只执行第 3 步的目录移动。执行命令前，应先完成清理和可复用内容沉淀，避免把可长期使用的材料封存在历史版本里。
