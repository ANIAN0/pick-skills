---
name: filebrowser-skill
description: |
  管理和操作 FileBrowser 文件管理系统。当用户提到文件上传、文件下载、文件分享、文件搜索、文件同步、云端文件管理或任何与 filebrowser 相关的操作时触发此 skill。支持上传文件获取分享链接、搜索下载文件、本地云端双向同步等功能。适用于个人文件管理、团队文件共享、云端备份同步等场景。
---

# FileBrowser Skill

管理你的 FileBrowser 文件管理实例，支持文件操作、分享管理、搜索下载和同步功能。

## 配置

配置从项目根目录的 `skillconfig.json` 文件读取。

### 配置文件位置

```
项目根目录/
├── skillconfig.json          ← 配置文件
├── skills/
│   └── filebrowser-skill/
│       └── SKILL.md
└── ...
```

### 配置格式

```json
{
  "filebrowser": {
    "instance_url": "http://your-server:8080",
    "username": "admin",
    "password": "your-password"
  }
}
```

### 配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `instance_url` | string | 是 | FileBrowser 实例地址 |
| `username` | string | 是 | 登录用户名 |
| `password` | string | 是 | 登录密码 |

## API 服务

按需读取对应的接口文档。

| 服务 | 文档 | 功能 |
|------|------|------|
| **Auth Service** | `references/auth-service.md` | 登录认证、Token 管理 |
| **Resource Service** | `references/resource-service.md` | 文件上传、下载、预览、删除 |
| **Share Service** | `references/share-service.md` | 创建分享、获取分享链接、删除分享 |
| **Search Service** | `references/search-service.md` | 文件搜索 |

## 同步脚本

### upload_and_share.py - 上传单文件获取分享链接

上传单个文件并自动创建分享链接，输出预览、下载、直接查看链接。

```bash
python scripts/upload_and_share.py --url <url> --user <user> --password <pwd> --file <file>
```

**参数:**
| 参数 | 说明 |
|------|------|
| `--file` | 本地文件路径 |
| `--remote` | 远程路径（可选，默认使用文件名） |
| `--expires` | 过期时间数值（可选） |
| `--unit` | 时间单位：seconds/minutes/hours/days |
| `--share-password` | 分享密码保护（可选） |

### directory_sync.py - 目录同步工具

上传、下载或同步整个目录。

```bash
python scripts/directory_sync.py <command> --url <url> --user <user> --password <pwd> --local <local> --remote <remote>
```

**命令:**
| 命令 | 说明 |
|------|------|
| `upload` | 上传整个目录到云端 |
| `download` | 从云端下载整个目录 |
| `sync-up` | 智能上传（只上传变化的文件） |
| `sync-down` | 智能下载（只下载变化的文件） |
| `sync` | 双向同步（本地云端互相同步） |

## 基础信息

- **Base URL**: `{instance_url}/api`
- **认证方式**: JWT Token
- **认证 Header**: `X-Auth: <token>`
- **Token 获取**: 登录接口返回纯文本 Token

## 权限说明

| 权限 | 说明 |
|------|------|
| `create` | 创建文件/目录 |
| `modify` | 修改文件内容 |
| `delete` | 删除文件 |
| `share` | 创建分享链接 |
| `download` | 下载文件 |
| `rename` | 重命名文件 |

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
| `401` | 未认证/Token过期 | 重新登录 |
| `403` | 无权限 | 检查用户权限 |
| `404` | 资源不存在 | 检查路径 |
| `409` | 文件已存在 | 使用 override 参数 |