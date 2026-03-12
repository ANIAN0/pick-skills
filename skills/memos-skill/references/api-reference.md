# Memos API 完整参考

## 基础信息

- **Base URL**: `{instance_url}/api/v1`
- **认证方式**: Bearer Token
- **请求头**: `Authorization: Bearer <token>`
- **内容类型**: `application/json` (除文件上传外)

## 错误代码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 3 | 无效参数 (Invalid argument) |
| 5 | 未找到 (Not found) |
| 7 | 未认证 (Unauthenticated) |
| 16 | 未授权 (Unauthorized) |

## Memo Service

### CreateMemo
```http
POST /api/v1/memos
```

**Request Body:**
```json
{
  "content": "string (required)",
  "visibility": "PRIVATE | PROTECTED | PUBLIC",
  "tags": ["string"],
  "resources": [
    {
      "name": "attachments/123",
      "uid": "string",
      "filename": "string",
      "size": 1024,
      "type": "image/png"
    }
  ]
}
```

**Response:**
```json
{
  "name": "memos/123",
  "uid": "uuid",
  "content": "string",
  "visibility": "PRIVATE",
  "pinned": false,
  "tags": ["tag1", "tag2"],
  "resources": [...],
  "creator": "users/1",
  "createTime": "2024-03-12T10:30:00Z",
  "updateTime": "2024-03-12T10:30:00Z"
}
```

### ListMemos
```http
GET /api/v1/memos?pageSize=10&pageToken=&filter=&sort=
```

**Query Parameters:**
- `pageSize`: 整数，默认10
- `pageToken`: 分页令牌
- `filter`: 过滤表达式
- `sort`: 排序字段 (`createTime`, `updateTime`)，加 `-` 表示倒序

**Filter 语法示例:**
```
# 基础过滤
creator == "users/1"
row_status == "NORMAL"
visibility == "PUBLIC"

# 标签过滤
tag == "work"
tag != "archive"

# 内容搜索
content.contains("关键词")

# 时间过滤
create_time > "2024-01-01"
update_time < "2024-12-31"

# 组合条件
content.contains("项目") AND tag == "work"
(tag == "work" OR tag == "urgent") AND create_time > "2024-01-01"
creator == "users/1" AND NOT tag == "archive"
```

### GetMemo
```http
GET /api/v1/memos/{memo}
```

**Path Parameters:**
- `memo`: 备忘录ID，如 `memos/123` 或只传 `123`

### UpdateMemo
```http
PATCH /api/v1/memos/{memo}?updateMask=content,visibility,tags
```

**Query Parameters:**
- `updateMask`: 逗号分隔的字段名，指定要更新的字段

**Request Body:**
```json
{
  "content": "新内容",
  "visibility": "PUBLIC",
  "tags": ["new-tag"]
}
```

### DeleteMemo
```http
DELETE /api/v1/memos/{memo}
```

### ListMemoComments
```http
GET /api/v1/memos/{memo}/comments
```

**Response:**
```json
{
  "comments": [
    {
      "name": "memos/123/comments/456",
      "uid": "uuid",
      "content": "评论内容",
      "creator": "users/1",
      "createTime": "2024-03-12T10:30:00Z"
    }
  ]
}
```

### CreateMemoComment
```http
POST /api/v1/memos/{memo}/comments
```

**Request Body:**
```json
{
  "content": "评论内容",
  "resources": []
}
```

### ListMemoReactions
```http
GET /api/v1/memos/{memo}/reactions
```

### UpsertMemoReaction
```http
POST /api/v1/memos/{memo}/reactions
```

**Request Body:**
```json
{
  "reaction": "THUMBS_UP"
}
```

**支持的 Reaction:**
- `THUMBS_UP` 👍
- `THUMBS_DOWN` 👎
- `HEART` ❤️
- `FIRE` 🔥
- `ROCKET` 🚀
- `EYES` 👀
- `THINKING` 🤔
- `CLAPPING` 👏
- `PARTY` 🎉

### SetMemoRelations
```http
POST /api/v1/memos/{memo}/relations
```

**Request Body:**
```json
{
  "relations": [
    {
      "memo": "memos/456",
      "type": "REFERENCE"
    }
  ]
}
```

**Relation Types:**
- `REFERENCE`: 引用关系
- `COMMENT`: 评论关系

## Attachment Service

### CreateAttachment
```http
POST /api/v1/attachments
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary data>
```

**Response:**
```json
{
  "name": "attachments/123",
  "uid": "uuid",
  "filename": "image.png",
  "size": 1024,
  "type": "image/png",
  "createTime": "2024-03-12T10:30:00Z"
}
```

### ListAttachments
```http
GET /api/v1/attachments?pageSize=10
```

### GetAttachment
```http
GET /api/v1/attachments/{attachment}
```

### DeleteAttachment
```http
DELETE /api/v1/attachments/{attachment}
```

### UpdateAttachment
```http
PATCH /api/v1/attachments/{attachment}?updateMask=filename
```

## Auth Service

### GetCurrentUser
```http
GET /api/v1/auth/status
```

**Response:**
```json
{
  "name": "users/1",
  "uid": "uuid",
  "username": "username",
  "nickname": "昵称",
  "email": "user@example.com",
  "avatarUrl": "https://...",
  "createTime": "2024-03-12T10:30:00Z",
  "updateTime": "2024-03-12T10:30:00Z"
}
```

### SignIn
```http
POST /api/v1/auth/signin
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

### RefreshToken
```http
POST /api/v1/auth/token/refresh
```

### SignOut
```http
POST /api/v1/auth/signout
```

## User Service

### ListUsers
```http
GET /api/v1/users?pageSize=10
```

### GetUser
```http
GET /api/v1/users/{user}
```

### UpdateUser
```http
PATCH /api/v1/users/{user}?updateMask=nickname,avatarUrl
```

### CreatePersonalAccessToken
```http
POST /api/v1/users/{user}/personalAccessTokens
```

**Request Body:**
```json
{
  "description": "My token",
  "expiresAt": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "name": "users/1/tokens/abc123",
  "token": "实际的token值（只返回一次）",
  "description": "My token",
  "expiresAt": "2024-12-31T23:59:59Z",
  "createTime": "2024-03-12T10:30:00Z"
}
```

### ListPersonalAccessTokens
```http
GET /api/v1/users/{user}/personalAccessTokens
```

### DeletePersonalAccessToken
```http
DELETE /api/v1/users/{user}/personalAccessTokens/{token}
```

## Shortcut Service

### ListShortcuts
```http
GET /api/v1/shortcuts?pageSize=10
```

### GetShortcut
```http
GET /api/v1/shortcuts/{shortcut}
```

### CreateShortcut
```http
POST /api/v1/shortcuts
```

**Request Body:**
```json
{
  "title": "快捷方式标题",
  "filter": "tag == \"work\"",
  "visibility": "PRIVATE"
}
```

### UpdateShortcut
```http
PATCH /api/v1/shortcuts/{shortcut}?updateMask=title,filter
```

### DeleteShortcut
```http
DELETE /api/v1/shortcuts/{shortcut}
```

## Instance Service

### GetInstanceProfile
```http
GET /api/v1/instance/profile
```

**Response:**
```json
{
  "name": "memos",
  "version": "v0.22.0",
  "mode": "prod",
  "allowSignup": false,
  "disablePublicMemos": false,
  "maxUploadSize": 104857600,
  "memoDisplayWithUpdatedTime": false
}
```

### GetInstanceSetting
```http
GET /api/v1/instance/settings/{setting}
```

### UpdateInstanceSetting
```http
PATCH /api/v1/instance/settings/{setting}?updateMask=value
```

## Activity Service

### ListActivities
```http
GET /api/v1/activities?pageSize=10
```

### GetActivity
```http
GET /api/v1/activities/{activity}
```

## 实用技巧

### 获取当前用户ID
```http
GET /api/v1/auth/status
# 从返回的 name 字段提取 ID（users/1 -> 1）
```

### 使用 cURL 示例

首先读取配置文件获取 token 和 URL：

```bash
# 读取配置文件
CONFIG_FILE="/path/to/skill/config.json"
MEMOS_URL=$(cat $CONFIG_FILE | grep -o '"instance_url": "[^"]*"' | cut -d'"' -f4)
MEMOS_TOKEN=$(cat $CONFIG_FILE | grep -o '"access_token": "[^"]*"' | cut -d'"' -f4)

# 列出备忘录
curl -H "Authorization: Bearer $MEMOS_TOKEN" \
  "$MEMOS_URL/api/v1/memos?pageSize=10"

# 创建备忘录
curl -X POST \
  -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "测试内容", "tags": ["test"]}' \
  "$MEMOS_URL/api/v1/memos"

# 搜索备忘录
curl -H "Authorization: Bearer $MEMOS_TOKEN" \
  "$MEMOS_URL/api/v1/memos?filter=content.contains(\"关键词\")"

# 上传附件
curl -X POST \
  -H "Authorization: Bearer $MEMOS_TOKEN" \
  -F "file=@/path/to/file.png" \
  "$MEMOS_URL/api/v1/attachments"
```

### 分页处理

```python
import json
import os
import requests

# 读取配置文件
skill_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(skill_dir, 'config.json')

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

base_url = config['instance_url']
headers = {
    'Authorization': f'Bearer {config["access_token"]}',
    'Content-Type': 'application/json'
}

# 分页获取所有备忘录
page_token = ""
all_memos = []

while True:
    url = f"{base_url}/api/v1/memos?pageSize=100&pageToken={page_token}"
    response = requests.get(url, headers=headers)
    data = response.json()

    all_memos.extend(data.get("memos", []))

    page_token = data.get("nextPageToken", "")
    if not page_token:
        break

print(f"共获取 {len(all_memos)} 条备忘录")
```
