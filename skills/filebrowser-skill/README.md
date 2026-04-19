# FileBrowser Skill

管理和操作 [FileBrowser](https://github.com/filebrowser/filebrowser) 文件管理系统的 Claude Skill。

适用于个人文件管理、团队文件共享、云端备份同步等场景。

## 功能

- **文件操作**: 上传、下载、预览、删除
- **分享管理**: 创建分享链接、获取外部访问链接
- **文件搜索**: 在云端搜索文件
- **同步功能**: 本地与云端双向同步

## 快速开始

### 1. 配置

在项目根目录创建 `skillconfig.json`：

```json
{
  "filebrowser": {
    "instance_url": "http://your-server:8080",
    "username": "admin",
    "password": "your-password"
  }
}
```

### 2. 获取凭据

1. 登录 FileBrowser
2. 记录用户名和密码

### 3. 使用

触发关键词：
- "上传文件到云端..."
- "帮我分享这个文件..."
- "搜索云端文件..."
- "同步本地和云端文件..."

## 项目结构

```
filebrowser-skill/
├── SKILL.md                    # 接口索引 + 配置说明
├── README.md                   # 本文件
├── references/
│   ├── auth-service.md         # 认证接口
│   ├── resource-service.md     # 文件操作接口
│   ├── share-service.md        # 分享接口
│   └── search-service.md       # 搜索接口
└── scripts/
    ├── upload_and_share.py     # 上传单文件获取分享链接
    └── directory_sync.py       # 目录同步工具
```

## 脚本使用

### upload_and_share.py - 上传单文件获取分享链接

上传单个文件并自动创建分享链接，获取预览、下载、直接查看链接。

```bash
# 上传文件并创建永久分享
python upload_and_share.py --url http://server:8080 --user admin --password pwd --file ./report.pdf

# 上传文件并创建24小时有效的分享
python upload_and_share.py --url http://server:8080 --user admin --password pwd --file ./report.pdf --expires 24 --unit hours

# 上传文件并创建带密码保护的分享
python upload_and_share.py --url http://server:8080 --user admin --password pwd --file ./report.pdf --share-password secret123

# 上传到指定远程路径
python upload_and_share.py --url http://server:8080 --user admin --password pwd --file ./report.pdf --remote /documents/report.pdf
```

**输出示例:**
```
✅ 登录成功: admin
✅ 上传成功: /report.pdf

📋 分享链接:
  预览链接: http://server:8080/share/abc123
  下载链接: http://server:8080/api/public/dl/abc123
  直接查看: http://server:8080/api/public/dl/abc123?inline=true
```

### directory_sync.py - 目录同步工具

上传、下载或同步整个目录。

```bash
# 上传整个目录到云端
python directory_sync.py upload --url http://server:8080 --user admin --password pwd --local ./data --remote /backup

# 从云端下载整个目录
python directory_sync.py download --url http://server:8080 --user admin --password pwd --remote /backup --local ./data

# 智能上传（只上传变化的文件）
python directory_sync.py sync-up --url http://server:8080 --user admin --password pwd --local ./data --remote /backup

# 智能下载（只下载变化的文件）
python directory_sync.py sync-down --url http://server:8080 --user admin --password pwd --remote /backup --local ./data

# 双向同步（本地云端互相同步）
python directory_sync.py sync --url http://server:8080 --user admin --password pwd --local ./data --remote /backup
```

## 外部链接格式

| 类型 | 链接格式 |
|------|----------|
| 分享预览 | `{instance_url}/share/{hash}` |
| 直接下载 | `{instance_url}/api/public/dl/{hash}` |
| 内部下载 | `{instance_url}/api/raw{path}` |

## 相关链接

- [FileBrowser 官方仓库](https://github.com/filebrowser/filebrowser)
- [FileBrowser 文档](https://filebrowser.org)

MIT