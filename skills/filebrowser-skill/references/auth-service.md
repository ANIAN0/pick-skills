# Auth Service

认证服务的完整 API 参考。

## 基础端点

认证相关接口无需额外权限，用于获取和管理 JWT Token。

---

## 接口列表

### Login - 用户登录

获取 JWT Token，用于后续所有 API 请求的认证。

```http
POST /api/login
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "recaptcha": "string"  // 可选，启用 ReCaptcha 时需要
}
```

**Response:**
- 状态码: `200 OK`
- 内容: 纯文本 JWT Token

**Response Headers:**
| Header | 说明 |
|--------|------|
| `X-Renew-Token` | `true` 表示 Token 即将过期，需要续期 |

**示例:**
```python
response = requests.post(f"{BASE_URL}/api/login", json={
    "username": "admin",
    "password": "password"
})
token = response.text.strip()
```

---

### Renew - Token 续期

续期即将过期的 JWT Token（默认有效期 2 小时）。

```http
POST /api/renew
X-Auth: <token>
```

**认证:** 需要有效的 JWT Token

**Response:**
- 状态码: `200 OK`
- 内容: 新的 JWT Token（纯文本）

**Response Headers:**
| Header | 说明 |
|--------|------|
| `X-Renew-Token` | `false` 表示无需续期 |

**示例:**
```python
headers = {"X-Auth": token}
response = requests.post(f"{BASE_URL}/api/renew", headers=headers)
new_token = response.text.strip()
```

---

## Token 使用方式

获取 Token 后，可通过以下方式认证：

### 方式一：请求头

```http
X-Auth: <token>
```

适用于所有 HTTP 方法（GET、POST、PUT、DELETE 等）。

### 方式二：Cookie

```http
Cookie: auth=<token>
```

仅适用于 GET 请求。

---

## 认证流程

### 标准流程

1. 调用 `/api/login` 获取 Token
2. 将 Token 存入请求头 `X-Auth`
3. 进行 API 操作
4. 检查响应头 `X-Renew-Token`
5. 如需续期，调用 `/api/renew`

### Python 示例

```python
class FileBrowserClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # 登录获取 Token
        response = self.session.post(
            f"{self.base_url}/api/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.text.strip()
            self.session.headers.update({"X-Auth": self.token})
    
    def renew_if_needed(self):
        """检查并续期 Token"""
        response = self.session.post(f"{self.base_url}/api/renew")
        if response.status_code == 200:
            self.token = response.text.strip()
            self.session.headers.update({"X-Auth": self.token})
```

---

## 错误处理

| 错误 | 说明 | 处理 |
|------|------|------|
| `401 Unauthorized` | Token 无效或过期 | 重新登录 |
| `403 Forbidden` | 用户被禁用 | 检查用户状态 |
| `400 Bad Request` | 请求参数错误 | 检查 JSON 格式 |