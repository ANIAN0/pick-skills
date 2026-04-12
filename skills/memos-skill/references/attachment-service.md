# Attachment Service

附件管理服务的完整 API 参考。

## 基础端点

`/api/v1/attachments`

## 接口列表

### CreateAttachment - 上传附件

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

---

### ListAttachments - 获取附件列表

```http
GET /api/v1/attachments?pageSize=10
```

---

### GetAttachment - 获取单个附件

```http
GET /api/v1/attachments/{attachment}
```

---

### DeleteAttachment - 删除附件

```http
DELETE /api/v1/attachments/{attachment}
```

---

### UpdateAttachment - 更新附件信息

```http
PATCH /api/v1/attachments/{attachment}?updateMask=filename
```

## 关联备忘录

上传附件后，需要通过 Memo Service 将附件关联到备忘录：

```http
POST /api/v1/memos/{memo}
```

**Request Body:**
```json
{
  "content": "带附件的备忘录",
  "resources": [
    {
      "name": "attachments/123"
    }
  ]
}
```