# 初始化工作区

`init_workspace.py` 脚本的详细使用说明。

## 功能

初始化项目工作区，包括：
- 创建 workplace 目录和版本结构
- 从 filebrowser 下载 CLAUDE.md、AGENTS.md
- 创建默认配置文件模板

## 命令

```bash
python scripts/init_workspace.py --config skillconfig.json
```

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--config` | skillconfig.json | 配置文件路径 |
| `--skip-download` | false | 跳过从 filebrowser 下载配置文件 |

## 执行流程

### 1. 加载配置

读取 skillconfig.json，获取以下配置：
- `workspace.workplace_dir` - 工作目录名
- `workspace.current_version` - 当前版本号
- `workspace.skill_name` - 技能名称（用于下载配置）
- `filebrowser.*` - filebrowser 连接配置

### 2. 创建目录结构

```
workplace/
├── {current_version}/
│   ├── requirements/
│   ├── references/
│   ├── prototypes/
│   ├── tech-design/
│   ├── plan/
│   └── tests/
└── archive/
```

### 3. 处理配置文件

- 如果 `skill_name` 配置且未使用 `--skip-download`：
  - 登录 filebrowser
  - 从 `{remote_base_path}/{skill_name}/` 下载 CLAUDE.md、AGENTS.md
  - 文件不存在时创建默认模板

- 否则创建默认配置文件模板

### 4. 更新配置

更新 skillconfig.json 中的 `current_version` 字段。

## 输出

```
🚀 开始初始化工作区...

✅ 创建工作目录: workplace
✅ 创建归档目录: archive
✅ 创建版本目录: 1.0
  ├── requirements/
  ├── references/
  ├── prototypes/
  ├── tech-design/
  ├── plan/
  ├── tests/

📥 从 filebrowser 下载配置文件...
✅ 登录成功: admin
✅ 下载成功: /skills/my-skill/CLAUDE.md -> CLAUDE.md
✅ 下载成功: /skills/my-skill/AGENTS.md -> AGENTS.md

📊 初始化完成:
   目录创建: 8
   配置下载: 2
   配置创建: 0
```

## 错误处理

| 错误 | 处理 |
|------|------|
| 配置文件缺失 | 抛出 FileNotFoundError |
| filebrowser 登录失败 | 创建默认配置文件模板 |
| 远程文件不存在 | 创建默认配置文件模板 |

## 使用示例

### 基本用法

```bash
# 在项目根目录运行
python skills/workspace-setup/scripts/init_workspace.py
```

### 跳过下载

```bash
# 不从 filebrowser 下载，只创建目录结构
python scripts/init_workspace.py --skip-download
```

### 自定义配置路径

```bash
python scripts/init_workspace.py --config path/to/config.json
```