# Search Service

搜索服务的完整 API 参考。支持在指定目录下搜索文件。

## 基础端点

`/api/search{path}` - 文件搜索

---

## 接口列表

### SearchFiles - 文件搜索

在指定目录下搜索匹配关键词的文件。

```http
GET /api/search{path}?query={keyword}
X-Auth: <token>
```

**Path Parameters:**
- `path`: 搜索的起始目录路径

**Query Parameters:**
| 参数 | 说明 |
|------|------|
| `query` | 搜索关键词 |

**Response Format:** Server-Sent Events (SSE) 流式返回

每行返回一个 JSON 结果：
```json
{"dir": false, "path": "/folder/file.txt"}
{"dir": true, "path": "/folder/subfolder"}
{"dir": false, "path": "/another_file.pdf"}
```

**字段说明:**
| 字段 | 说明 |
|------|------|
| `dir` | 是否为目录 |
| `path` | 文件/目录的完整路径 |

---

## 使用示例

### Python 示例

```python
import requests

# 搜索文件
def search_files(base_url, token, search_path, keyword):
    url = f"{base_url}/api/search{search_path}"
    headers = {"X-Auth": token}
    params = {"query": keyword}
    
    response = requests.get(url, headers=headers, params=params, stream=True)
    
    results = []
    for line in response.iter_lines():
        if line:
            result = json.loads(line)
            results.append(result)
    
    return results

# 使用示例
results = search_files(
    base_url="http://localhost:8080",
    token=token,
    search_path="/",
    keyword="report"
)

for r in results:
    if r["dir"]:
        print(f"目录: {r['path']}")
    else:
        print(f"文件: {r['path']}")
```

### 搜索后下载

```python
# 搜索并下载匹配的文件
results = search_files(BASE_URL, token, "/", "backup")

for r in results:
    if not r["dir"]:  # 只下载文件，跳过目录
        download_url = f"{BASE_URL}/api/raw{r['path']}"
        response = requests.get(download_url, headers={"X-Auth": token})
        
        filename = r['path'].split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"下载完成: {filename}")
```

---

## 搜索范围

搜索在指定的起始目录及其所有子目录中进行。

| 搜索路径 | 搜索范围 |
|----------|----------|
| `/` | 整个文件系统 |
| `/documents` | 仅 documents 目录及其子目录 |
| `/projects/2024` | 仅指定项目目录 |

---

## 搜索特性

### 实时流式返回

搜索结果通过 SSE 流式返回，无需等待搜索完成即可处理结果。

### 大小写敏感

搜索默认对文件名进行匹配，不同系统可能有大小写敏感差异。

### 匹配规则

- 匹配文件名中包含关键词的文件
- 同时返回匹配的目录和文件
- 路径为完整绝对路径

---

## 结合其他接口使用

### 搜索 + 获取文件信息

```python
results = search_files(BASE_URL, token, "/", "image")

for r in results:
    if not r["dir"]:
        # 获取文件详细信息
        info_url = f"{BASE_URL}/api/resources{r['path']}"
        info = requests.get(info_url, headers={"X-Auth": token}).json()
        
        print(f"文件: {info['name']}")
        print(f"大小: {info['size']} bytes")
        print(f"类型: {info['type']}")
```

### 搜索 + 创建分享

```python
results = search_files(BASE_URL, token, "/", "report.pdf")

for r in results:
    if not r["dir"]:
        # 创建分享链接
        share_response = requests.post(
            f"{BASE_URL}/api/share{r['path']}",
            headers={"X-Auth": token},
            json={"expires": "24", "unit": "hours"}
        )
        share_info = share_response.json()
        
        share_url = f"{BASE_URL}/share/{share_info['hash']}"
        print(f"分享链接: {share_url}")
```

---

## 错误处理

| 状态码 | 说明 | 处理 |
|--------|------|------|
| `200` | 成功（流式返回） | - |
| `401` | 未认证 | 重新登录 |
| `404` | 搜索目录不存在 | 检查路径 |
| `400` | 缺少 query 参数 | 添加关键词 |