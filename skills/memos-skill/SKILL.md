---
name: memos-skill
description: |
  管理和操作 Memos 备忘录系统。当用户提到备忘录、memos、记录笔记、查看笔记、搜索备忘录、整理备忘录或任何与 memos 相关的操作时触发此 skill。支持创建备忘录、获取备忘录列表、搜索过滤、更新删除、管理附件等功能。适用于个人知识管理、快速记录想法、整理笔记内容等场景。
---

# Memos Skill

管理你的 Memos 备忘录实例，支持备忘录和附件操作。

## 配置

配置从项目根目录的 `skillconfig.json` 文件读取。

### 配置文件位置

```
项目根目录/
├── skillconfig.json          ← 配置文件
├── skills/
│   └── memos-skill/
│       └── SKILL.md
└── ...
```

### 配置格式

```json
{
  "memos": {
    "instance_url": "https://your-memos-instance.com",
    "access_token": "your-access-token",
    "default_page_size": 10,
    "default_visibility": "PRIVATE"
  }
}
```

### 配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `instance_url` | string | 是 | Memos 实例地址 |
| `access_token` | string | 是 | 个人访问令牌（在 Memos Settings → Tokens 创建） |
| `default_page_size` | number | 否 | 默认分页大小（默认10） |
| `default_visibility` | string | 否 | 默认可见性：`PRIVATE`/`PROTECTED`/`PUBLIC` |

## API 服务

按需读取对应的接口文档。

| 服务 | 文档 | 功能 |
|------|------|------|
| **Memo Service** | `references/memo-service.md` | 备忘录 CRUD、评论 |
| **Attachment Service** | `references/attachment-service.md` | 附件上传与管理 |

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
- 附件: `attachments/{id}`，如 `attachments/456`
- 时间: ISO 8601，如 `2024-03-12T10:30:00Z`