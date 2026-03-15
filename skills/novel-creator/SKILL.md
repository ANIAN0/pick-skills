---
name: novel-creator
description: |
  小说创作主入口，协调整个创作流程。当用户提到"写小说"、"创作小说"、"开始新小说"、"小说项目"、"继续写小说"、"查看小说进度"、"管理小说"或任何与小说创作相关的操作时触发此技能。
---

# Novel Creator Skill

小说创作主技能，负责项目初始化、流程协调、状态管理和子技能调度。

## 核心职责

1. **项目管理** - 初始化、加载、管理小说项目
2. **流程协调** - 按创作阶段调度子技能
3. **状态追踪** - 维护创作进度和上下文
4. **子技能调用** - 根据用户需求调用专业子技能

## 项目结构

```
my-novel/
├── .novel/                       # 隐藏配置目录
│   ├── config.json               # 项目配置
│   ├── state.json                # 创作状态
│   └── vector-index/             # 向量索引(Turso)
├── 00-选题/                       # 选题与定位
│   └── topic.md
├── 01-世界观/                     # 世界观设定
│   ├── magic-system.md
│   ├── geography.md
│   └── history.md
├── 02-角色/                       # 角色设定
│   ├── protagonist.md
│   ├── supporting/
│   └── antagonist.md
├── 03-大纲/                       # 整体大纲
│   └── outline.md
├── 04-分卷/                       # 分卷结构
│   ├── volume-01.md
│   └── volume-02.md
├── 05-故事线/                     # 故事线设计
│   ├── main-plot.md
│   ├── sub-plots.md
│   └── romance-arc.md
├── 06-章纲/                       # 章纲
│   └── chapter-plans.md
└── 07-正文/                       # 章节正文
    ├── chapter-001.md
    └── chapter-002.md
```

## 创作流程

```
选题 → 世界观 → 角色 → 大纲 → 分卷 → 故事线 → 章纲 → 草稿 → 润色 → 审查
  │
  └─ 一句话故事
```

**阶段说明：**

| 阶段 | 技能 | 产出 | 可并行 |
|------|------|------|--------|
| 选题 | novel-topic | 选题文档 | - |
| 一句话故事 | novel-logline | 一句话描述 | 与构思组并行 |
| 世界观 | novel-world | 世界观文档 | ✓ |
| 角色 | novel-characters | 角色设定 | ✓ |
| 大纲 | novel-outline | 大纲文档 | 依赖构思组 |
| 分卷 | novel-volumes | 分卷结构 | - |
| 故事线 | novel-storylines | 故事线文档 | ✓ |
| 章纲 | novel-chapter-plans | 章纲文档 | 依赖结构组 |
| 草稿 | novel-draft | 章节正文 | 按章进行 |
| 润色 | novel-polish | 润色后正文 | - |
| 审查 | novel-review | 审查报告 | - |

## 工作流程

### 1. 初始化新项目

```
用户: "我想写一部新小说"

Claude:
1. 询问小说名称和工作目录
2. 创建项目结构
3. 初始化配置文件
4. 引导用户进入选题阶段
```

### 2. 加载现有项目

```
用户: "继续写我的小说"

Claude:
1. 查找当前目录或上级目录的.novel文件夹
2. 读取 config.json 和 state.json
3. 显示当前进度
4. 询问用户下一步操作
```

### 3. 协调子技能

```
用户: "设计主角"

Claude:
1. 确认项目已加载
2. 检查前置依赖（如世界观是否已创建）
3. 调用 novel-characters 技能
4. 保存产出到 02-角色/ 目录
5. 更新 state.json
6. 询问是否同步知识库
```

## 状态管理

**state.json 结构：**

```json
{
  "project_name": "我的小说",
  "current_phase": "角色创作",
  "phases": {
    "topic": {
      "status": "completed",
      "completed_at": "2026-03-15T10:00:00",
      "output_files": ["00-选题/topic.md"]
    },
    "world": {
      "status": "completed",
      "completed_at": "2026-03-15T12:00:00",
      "output_files": ["01-世界观/magic-system.md", "01-世界观/geography.md"]
    },
    "characters": {
      "status": "in_progress",
      "started_at": "2026-03-15T14:00:00",
      "output_files": []
    }
  },
  "last_updated": "2026-03-15T14:30:00"
}
```

**状态值：**
- `pending` - 未开始
- `in_progress` - 进行中
- `completed` - 已完成
- `skipped` - 已跳过

## 配置管理

**config.json 结构：**

```json
{
  "project_name": "我的小说",
  "version": "1.0.0",
  "created_at": "2026-03-15T10:00:00",
  "settings": {
    "target_word_count": 100000,
    "estimated_chapters": 100,
    "genre": "玄幻",
    "style": "轻松",
    "language": "zh-CN"
  },
  "kb_sync": {
    "chunk_size": 500,
    "chunk_overlap": 100,
    "db_path": ".novel/vector-index/novel_kb.db"
  }
}
```

## 命令行接口

```bash
# 初始化新项目
novel-creator init [项目名称]

# 查看项目状态
novel-creator status

# 进入指定阶段
novel-creator phase <phase-name>

# 同步知识库
novel-creator sync [--full]

# 搜索知识库
novel-creator search <query> [options]
```

## 子技能调用规则

### 自动调用

当用户表达以下意图时，自动调用对应子技能：

| 用户输入 | 调用的技能 |
|----------|------------|
| "确定选题" / "写什么题材" | novel-topic |
| "一句话故事" / "用一句话概括" | novel-logline |
| "设计世界观" / "世界设定" | novel-world |
| "设计角色" / "创建人物" | novel-characters |
| "写大纲" / "故事结构" | novel-outline |
| "分卷" / "卷纲" | novel-volumes |
| "故事线" / "主线暗线" | novel-storylines |
| "写章纲" / "章节大纲" | novel-chapter-plans |
| "写章节" / "生成草稿" | novel-draft |
| "润色" / "优化文字" | novel-polish |
| "审查" / "检查一致性" | novel-review |
| "更新知识库" / "同步向量索引" | novel-kb-update |

### 依赖检查

调用子技能前检查前置条件：

```python
DEPENDENCIES = {
    "novel-outline": ["novel-topic", "novel-world", "novel-characters"],
    "novel-volumes": ["novel-outline"],
    "novel-storylines": ["novel-outline"],
    "novel-chapter-plans": ["novel-volumes", "novel-storylines"],
    "novel-draft": ["novel-chapter-plans"],
    "novel-polish": ["novel-draft"],
    "novel-review": ["novel-draft"]
}
```

**处理方式：**
- 如果依赖未完成，提醒用户并提供选择：
  1. 先完成依赖阶段
  2. 跳过依赖（不推荐）
  3. 同时完成依赖阶段

## 知识库集成

### 自动同步

关键操作后询问是否同步知识库：

1. 创作阶段完成后
2. 重要修改后
3. 审查前

### 手动同步

```
用户: "更新知识库"

Claude:
1. 调用 novel-kb-update 的 sync 命令
2. 显示同步统计
3. 提示用户同步完成
```

### 调用 novel-kb-update 技能

**触发条件：**
- 用户说"更新知识库"、"同步知识库"、"检查一致性"、"审查剧情"
- 用户提到"知识库同步"、"向量索引"
- 需要在小说创作过程中维护内容一致性

**技能行为：**
```
novel-kb-update 执行以下操作：
1. 扫描 00-选题 到 07-正文 目录的 Markdown 文件
2. 计算文件哈希，识别新增/修改/删除的文件
3. 对修改的文件重新分块、生成向量（SiliconFlow API）
4. 更新 Turso 向量数据库
5. 返回同步统计信息
```

**同步模式：**
- **增量同步**（默认）：只处理修改的文件
- **全量重建**：`--full` 参数，重建整个索引

**技术架构：**
```
Markdown 文件 → 分块 → 向量化 → Turso 索引
                    ↓
              保留文件路径引用
```

- **主存储**：Markdown 文件（人类可读、版本控制）
- **向量索引**：Turso 数据库（语义检索）
- **嵌入模型**：BAAI/bge-m3（1024维）
- **API**：SiliconFlow API

### 在审查流程中使用

```
novel-review 技能执行审查时：
1. 自动调用 novel-kb-update 确保知识库最新
2. 使用 search_knowledge() 查询相关内容
3. 对比检查一致性
4. 生成审查报告
```

## 最佳实践

1. **频繁保存** - 每个子技能完成后自动保存产出
2. **定期同步** - 建议每个创作会话后同步知识库
3. **保持依赖** - 按顺序完成创作阶段，确保质量
4. **版本控制** - 建议对项目目录使用 git 管理

## 错误处理

**常见错误：**

| 错误 | 处理 |
|------|------|
| 未找到项目 | 提示初始化新项目或指定项目路径 |
| 依赖未完成 | 显示依赖关系，提供处理选项 |
| 知识库同步失败 | 检查 API token，提供手动同步选项 |
| 文件写入失败 | 检查目录权限，尝试创建目录 |

## 与其他技能的关系

```
novel-creator (主技能)
    ├── novel-topic
    ├── novel-logline
    ├── novel-world
    ├── novel-characters
    ├── novel-outline
    ├── novel-volumes
    ├── novel-storylines
    ├── novel-chapter-plans
    ├── novel-draft
    ├── novel-polish
    ├── novel-review
    └── novel-kb-update (基础设施)
```

## 文件位置

- 主技能: `skills/novel-creator/SKILL.md`
- 项目脚本: `skills/novel-creator/scripts/`
  - `project_manager.py` - 项目管理
  - `state_manager.py` - 状态管理
  - `cli.py` - 命令行接口
