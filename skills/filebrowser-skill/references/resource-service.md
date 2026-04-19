# Resource Service

文件资源服务的完整 API 参考。支持文件上传、下载、预览、删除等操作。

## 基础端点

`/api/resources{path}` - 文件/目录操作
`/api/raw{path}` - 文件下载
`/api/preview/{size}/{path}` - 图片预览

---

## 接口列表

### GetResource - 获取文件/目录信息

获取指定路径的文件或目录信息。

```http
GET /api/resources{path}
X-Auth: <token>
```

**Path Parameters:**
- `path`: 文件路径（URL 编码）

**Query Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `checksum` | md5/sha1/sha256/sha512 | 计算文件校验和 |

**Request Headers:**
| Header | 值 | 说明 |
|--------|------|------|
| `X-Encoding` | true | 文本文件返回内容而非 JSON |

**Response (目录):**
```json
{
  "path": "/folder",
  "name": "folder",
  "isDir": true,
  "size": 0,
  "modified": "2024-01-01T00:00:00Z",
  "created": "2024-01-01T00:00:00Z",
  "type": "dir",
  "items": [
    {
      "path": "/folder/file.txt",
      "name": "file.txt",
      "isDir": false,
      "size": 1024,
      "modified": "2024-01-01T00:00:00Z",
      "type": "text",
      "extension": ".txt"
    }
  ],
  "numDirs": 2,
  "numFiles": 5
}
```

**Response (文件):**
```json
{
  "path": "/file.txt",
  "name": "file.txt",
  "isDir": false,
  "size": 1024,
  "modified": "2024-01-01T00:00:00Z",
  "type": "text",
  "extension": ".txt",
  "content": "file content...",
  "checksums": {
    "md5": "abc123...",
    "sha256": "def456..."
  }
}
```

---

### CreateResource - 上传文件/创建目录

上传文件或创建目录。

```http
POST /api/resources{path}
X-Auth: <token>
```

**权限要求:** `create`

**Path Parameters:**
- `path`: 目标路径

**Query Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `override` | true/false | 覆盖已存在的文件 |

**Request Body:**
- 上传文件: 文件二进制内容
- 创建目录: 空内容，路径以 `/` 结尾

**Response:**
| 状态码 | 说明 |
|--------|------|
| `200 OK` | 成功 |
| `409 Conflict` | 文件已存在（未设置 override） |
| `403 Forbidden` | 无权限 |

**Response Headers:**
| Header | 说明 |
|--------|------|
| `ETag` | `{timestamp}{size}` |

**示例:**
```python
# 上传文件
with open("local_file.txt", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/resources/remote_file.txt",
        headers={"X-Auth": token},
        data=f,
        params={"override": "true"}
    )

# 创建目录
response = requests.post(
    f"{BASE_URL}/api/resources/new_folder/",
    headers={"X-Auth": token}
)
```

---

### UpdateResource - 更新文件内容

更新已存在文件的内容（不支持目录）。

```http
PUT /api/resources{path}
X-Auth: <token>
```

**权限要求:** `modify`

**Path Parameters:**
- `path`: 文件路径

**Request Body:** 文件二进制内容

**Response:**
| 状态码 | 说明 |
|--------|------|
| `200 OK` | 成功 |
| `404 Not Found` | 文件不存在 |

**Response Headers:**
| Header | 说明 |
|--------|------|
| `ETag` | `{timestamp}{size}` |

---

### DeleteResource - 删除文件/目录

删除指定文件或目录。

```http
DELETE /api/resources{path}
X-Auth: <token>
```

**权限要求:** `delete`

**Path Parameters:**
- `path`: 文件/目录路径

**Response:**
- 状态码: `204 No Content`

---

### PatchResource - 移动/复制文件

移动或复制文件到新位置。

```http
PATCH /api/resources{path}?action={action}&destination={dest}
X-Auth: <token>
```

**权限要求:** `rename`（移动）或 `create`（复制）

**Path Parameters:**
- `path`: 源文件路径

**Query Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `action` | rename/copy | 操作类型 |
| `destination` | /new/path | 目标路径（URL 编码） |
| `override` | true/false | 覆盖已存在的文件 |
| `rename` | true/false | 自动重命名避免冲突 |

**Response:**
| 状态码 | 说明 |
|--------|------|
| `200 OK` | 成功 |
| `409 Conflict` | 目标已存在 |
| `403 Forbidden` | 无权限 |

---

### DownloadFile - 下载文件/目录

下载单个文件或打包下载目录/多文件。

```http
GET /api/raw{path}
X-Auth: <token>
```

**权限要求:** `download`

**Path Parameters:**
- `path`: 文件/目录路径

**Query Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `files` | /path1,/path2 | 多文件下载（逗号分隔） |
| `algo` | zip/tar/targz/... | 打包格式 |
| `inline` | true/false | 内联显示而非下载 |

**支持的打包格式:**
- `zip` - ZIP 格式
- `tar` - TAR 格式
- `targz` - TAR.GZ 格式
- `tarbz2` - TAR.BZ2 格式
- `tarxz` - TAR.XZ 格式
- `tarlz4` - TAR.LZ4 格式
- `tarsz` - TAR.SZ 格式
- `tarbr` - TAR.BR 格式
- `tarzst` - TAR.ZST 格式

**Response Headers:**
| Header | 说明 |
|--------|------|
| `Content-Disposition` | attachment/inline |
| `Cache-Control` | private |

**示例:**
```python
# 下载单个文件
response = requests.get(
    f"{BASE_URL}/api/raw/file.txt",
    headers={"X-Auth": token},
    stream=True
)
with open("local_file.txt", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

# 打包下载目录
response = requests.get(
    f"{BASE_URL}/api/raw/folder",
    headers={"X-Auth": token},
    params={"algo": "zip"}
)
```

---

### GetPreview - 图片预览

获取图片的缩略图或预览图。

```http
GET /api/preview/{size}/{path}
X-Auth: <token>
```

**权限要求:** `download`

**Path Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `size` | thumb/big | 预览尺寸 |
| `path` | 文件路径 | 图片文件路径 |

**尺寸规格:**
- `thumb` - 256x256 像素
- `big` - 1080x1080 像素

**Query Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `inline` | true/false | 内联显示 |
| `key` | timestamp | 缓存键 |

**Response:** 图片二进制内容

---

## TUS 大文件上传

TUS 协议支持大文件分块上传和断点续传。

### TusCreate - 创建上传会话

```http
POST /api/tus{path}
X-Auth: <token>
Upload-Length: <file_size>
Tus-Resumable: 1.0.0
```

**权限要求:** `create`

**Response:**
- 状态码: `201 Created`
- Header: `Location: /api/tus{path}`

### TusStatus - 获取上传状态

```http
HEAD /api/tus{path}
X-Auth: <token>
```

**Response Headers:**
| Header | 说明 |
|--------|------|
| `Upload-Offset` | 已上传字节数 |
| `Upload-Length` | 文件总大小 |

### TusUpload - 上传数据块

```http
PATCH /api/tus{path}
X-Auth: <token>
Content-Type: application/offset+octet-stream
Upload-Offset: <offset>
Tus-Resumable: 1.0.0
```

**Request Body:** 文件二进制数据

**Response Headers:**
| Header | 说明 |
|--------|------|
| `Upload-Offset` | 新的偏移量 |

### TusDelete - 取消上传

```http
DELETE /api/tus{path}
X-Auth: <token>
```

**权限要求:** `delete`

**Response:** `204 No Content`

---

## 文件类型说明

| type | 说明 |
|------|------|
| `text` | 文本文件 |
| `image` | 图片文件 |
| `video` | 视频文件 |
| `audio` | 音频文件 |
| `pdf` | PDF 文件 |
| `blob` | 其他二进制文件 |

---

## 错误处理

| 状态码 | 说明 | 处理 |
|--------|------|------|
| `200` | 成功 | - |
| `201` | 创建成功 | - |
| `204` | 删除成功 | - |
| `401` | 未认证 | 重新登录 |
| `403` | 无权限 | 检查用户权限 |
| `404` | 文件不存在 | 检查路径 |
| `409` | 文件已存在 | 使用 override 参数 |