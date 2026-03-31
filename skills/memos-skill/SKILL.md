---
name: memos-skill
description: |
  管理和操作 Memos 备忘录系统。当用户提到备忘录、memos、记录笔记、查看笔记、搜索备忘录、整理备忘录或任何与 memos 相关的操作时触发此 skill。支持创建备忘录、获取备忘录列表、搜索过滤、更新删除、管理附件、评论反应等功能。适用于个人知识管理、快速记录想法、整理笔记内容等场景。
---

# Memos Skill

管理你的 Memos 备忘录实例，支持完整的备忘录生命周期操作。

## 配置

在使用 memos API 之前，需要创建配置文件。

### 配置文件位置

**推荐方案（更新 skill 时不会被覆盖）：**

配置文件应放在 skill 目录之外的上级目录中，支持以下位置（按优先级查找）：

```
项目根目录/
├── .claude/                    ← 推荐位置
│   └── config.json             # 直接放这里
├── .agents/                    ← 备选位置
│   └── config.json
├── .config/                    ← 备选位置
│   └── config.json
├── skills/
│   └── memos-skill/
│       ├── SKILL.md
│       └── config.json         ← 备选（更新会被覆盖）
└── ...
```

**查找优先级：**
1. `{skill_dir}/../../.claude/config.json`
2. `{skill_dir}/../../.agents/config.json`
3. `{skill_dir}/../../.config/config.json`
4. `{skill_dir}/config.json` （skill 目录内，更新会被覆盖）

### 配置文件格式

```json
{
  "instance_url": "https://your-memos-instance.com",
  "access_token": "your-access-token",
  "default_page_size": 10,
  "default_visibility": "PRIVATE"
}
```

### 配置说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `instance_url` | string | 是 | 你的 memos 实例地址，如 `https://memo.example.com` |
| `access_token` | string | 是 | 个人访问令牌 |
| `default_page_size` | number | 否 | 默认分页大小（默认10） |
| `default_visibility` | string | 否 | 默认可见性（`PRIVATE`, `PROTECTED`, `PUBLIC`） |

### 获取访问令牌

1. 登录你的 memos 实例
2. 进入 Settings → Tokens
3. 点击 "Create Token"
4. 复制生成的令牌并填入 config.json

### 在代码中读取配置

**推荐方式（自动查找配置）：**

```python
import json
import os

def get_config():
    """查找并读取 memos-skill 配置"""
    skill_dir = os.path.dirname(os.path.abspath(__file__))

    # 配置查找路径（按优先级）
    config_paths = [
        # 推荐：外置配置（更新 skill 时不会被覆盖）
        os.path.join(skill_dir, '..', '..', '.claude', 'config.json'),
        os.path.join(skill_dir, '..', '..', '.agents', 'config.json'),
        os.path.join(skill_dir, '..', '..', '.config', 'config.json'),
        # 备选：skill 目录内（更新会被覆盖）
        os.path.join(skill_dir, 'config.json'),
    ]

    for path in config_paths:
        path = os.path.normpath(path)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

    raise FileNotFoundError(
        "未找到 memos-skill 配置文件。请创建以下位置的 config.json：\n"
        f"  - {config_paths[0]}\n"
        f"  - {config_paths[1]}\n"
        "详见 README.md"
    )

# 读取配置
config = get_config()
instance_url = config['instance_url']
access_token = config['access_token']
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}
```

## 核心功能

### 1. Memo 管理

#### 创建备忘录
- **端点**: POST `/api/v1/memos`
- **关键字段**:
  - `content`: 备忘录内容（支持 Markdown）
  - `visibility`: 可见性（`PRIVATE`, `PROTECTED`, `PUBLIC`）
  - `tags`: 标签数组
  - `resources`: 关联资源

**示例**:
```json
{
  "content": "今天要完成的任务：\n- 完成项目文档\n- 回复客户邮件",
  "visibility": "PRIVATE",
  "tags": ["todo", "work"]
}
```

#### 获取备忘录列表
- **端点**: GET `/api/v1/memos`
- **参数**:
  - `pageSize`: 每页数量（默认 10）
  - `pageToken`: 分页令牌
  - `filter`: 过滤条件（遵循 Google AIP-160 标准）
    - `creator == "users/1"`: 按创建者过滤
    - `row_status == "NORMAL"`: 正常状态的备忘录
    - `create_time > "2024-01-01"`: 按创建时间过滤
    - `tag == "work"`: 按标签过滤
    - `content.contains("关键词")`: 内容搜索
  - `sort`: 排序方式（`createTime`, `updateTime`）

#### 获取单个备忘录
- **端点**: GET `/api/v1/memos/{memo}`
- 返回完整的备忘录详情，包括内容、标签、评论等

#### 更新备忘录
- **端点**: PATCH `/api/v1/memos/{memo}`
- 使用 `updateMask` 指定要更新的字段，如 `content,visibility,tags`

#### 删除备忘录
- **端点**: DELETE `/api/v1/memos/{memo}`

### 2. 搜索与过滤

使用 Google AIP-160 过滤语法进行高级搜索：

```
# 组合条件
content.contains("项目") AND tag == "work"

# 按时间范围
create_time > "2024-01-01" AND create_time < "2024-12-31"

# 多标签查询
tag == "work" OR tag == "personal"

# 排除条件
NOT tag == "archive"

# 完整示例
filter: "creator == \"users/1\" AND (tag == \"work\" OR tag == \"urgent\") AND create_time > \"2024-01-01\""
```

### 3. 评论与反应

#### 添加评论
- **端点**: POST `/api/v1/memos/{memo}/comments`

#### 获取评论列表
- **端点**: GET `/api/v1/memos/{memo}/comments`

#### 添加反应（表情）
- **端点**: POST `/api/v1/memos/{memo}/reactions`
- 支持的表情：`THUMBS_UP`, `THUMBS_DOWN`, `HEART`, `FIRE`, `ROCKET`, `EYES`, `THINKING`, `CLAPPING`, `PARTY`, `ROCKET`

### 4. 附件管理

#### 上传附件
- **端点**: POST `/api/v1/attachments`
- 支持 multipart/form-data 上传文件

#### 获取附件列表
- **端点**: GET `/api/v1/attachments`

#### 将附件关联到备忘录
- **端点**: POST `/api/v1/memos/{memo}/attachments`
- 请求体：`{"attachmentIds": ["attachments/1", "attachments/2"]}`

### 5. 关联备忘录

#### 创建关联
- **端点**: POST `/api/v1/memos/{memo}/relations`
- 关联类型：`REFERENCE`, `COMMENT`

### 6. 用户管理

#### 获取当前用户
- **端点**: GET `/api/v1/auth/status`

#### 创建个人访问令牌
- **端点**: POST `/api/v1/users/{user}/personalAccessTokens`
- 返回的 `token` 只在创建时显示一次

## API 请求格式

### 认证头
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

### 标准响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 错误响应
```json
{
  "code": 3,
  "message": "Invalid argument",
  "details": []
}
```

## 使用场景示例

### 场景 1: 快速记录想法
用户说："帮我记录一条备忘录，内容是今天和客户的会议要点..."
```http
POST /api/v1/memos
{
  "content": "今天和客户的会议要点：\n1. 确认交付时间...",
  "visibility": "PRIVATE",
  "tags": ["meeting", "client"]
}
```

### 场景 2: 搜索备忘录
用户说："搜索我上个月关于项目的备忘录"
```http
GET /api/v1/memos?filter=content.contains("项目") AND create_time > "2024-02-01"&pageSize=20
```

### 场景 3: 批量整理
用户说："把标签为'temp'的所有备忘录改成'archive'"
```http
GET /api/v1/memos?filter=tag == "temp"&pageSize=100
# 然后对每个 memo 调用 PATCH 更新标签
```

### 场景 4: 带附件的备忘录
用户说："创建一个备忘录并附上这张图片"
```http
# 1. 先上传附件
POST /api/v1/attachments
Content-Type: multipart/form-data

# 2. 创建备忘录
POST /api/v1/memos
{
  "content": "图片说明...",
  "resources": [{"name": "attachments/1"}]
}
```

### 场景 5: 配置 memos 实例
用户说："把我的 memos 实例配置为 https://memo.example.com，token 是 abc123"

**处理步骤：**
1. 优先检查外置配置目录（`.claude/` 或 `.agents/`）
2. 如果外置目录不存在，创建它
3. 创建或更新外置配置文件
4. 验证配置（可选：发送测试请求）
5. 返回配置成功的确认信息

**代码示例：**
```python
import json
import os

def get_skill_dir():
    """获取 skill 目录路径"""
    return os.path.dirname(os.path.abspath(__file__))

def get_external_config_dir():
    """获取外置配置目录（推荐位置）"""
    skill_dir = get_skill_dir()
    # 尝试找到 .claude 或 .agents 目录
    for config_dir in ['.claude', '.agents', '.config']:
        external_dir = os.path.normpath(os.path.join(skill_dir, '..', '..', config_dir))
        if os.path.exists(os.path.dirname(external_dir)):
            return external_dir
    # 默认使用 .claude
    return os.path.normpath(os.path.join(skill_dir, '..', '..', '.claude'))

# 配置内容
config = {
    "instance_url": "https://memo.example.com",
    "access_token": "abc123",
    "default_page_size": 10,
    "default_visibility": "PRIVATE"
}

# 确定配置文件路径（优先外置）
config_dir = get_external_config_dir()
os.makedirs(config_dir, exist_ok=True)
config_path = os.path.join(config_dir, 'config.json')

# 保存配置
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"配置已保存到: {config_path}")
print("注意：使用外置配置可避免更新 skill 时被覆盖")
```

## 输出格式建议

根据用户需求，灵活返回以下格式：

1. **简要摘要**: 返回备忘录标题/ID、创建时间、标签列表
2. **完整内容**: 返回完整内容（包括 Markdown 渲染）
3. **表格形式**: 多条备忘录时用表格展示 ID、内容预览、时间、标签
4. **JSON 格式**: 用户需要编程处理时返回原始 JSON

## 最佳实践

1. **内容格式**: 鼓励使用 Markdown 格式编写备忘录内容
2. **标签管理**: 建议使用统一的标签命名规范（小写、用连字符连接）
3. **可见性设置**: 默认为 PRIVATE，分享时才设为 PUBLIC
4. **分页处理**: 列表查询时注意处理分页，避免一次返回过多数据
5. **错误处理**: API 可能返回 401（未授权）、404（不存在）、400（参数错误）等状态码

## 注意事项

- 备忘录 ID 格式为 `memos/{id}`，如 `memos/123`
- 用户 ID 格式为 `users/{id}`，如 `users/1`
- 附件 ID 格式为 `attachments/{id}`
- 创建时间字段是 ISO 8601 格式，如 `2024-03-12T10:30:00Z`
- 更新操作使用 PATCH，需要指定 updateMask 避免覆盖其他字段
