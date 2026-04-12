# Memo Service

Memo（备忘录）核心服务的完整 API 参考。

## 基础端点

`/api/v1/memos`

## 接口列表

### CreateMemo - 创建备忘录

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

---

### ListMemos - 获取备忘录列表

```http
GET /api/v1/memos?pageSize=10&pageToken=&filter=&sort=
```

**Query Parameters:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `pageSize` | integer | 每页数量，默认10 |
| `pageToken` | string | 分页令牌 |
| `filter` | string | 过滤表达式（AIP-160语法） |
| `sort` | string | 排序字段 (`createTime`, `updateTime`)，加 `-` 表示倒序 |

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

---

### GetMemo - 获取单个备忘录

```http
GET /api/v1/memos/{memo}
```

**Path Parameters:**
- `memo`: 备忘录ID，如 `memos/123` 或只传 `123`

---

### UpdateMemo - 更新备忘录

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

---

### DeleteMemo - 删除备忘录

```http
DELETE /api/v1/memos/{memo}
```

---

### ListMemoComments - 获取评论列表

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

---

### CreateMemoComment - 创建评论

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

