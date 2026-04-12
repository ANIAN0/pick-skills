# Memos Skill

管理和操作 [Memos](https://github.com/usememos/memos) 备忘录系统的 Claude Skill。

适用于个人知识管理、快速记录想法、整理笔记内容。

## 功能

- **备忘录管理**: 创建、查询、更新、删除
- **高级搜索**: Google AIP-160 过滤语法
- **附件上传**: 图片、文件附件

## 快速开始

### 1. 配置

在项目根目录创建 `skillconfig.json`：

```json
{
  "memos": {
    "instance_url": "https://your-memos-instance.com",
    "access_token": "your-access-token"
  }
}
```

### 2. 获取令牌

1. 登录 Memos → Settings → Tokens
2. Create Token → 复制令牌

### 3. 使用

触发关键词：
- "帮我记个备忘录..."
- "搜索关于 xxx 的笔记"
- "查看我的备忘录列表"

## 项目结构

```
memos-skill/
├── SKILL.md              # 接口索引 + 配置说明
├── README.md             # 本文件
└── references/
    ├── memo-service.md   # 备忘录接口
    └── attachment-service.md  # 附件接口
```

## 相关链接

- [Memos 官方仓库](https://github.com/usememos/memos)

MIT