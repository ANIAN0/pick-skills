# 配置文件同步

`sync_config.py` 脚本的详细使用说明。

## 功能

同步 CLAUDE.md、AGENTS.md 配置文件：
- `upload` - 上传本地变更到 filebrowser
- `download` - 从 filebrowser 下载最新配置
- `sync` - 双向同步（基于修改时间）

## 命令

### 上传配置

```bash
python scripts/sync_config.py upload --config skillconfig.json
```

上传本地 CLAUDE.md、AGENTS.md 到 filebrowser。

### 下载配置

```bash
python scripts/sync_config.py download --config skillconfig.json
```

从 filebrowser 下载 CLAUDE.md、AGENTS.md 到本地。

### 双向同步

```bash
python scripts/sync_config.py sync --config skillconfig.json
```

根据修改时间智能决定同步方向：
- 本地较新 → 上传
- 远程较新 → 下载
- 相同时间 → 跳过
- 单边缺失 → 补充

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--config` | skillconfig.json | 配置文件路径 |

## 远程路径

配置文件在 filebrowser 上的存储路径：

```
{remote_base_path}/{skill_name}/CLAUDE.md
{remote_base_path}/{skill_name}/AGENTS.md
```

默认路径示例：
- `/skills/my-skill/CLAUDE.md`
- `/skills/my-skill/AGENTS.md`

## 输出示例

### 上传

```
📤 开始上传配置文件...

✅ 登录成功: admin
✅ 创建目录: /skills/my-skill
✅ 上传成功: CLAUDE.md -> /skills/my-skill/CLAUDE.md
✅ 上传成功: AGENTS.md -> /skills/my-skill/AGENTS.md

📊 上传完成:
   成功: 2
   跳过: 0
   失败: 0
```

### 下载

```
📥 开始下载配置文件...

✅ 登录成功: admin
✅ 下载成功: /skills/my-skill/CLAUDE.md -> CLAUDE.md
✅ 下载成功: /skills/my-skill/AGENTS.md -> AGENTS.md

📊 下载完成:
   成功: 2
   跳过: 0
   失败: 0
```

### 双向同步

```
🔄 开始双向同步配置文件...

  ⬆️ CLAUDE.md (本地较新)
  ⏭️ AGENTS.md (无需更新)

📊 同步完成:
   上传: 1
   下载: 0
   跳过: 1
   失败: 0
```

## 同步逻辑

### upload 模式

| 条件 | 行为 |
|------|------|
| 本地文件存在 | 上传（override=True） |
| 本地文件不存在 | 跳过，警告 |

### download 模式

| 条件 | 行为 |
|------|------|
| 远程文件存在 | 下载 |
| 远程文件不存在 | 跳过，警告 |

### sync 模式

| 条件 | 行为 |
|------|------|
| 本地存在，远程不存在 | 上传 |
| 远程存在，本地不存在 | 下载 |
| 本地较新（mtime > remote） | 上传 |
| 远程较新（mtime > local） | 下载 |
| 时间相同 | 跳过 |

## 错误处理

| 错误 | 处理 |
|------|------|
| 登录失败 | 返回错误，终止操作 |
| 上传失败 | 记录错误，继续处理其他文件 |
| 下载失败 | 记录错误，继续处理其他文件 |

## 使用示例

### 日常同步工作流

```bash
# 修改 CLAUDE.md 后上传
python scripts/sync_config.py upload

# 获取团队最新配置
python scripts/sync_config.py download

# 智能同步（推荐）
python scripts/sync_config.py sync
```

### CI/CD 集成

```bash
# 在 CI 中下载配置
python scripts/sync_config.py download --config skillconfig.json

# 在 CD 中上传变更
python scripts/sync_config.py upload --config skillconfig.json
```