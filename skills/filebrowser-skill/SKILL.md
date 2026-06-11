---
name: filebrowser-skill
description: |
  管理和操作 FileBrowser 文件管理系统。当用户提到文件上传、文件下载、文件分享、文件搜索、文件同步、云端文件管理或任何与 filebrowser 相关的操作时触发此 skill。支持上传文件获取分享链接、搜索下载文件、目录管理等功能。适用于个人文件管理、团队文件共享等场景。
---

# FileBrowser Skill

管理你的 FileBrowser 文件管理实例，支持文件操作、分享管理和搜索功能。

## 安装

### 方式一：从 GitHub Release 下载预编译二进制（推荐）

访问 [GitHub Releases](https://github.com/ANIAN0/filebrowser-cli/releases) 下载对应平台的二进制文件：

- Windows: `filebrowser-cli-windows-amd64.exe`
- Linux: `filebrowser-cli-linux-amd64`
- macOS: `filebrowser-cli-darwin-amd64`

下载后重命名为 `filebrowser-cli`（Windows 为 `filebrowser-cli.exe`）并添加到 PATH。

### 方式二：使用 go install

```bash
go install github.com/ANIAN0/filebrowser-cli@latest
```

### 方式三：从源码编译

```bash
git clone https://github.com/ANIAN0/filebrowser-cli.git
cd filebrowser-cli
make build
# 二进制文件在 bin/filebrowser-cli
```

## 配置

配置使用 YAML 格式，支持 `${ENV_VAR}` 环境变量插值。

### 配置文件位置（按优先级）

1. `--config <path>` 命令行参数
2. `FILEBROWSER_CLI_CONFIG` 环境变量
3. 二进制同级目录的 `config.yaml`（项目安装模式）
4. 用户目录：`~/.config/filebrowser-cli/config.yaml`（Unix）或 `%APPDATA%\filebrowser-cli\config.yaml`（Windows）

### 配置文件示例

```yaml
version: 1
instance_url: "http://your-server:8080"
username: "admin"
password: "${FB_PASSWORD}"  # 支持环境变量插值
default_expires: 24
default_unit: "hours"
```

### 配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `instance_url` | string | 是 | FileBrowser 实例地址 |
| `username` | string | 是 | 登录用户名 |
| `password` | string | 是 | 登录密码（支持 `${ENV_VAR}` 插值） |
| `default_expires` | int | 否 | 分享默认过期时间 |
| `default_unit` | string | 否 | 时间单位：seconds/minutes/hours/days |

## CLI 工具

### 认证

```bash
# 登录
filebrowser-cli login

# 续期 token
filebrowser-cli renew

# 显示当前用户
filebrowser-cli whoami
```

### 文件操作

```bash
# 列出目录
filebrowser-cli ls /
filebrowser-cli ls /documents --long

# 显示目录树
filebrowser-cli tree /documents

# 查看文件信息
filebrowser-cli info /documents/report.pdf

# 上传文件
filebrowser-cli upload ./local.pdf /remote/path.pdf
filebrowser-cli upload ./local.pdf /remote/path.pdf --override

# 下载文件
filebrowser-cli download /remote/path.pdf ./local.pdf

# 创建目录
filebrowser-cli mkdir /new-folder

# 删除文件/目录
filebrowser-cli rm /path/to/delete

# 移动/重命名
filebrowser-cli mv /old/path /new/path

# 复制
filebrowser-cli cp /source /destination
```

### 预览

```bash
# 获取缩略图（256x256）
filebrowser-cli preview /image.png --size thumb

# 获取大图（1080x1080）
filebrowser-cli preview /image.png --size big --output ./preview.png
```

### 分享管理

```bash
# 创建分享链接
filebrowser-cli share create /documents/report.pdf
filebrowser-cli share create /documents/report.pdf --expires 24 --unit hours
filebrowser-cli share create /documents/report.pdf --password mypassword

# 列出所有分享
filebrowser-cli share list

# 查看分享信息
filebrowser-cli share info /documents/report.pdf

# 删除分享
filebrowser-cli share delete <hash>
```

### 搜索

```bash
# 搜索文件
filebrowser-cli search / "report"
filebrowser-cli search / "report" --limit 50
```

### JSON 输出

所有命令支持 `--json` 标志，输出可被 `jq` 解析的 JSON：

```bash
filebrowser-cli ls / --json | jq '.items'
filebrowser-cli share create /file.pdf --json | jq '.hash'
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
| `0` | 成功 | 请求成功（2xx） |
| `1` | 客户端错误 | HTTP 4xx（401/403/404/409） |
| `2` | 服务端错误 | HTTP 5xx（500/502/503/504） |
| `3` | 网络错误 | DNS 失败、连接超时、连接拒绝 |
| `4` | 配置错误 | 配置文件不存在、字段缺失、环境变量未设置 |

错误详情输出到 stderr，成功数据输出到 stdout。

## 基础信息

- **Base URL**: `{instance_url}/api`
- **认证方式**: JWT Token
- **认证 Header**: `X-Auth: <token>`
- **Token 获取**: 登录接口返回纯文本 Token

## 外部访问链接格式

创建分享后，可通过以下格式访问：

| 类型 | 链接格式 |
|------|----------|
| **分享预览** | `{instance_url}/share/{hash}` |
| **直接下载** | `{instance_url}/api/public/dl/{hash}` |
| **内部下载** | `{instance_url}/api/raw{path}` |

## 常见错误

| 状态码 | 说明 | 处理 |
|--------|------|------|
| `200` | 成功 | - |
| `201` | 创建成功 | - |
| `204` | 删除成功 | - |
| `401` | 未认证/Token过期 | 重新运行 `filebrowser-cli login` |
| `403` | 无权限 | 检查用户权限 |
| `404` | 资源不存在 | 检查路径 |
| `409` | 文件已存在 | 使用 `--override` 参数 |

## 使用示例

```bash
# 登录
filebrowser-cli login

# 列出根目录
filebrowser-cli ls /

# 上传文件
filebrowser-cli upload ./report.pdf /documents/report.pdf

# 创建分享链接
filebrowser-cli share create /documents/report.pdf --expires 24 --unit hours

# 搜索文件
filebrowser-cli search / "report"

# 使用 JSON 输出
filebrowser-cli ls / --json | jq '.items'
```
