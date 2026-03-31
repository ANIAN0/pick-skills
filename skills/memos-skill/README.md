# Memos Skill

管理和操作 [Memos](https://github.com/usememos/memos) 备忘录系统的 Claude Skill。

## 功能特性

- **完整 Memo 生命周期管理**：创建、读取、更新、删除备忘录
- **高级搜索过滤**：支持 Google AIP-160 过滤语法
- **评论与反应**：添加评论、表情反应
- **附件管理**：上传文件、关联资源
- **多用户支持**：支持多实例配置

## 快速开始

### 1. 安装

将本 skill 目录复制到你的 skills 目录：

```bash
# 例如：~/.claude/skills/ 或你的项目 skills/ 目录
cp -r memos-skill /path/to/your/skills/
```

### 2. 配置

**创建配置文件（推荐外置配置）：**

```bash
# 在项目根目录创建配置
mkdir -p .claude
cat > .claude/config.json << 'EOF'
{
  "instance_url": "https://your-memos-instance.com",
  "access_token": "your-access-token",
  "default_page_size": 10,
  "default_visibility": "PRIVATE"
}
EOF
```

**配置优先级（从高到低）：**

1. `{项目根目录}/.claude/config.json` ⭐ **推荐**
2. `{项目根目录}/.agents/config.json`
3. `{项目根目录}/.config/config.json`
4. `{skill目录}/config.json` ⚠️ 更新时会被覆盖

> **为什么推荐外置配置？**
>
> 通过商店更新 skill 时，整个 skill 目录会被替换，内部 `config.json` 会丢失。外置配置可永久保存。

### 3. 获取访问令牌

1. 登录你的 Memos 实例
2. 进入 Settings → Tokens
3. 点击 "Create Token"
4. 复制生成的令牌填入 `config.json`

### 4. 使用

安装配置完成后，Claude 会在你提到以下关键词时自动触发 memos-skill：

- "帮我记个备忘录..."
- "搜索我之前的笔记..."
- "整理一下标签为 xxx 的备忘录"
- "查看我的备忘录列表"

## 配置示例

```json
{
  "instance_url": "https://memo.example.com",
  "access_token": "eyJhbGciOiJI...",
  "default_page_size": 10,
  "default_visibility": "PRIVATE"
}
```

### 配置字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `instance_url` | string | 是 | - | Memos 实例地址，如 `https://memo.example.com` |
| `access_token` | string | 是 | - | 个人访问令牌（从 Memos 设置获取） |
| `default_page_size` | number | 否 | 10 | 默认分页大小 |
| `default_visibility` | string | 否 | `PRIVATE` | 默认可见性：`PRIVATE`/`PROTECTED`/`PUBLIC` |

## 项目结构

```
memos-skill/
├── SKILL.md                 # Skill 定义（核心逻辑）
├── README.md                # 本文件（使用说明）
├── config.json              # 配置文件模板
└── references/
    └── api-reference.md     # API 详细参考
```

**推荐的项目结构（外置配置）：**

```
your-project/
├── .claude/
│   └── config.json          # 实际配置文件
├── .git/
├── skills/                  # 你的 skills 目录
│   └── memos-skill/         # memos-skill（可通过商店更新）
│       ├── SKILL.md
│       ├── README.md
│       └── ...
└── ...
```

## 常见问题

### Q: 配置放在 skill 目录内可以吗？

可以，但**不推荐**。通过商店更新 skill 时会覆盖整个目录，导致配置丢失。

### Q: 支持多个 Memos 实例吗？

当前配置设计为单实例。如需多实例支持，可以：
1. 创建多个配置文件，手动切换
2. 在请求时动态指定 instance_url

### Q: 访问令牌泄露怎么办？

1. 立即在 Memos 后台删除该 token
2. 重新生成新的 token
3. 更新配置文件

## 相关链接

- [Memos 官方仓库](https://github.com/usememos/memos)
- [Memos API 文档](https://memos.apidocumentation.com)

## 许可证

MIT
