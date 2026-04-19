# 技能管理

`skills_manager.py` 脚本的详细使用说明。

## 功能

封装 `npx skills` 命令，管理技能包：
- `find` - 搜索技能
- `add` - 安装技能
- `check` - 检查更新
- `update` - 更新所有技能
- `list` - 列出已安装技能

## 命令

### 搜索技能

```bash
# 交互式搜索
python scripts/skills_manager.py find

# 搜索指定关键词
python scripts/skills_manager.py find "react testing"
```

### 安装技能

```bash
# 全局安装（推荐）
python scripts/skills_manager.py add "vercel-labs/agent-skills@react-best-practices"

# 本地安装
python scripts/skills_manager.py add "vercel-labs/agent-skills@react-best-practices" --no-global

# 需要确认
python scripts/skills_manager.py add "vercel-labs/agent-skills@react-best-practices" --confirm
```

### 检查更新

```bash
python scripts/skills_manager.py check
```

### 更新所有技能

```bash
python scripts/skills_manager.py update
```

### 列出已安装技能

```bash
python scripts/skills_manager.py list
```

## 参数

| 参数 | 说明 |
|------|------|
| `command` | 执行命令：find/add/check/update/list |
| `args` | 命令参数（如搜索关键词或技能包名） |
| `--no-global` | 本地安装（不使用 -g 标志） |
| `--confirm` | 需要确认（不使用 -y 标志） |

## 技能包格式

技能包名称格式：`owner/repo@skill-name`

示例：
- `vercel-labs/agent-skills@react-best-practices`
- `anthropics/skills@frontend-design`

## 输出示例

### 搜索

```
🔍 搜索技能: react testing

🔧 执行命令: npx skills find react testing

[输出 npx skills 的搜索结果]
```

### 安装

```
📥 安装技能: vercel-labs/agent-skills@react-best-practices

🔧 执行命令: npx skills add vercel-labs/agent-skills@react-best-practices -g -y

[输出 npx skills 的安装结果]
```

### 检查更新

```
🔔 检查技能更新...

🔧 执行命令: npx skills check

[输出 npx skills 的检查结果]
```

### 更新

```
⬆️ 更新所有技能...

🔧 执行命令: npx skills update

[输出 npx skills 的更新结果]
```

## 安装模式

### 全局安装（-g）

安装到用户级别，所有项目共享：
- Windows: `%USERPROFILE%\.skills\`
- macOS/Linux: `~/.skills/`

推荐用于通用技能。

### 本地安装

安装到当前项目，仅本项目可用：
- 项目目录下的 `.skills/`

推荐用于项目特定技能。

## 技能来源

常用技能来源：

| 来源 | 说明 |
|------|------|
| `vercel-labs/agent-skills` | Vercel 官方技能包（React、Next.js 等） |
| `anthropics/skills` | Anthropic 官方技能包 |
| `ComposioHQ/awesome-claude-skills` | Claude 社区技能合集 |

## 技能浏览

在线浏览技能：https://skills.sh/

## 使用建议

### 推荐工作流

```bash
# 1. 搜索需要的技能
python scripts/skills_manager.py find "react"

# 2. 安装（全局安装，跳过确认）
python scripts/skills_manager.py add "vercel-labs/agent-skills@react-best-practices"

# 3. 定期检查更新
python scripts/skills_manager.py check

# 4. 更新所有技能
python scripts/skills_manager.py update
```

### 直接使用 npx skills

脚本只是封装，可直接运行：

```bash
npx skills find react testing
npx skills add vercel-labs/agent-skills@react-best-practices -g -y
npx skills check
npx skills update
```

## 错误处理

| 错误 | 处理 |
|------|------|
| 命令超时（120秒） | 返回超时错误 |
| 执行异常 | 返回异常信息 |
| npx 不可用 | 需要安装 Node.js |

## 前置依赖

需要安装 Node.js 和 npm：
- Node.js 18+ 推荐
- npm 随 Node.js 安装

检查安装：
```bash
node --version
npm --version
```