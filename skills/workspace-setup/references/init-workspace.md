# 初始化工作区

`init_workspace.py` 初始化三层项目上下文结构，并保留原有 `workplace/` 过程文档目录。

## 功能

- 创建 `workplace/{current_version}/` 过程文档目录。
- 创建 `workplace/global/` 和 `workplace/test/`，其中 `workplace/test/` 与 `test-suite-maintainer` 联动，用于跨迭代复用材料。
- 从 FileBrowser 下载第 1 层通用 `AGENTS.md`、`CLAUDE.md`。
- 创建第 2 层项目规则 `PROJECT_RULES.md`。
- 创建第 3 层项目知识库入口 `project-kb/`。
- 已存在的项目规则和项目知识库不会被覆盖。

## 命令

```bash
python skills/workspace-setup/scripts/init_workspace.py --config skillconfig.json
```

### 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--config` | `skillconfig.json` | 配置文件路径 |
| `--skip-download` | `false` | 跳过从 FileBrowser 下载通用配置文件 |

## 配置字段

```json
{
  "workspace": {
    "config_pack": "config-1",
    "current_version": "1.0",
    "workplace_dir": "workplace",
    "project_rules_file": "PROJECT_RULES.md",
    "project_kb_dir": "project-kb"
  }
}
```

| 字段 | 默认值 | 说明 |
|---|---|---|
| `workplace_dir` | `workplace` | 过程文档目录 |
| `current_version` | `1.0` | 当前过程文档版本 |
| `config_pack` | 空 | 通用配置包名称 |
| `project_rules_file` | `PROJECT_RULES.md` | 项目独立规则文件 |
| `project_kb_dir` | `project-kb` | 项目独立知识库目录 |

## 执行流程

### 1. 创建过程文档目录

```
workplace/
├── global/
├── test/
├── 1.0/
│   ├── requirements/
│   ├── references/
│   ├── prototypes/
│   ├── tech-design/
│   ├── plan/
│   └── tests/
└── archive/
```

### 2. 处理第 1 层通用入口

如果配置了 `config_pack` 且未使用 `--skip-download`：

```
{remote_base_path}/{config_pack}/AGENTS.md
{remote_base_path}/{config_pack}/CLAUDE.md
```

下载失败时创建默认模板：
- `CLAUDE.md`：`@AGENTS.md`
- `AGENTS.md`：通用规则和同级 `PROJECT_RULES.md` 入口说明

### 3. 创建第 2 层项目规则

默认创建：

```
PROJECT_RULES.md
```

该文件只在不存在时创建，避免覆盖项目自己的规则。

### 4. 创建第 3 层项目知识库

默认创建：

```
project-kb/
├── README.md
└── code/
    └── README.md
```

`project-kb/code/` 后续由 `personal-kb` 按源码相对路径维护。

## 输出示例

```text
🚀 开始初始化工作区...

✅ 创建工作目录: workplace
✅ 创建全局目录: workplace/global
✅ 创建全局目录: workplace/test
✅ 创建归档目录: workplace/archive
✅ 创建版本目录: workplace/1.0
  ├── requirements/
  ├── references/
  ├── prototypes/
  ├── tech-design/
  ├── plan/
  ├── tests/

📥 从 filebrowser 下载配置文件...
✅ 下载成功: /config/config-1/AGENTS.md -> AGENTS.md
✅ 下载成功: /config/config-1/CLAUDE.md -> CLAUDE.md
✅ 创建项目规则模板: PROJECT_RULES.md

📊 初始化完成:
   目录创建: 10
   配置下载: 2
   配置创建: 0
```

## 维护边界

- `AGENTS.md`、`CLAUDE.md`：通用配置包同步。
- `PROJECT_RULES.md`：项目独立维护。
- `project-kb/`：项目独立维护。
- `workplace/`：过程文档，不作为项目规则入口。
- `workplace/global/`：跨迭代复用的过程资产、模板、脚本和说明。
- `workplace/test/`：与 `test-suite-maintainer` 联动的跨迭代测试方案、脚本、夹具和报告模板。
