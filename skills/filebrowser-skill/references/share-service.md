# Share Service

分享服务的完整 API 参考。支持创建分享链接、获取分享信息、删除分享等功能。

## 基础端点

`/api/shares` - 分享列表
`/api/share{path}` - 单个路径的分享
`/api/public/share/{hash}` - 公共分享访问
`/api/public/dl/{hash}` - 公共分享下载

---

## 接口列表

### ListShares - 获取分享列表

获取用户创建的所有分享链接。

```http
GET /api/shares
X-Auth: <token>
```

**权限要求:** `share` + `download`

**Response:**
```json
[
  {
    "hash": "abc123def456",
    "path": "/sharedfolder",
    "expire": 1704067200,
    "userID": 1,
    "username": "admin",
    "token": ""
  }
]
```

**字段说明:**
| 字段 | 说明 |
|------|------|
| `hash` | 分享链接的唯一标识 |
| `path` | 分享的文件/目录路径 |
| `expire` | 过期时间戳（Unix timestamp） |
| `userID` | 创建者的用户 ID |
| `username` | 创建者用户名 |
| `token` | 密码保护时的下载令牌 |

---

### GetShare - 获取路径的分享信息

获取指定文件/目录的分享信息。

```http
GET /api/share{path}
X-Auth: <token>
```

**权限要求:** `share` + `download`

**Path Parameters:**
- `path`: 文件/目录路径

**Response:** 分享信息数组

---

### CreateShare - 创建分享链接

创建文件或目录的分享链接。

```http
POST /api/share{path}
X-Auth: <token>
Content-Type: application/json
```

**权限要求:** `share` + `download`

**Path Parameters:**
- `path`: 要分享的文件/目录路径

**Query Parameters:**
| 参数 | 值 | 说明 |
|------|------|------|
| `expires` | number | 过期时间数值 |
| `unit` | seconds/minutes/hours/days | 时间单位 |

**Request Body:**
```json
{
  "expires": "24",
  "unit": "hours",
  "password": "optional_password"
}
```

**expires 和 unit 参数:**
| unit | 说明 | expires 示例 |
|------|------|---------------|
| `seconds` | 秒 | `"3600"` = 1小时 |
| `minutes` | 分钟 | `"60"` = 1小时 |
| `hours` | 小时 | `"24"` = 1天 |
| `days` | 天 | `"7"` = 7天 |

**password 参数（可选）:**
- 设置分享密码保护
- 访客需要输入密码才能访问

**Response:**
```json
{
  "hash": "abc123def456",
  "path": "/sharedfolder",
  "expire": 1704067200,
  "userID": 1,
  "token": "download_token_for_password"
}
```

**示例:**
```python
# 创建24小时有效的分享链接
response = requests.post(
    f"{BASE_URL}/api/share/folder",
    headers={"X-Auth": token},
    json={"expires": "24", "unit": "hours"}
)
share_info = response.json()
share_url = f"{BASE_URL}/share/{share_info['hash']}"

# 创建带密码保护的分享
response = requests.post(
    f"{BASE_URL}/api/share/folder",
    headers={"X-Auth": token},
    json={"expires": "7", "unit": "days", "password": "secret123"}
)
```

---

### DeleteShare - 删除分享链接

删除指定的分享链接。

```http
DELETE /api/share/{hash}
X-Auth: <token>
```

**权限要求:** `share` + `download`

**Path Parameters:**
- `hash`: 分享链接的 hash 值

**Response:** `200 OK`

---

## 公共访问接口

以下接口无需认证，通过分享 hash 访问。

### PublicShare - 公共分享访问

通过分享链接访问文件/目录内容。

```http
GET /api/public/share/{hash}[/path]
```

**Path Parameters:**
| 参数 | 说明 |
|------|------|
| `hash` | 分享链接 hash |
| `path` | 分享目录下的子路径（可选） |

**Request Headers (密码保护时):**
| Header | 说明 |
|--------|------|
| `X-SHARE-PASSWORD` | 分享密码 |

**Query Parameters:**
| 参数 | 说明 |
|------|------|
| `token` | 密码保护分享的下载令牌 |

**Response:** 文件/目录的 JSON 信息

---

### PublicDownload - 公共下载

通过分享链接下载文件。

```http
GET /api/public/dl/{hash}[/filename]
```

**Path Parameters:**
| 参数 | 说明 |
|------|------|
| `hash` | 分享链接 hash |
| `filename` | 文件名（可选） |

**Query Parameters:**
| 参数 | 说明 |
|------|------|
| `files` | 多文件下载路径（逗号分隔） |
| `algo` | 打包格式（zip/tar/targz等） |
| `token` | 密码保护分享的令牌 |

**Request Headers (密码保护时):**
| Header | 说明 |
|--------|------|
| `X-SHARE-PASSWORD` | 分享密码 |

**Response:** 文件二进制内容

---

## 外部访问链接格式

创建分享后，可生成以下外部访问链接：

### 分享预览链接

用于在浏览器中预览分享内容（目录列表或文件内容）。

```
{instance_url}/share/{hash}
```

**示例:**
```
http://your-server:8080/share/abc123def456
```

### 直接下载链接

用于直接下载分享的文件或打包下载目录。

```
{instance_url}/api/public/dl/{hash}
```

**示例:**
```
http://your-server:8080/api/public/dl/abc123def456

# 打包下载目录
http://your-server:8080/api/public/dl/abc123def456?algo=zip

# 下载特定文件
http://your-server:8080/api/public/dl/abc123def456/subfolder/file.txt
```

### 密码保护链接访问

当分享设置了密码时，需要传递密码：

**方式一：请求头**
```http
X-SHARE-PASSWORD: your_password
```

**方式二：URL 参数（获取 token 后）**
```
{instance_url}/api/public/dl/{hash}?token={download_token}
```

---

## 完整使用流程

### 创建分享并获取外部链接

```python
# 1. 登录获取 Token
login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "password"}
)
token = login_response.text.strip()

# 2. 创建分享链接
headers = {"X-Auth": token}
share_response = requests.post(
    f"{BASE_URL}/api/share/myfile.pdf",
    headers=headers,
    json={"expires": "24", "unit": "hours"}
)
share_info = share_response.json()

# 3. 生成外部访问链接
preview_url = f"{BASE_URL}/share/{share_info['hash']}"
download_url = f"{BASE_URL}/api/public/dl/{share_info['hash']}"

print(f"预览链接: {preview_url}")
print(f"下载链接: {download_url}")
```

### 创建带密码的分享

```python
# 创建带密码保护的分享
share_response = requests.post(
    f"{BASE_URL}/api/share/private_folder",
    headers=headers,
    json={
        "expires": "7",
        "unit": "days",
        "password": "secret123"
    }
)
share_info = share_response.json()

# 分享链接（访问者需要输入密码）
preview_url = f"{BASE_URL}/share/{share_info['hash']}"
```

---

## 错误处理

| 状态码 | 说明 | 处理 |
|--------|------|------|
| `200` | 成功 | - |
| `201` | 创建成功 | - |
| `401` | 未认证 | 重新登录 |
| `403` | 无分享权限 | 检查用户权限 |
| `404` | 文件不存在 | 检查路径 |
| `4xx` | 密码错误 | 检查分享密码 |