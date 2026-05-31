# 配置文件同步

`sync_config.py` 只同步第 1 层通用入口和可选 `skills/` 目录。

## 功能

- `upload`：上传本地通用入口到 FileBrowser。
- `download`：从 FileBrowser 下载通用入口。
- `sync`：基于修改时间双向同步通用入口。
- `--sync-skills`：额外同步 `skills/` 目录。

同步范围：
- `AGENTS.md`
- `CLAUDE.md`
- `skills/`（可选）

不同步范围：
- `PROJECT_RULES.md`
- `project-kb/`
- `workplace/`

这些文件和目录是项目独立内容，不能进入通用配置包。

## 命令

### 上传通用入口

```bash
python skills/workspace-setup/scripts/sync_config.py upload --config skillconfig.json
```

### 下载通用入口

```bash
python skills/workspace-setup/scripts/sync_config.py download --config skillconfig.json
```

### 双向同步

```bash
python skills/workspace-setup/scripts/sync_config.py sync --config skillconfig.json
```

### 同步通用入口和 skills

```bash
python skills/workspace-setup/scripts/sync_config.py sync --config skillconfig.json --sync-skills
```

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `command` | 必填 | `upload`、`download` 或 `sync` |
| `--config` | `skillconfig.json` | 配置文件路径 |
| `--sync-skills` | `false` | 同时同步 `skills/` 目录 |

## 云端路径

```
{remote_base_path}/{config_pack}/AGENTS.md
{remote_base_path}/{config_pack}/CLAUDE.md
{remote_base_path}/{config_pack}/skills/
```

示例：

```
/config/config-1/AGENTS.md
/config/config-1/CLAUDE.md
/config/config-1/skills/
```

## 同步逻辑

### upload

| 条件 | 行为 |
|---|---|
| 本地通用入口存在 | 上传并覆盖云端 |
| 本地通用入口不存在 | 跳过并提示 |

### download

| 条件 | 行为 |
|---|---|
| 云端通用入口存在 | 下载并覆盖本地 |
| 云端通用入口不存在 | 跳过并提示 |

### sync

| 条件 | 行为 |
|---|---|
| 本地存在，云端不存在 | 上传 |
| 云端存在，本地不存在 | 下载 |
| 本地较新 | 上传 |
| 云端较新 | 下载 |
| 时间相同 | 跳过 |

## 日常工作流

```bash
# 获取团队统一入口
python skills/workspace-setup/scripts/sync_config.py download --config skillconfig.json

# 修改通用 AGENTS.md 后上传
python skills/workspace-setup/scripts/sync_config.py upload --config skillconfig.json

# 同步通用入口和技能目录
python skills/workspace-setup/scripts/sync_config.py sync --config skillconfig.json --sync-skills
```

## 注意事项

- `PROJECT_RULES.md` 和 `project-kb/` 必须通过项目仓库自身版本控制维护。
- 如果发现通用入口里混入项目规则，应移动到 `PROJECT_RULES.md`。
- 如果发现 `PROJECT_RULES.md` 里存在跨项目通用规则，应提炼到 `AGENTS.md` 并同步配置包。
