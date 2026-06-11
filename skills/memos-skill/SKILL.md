---
name: memos-skill
description: |
  管理和操作 Memos 备忘录系统。当用户提到备忘录、memos、记录笔记、查看笔记、搜索备忘录、整理备忘录或任何与 memos 相关的操作时触发此 skill。支持创建备忘录、获取备忘录列表、搜索过滤、更新删除、管理评论和附件等功能。适用于个人知识管理、快速记录想法、整理笔记内容等场景。
---

# Memos Skill

管理你的 Memos 备忘录实例，支持备忘录、评论和附件操作。

## 安装

### 方式一：从 GitHub Release 下载预编译二进制（推荐）

访问 [GitHub Releases](https://github.com/ANIAN0/memos-cli/releases) 下载对应平台的二进制文件：

- Windows: `memos-cli-windows-amd64.exe`
- Linux: `memos-cli-linux-amd64`
- macOS: `memos-cli-darwin-amd64`

下载后重命名为 `memos-cli`（Windows 为 `memos-cli.exe`）并添加到 PATH。

### 方式二：使用 go install

```bash
go install github.com/ANIAN0/memos-cli@latest
```

### 方式三：从源码编译

```bash
git clone https://github.com/ANIAN0/memos-cli.git
cd memos-cli
make build
# 二进制文件在 bin/memos-cli
```

## 配置

配置使用 YAML 格式，支持 `${ENV_VAR}` 环境变量插值。

### 配置文件位置（按优先级）

1. `--config <path>` 命令行参数
2. `MEMOS_CLI_CONFIG` 环境变量
3. 二进制同级目录的 `config.yaml`（项目安装模式）
4. 用户目录：`~/.config/memos-cli/config.yaml`（Unix）或 `%APPDATA%\memos-cli\config.yaml`（Windows）

### 配置文件示例

```yaml
version: 1
instance_url: "https://your-memos-instance.com"
access_token: "${MEMOS_TOKEN}"  # 支持环境变量插值
default_page_size: 10
default_visibility: "PRIVATE"
```

### 配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `instance_url` | string | 是 | Memos 实例地址 |
| `access_token` | string | 是 | 个人访问令牌（支持 `${ENV_VAR}` 插值） |
| `default_page_size` | number | 否 | 默认分页大小（默认10） |
| `default_visibility` | string | 否 | 默认可见性：`PRIVATE`/`PROTECTED`/`PUBLIC` |

## CLI 工具

### 备忘录操作

```bash
# 创建备忘录
memos-cli memo create --content "Hello World"
memos-cli memo create --content "工作笔记" --visibility PRIVATE --tags work,urgent

# 获取备忘录
memos-cli memo get <id>

# 列出备忘录
memos-cli memo list
memos-cli memo list --page-size 20
memos-cli memo list --filter "tag=='work'"
memos-cli memo list --sort "-createTime"

# 更新备忘录
memos-cli memo update <id> --content "更新内容"
memos-cli memo update <id> --content "更新" --visibility PUBLIC

# 删除备忘录
memos-cli memo delete <id>

# 搜索备忘录
memos-cli memo search "关键词"
memos-cli memo search "关键词" --page-size 50
```

### 评论操作

```bash
# 列出评论
memos-cli comment list <memo-id>

# 创建评论
memos-cli comment create <memo-id> --content "评论内容"
```

### 附件操作

```bash
# 上传附件
memos-cli attachment upload ./image.png
memos-cli attachment upload ./document.pdf

# 列出附件
memos-cli attachment list
memos-cli attachment list --page-size 20

# 下载附件
memos-cli attachment get <id> --output ./downloaded.png

# 删除附件
memos-cli attachment delete <id>
```

### JSON 输出

所有命令支持 `--json` 标志，输出可被 `jq` 解析的 JSON：

```bash
memos-cli memo list --json | jq '.items'
memos-cli memo create --content "test" --json | jq '.name'
```

## 全局选项

| 选项 | 说明 |
|------|------|
| `--config <path>` | 指定配置文件路径 |
| `--json` | 输出 JSON 格式 |
| `--verbose, -v` | 详细日志到 stderr |
| `--timeout <seconds>` | HTTP 请求超时（默认 60） |
| `--no-color` | 禁用颜色输出 |
| `--version` | 输出版本信息 |
| `--help, -h` | 显示帮助 |

## 退出码

| 退出码 | 含义 | 触发条件 |
|--------|------|----------|
| `0` | 成功 | 请求成功 |
| `1` | 客户端错误 | Memos 错误码 3/5/7/16 |
| `2` | 服务端错误 | 其他 Memos 错误码 |
| `3` | 网络错误 | DNS 失败、连接超时、连接拒绝 |
| `4` | 配置错误 | 配置文件不存在、字段缺失、环境变量未设置 |

错误详情输出到 stderr，成功数据输出到 stdout。

## 基础信息

- **Base URL**: `{instance_url}/api/v1`
- **认证**: `Authorization: Bearer <token>`
- **内容类型**: `application/json`

## 错误代码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 3 | 无效参数 |
| 5 | 未找到 |
| 7 | 未认证 |
| 16 | 未授权 |

## ID 格式

- 备忘录: `memos/{id}`，如 `memos/123`
- 评论: `memos/{id}/comments/{cid}`
- 附件: `attachments/{id}`，如 `attachments/456`
- 时间: ISO 8601，如 `2024-03-12T10:30:00Z`

## 使用示例

```bash
# 创建备忘录
memos-cli memo create --content "Hello World" --visibility PRIVATE

# 列出备忘录
memos-cli memo list --page-size 10

# 搜索备忘录
memos-cli memo search "Hello"

# 上传附件
memos-cli attachment upload ./image.png

# 使用 JSON 输出
memos-cli memo list --json | jq '.items'
```
