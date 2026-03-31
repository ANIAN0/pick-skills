# AI辅助小说创作系统技术分享

## 概述

本次分享介绍我们最近实现的AI辅助小说创作系统。这是一个模块化的技能系统，通过多技能协作、状态管理和知识库同步，帮助作者进行小说创作。

---

## 一、系统架构

### 1.1 整体设计理念

系统的核心设计原则是**流程驱动、渐进确认**：

- 不是一次性输出大量内容，而是多轮交互逐步确认
- 严格的前置检查，防止跳步和失控创作
- 模块化技能设计，可独立使用或组合调用

### 1.2 技能模块结构

系统包含以下核心技能模块：

| 技能名称 | 功能定位 | 是否必须 |
|---------|---------|---------|
| `novel-creator` | 总控技能，协调其他技能 | 必须 |
| `novel-topic` | 选题确认 | 必须 |
| `novel-logline` | 三句话故事确认 | 必须 |
| `novel-draft` | 章节草稿创作 | 必须 |
| `novel-polish` | 正文定稿与风格沉淀 | 必须 |
| `novel-volumes` | 分卷设计 | 必须 |
| `novel-storylines` | 分卷故事线与故事单元 | 必须 |
| `novel-review` | 章节审查 | 推荐 |
| `novel-world` | 世界观设定 | 可选 |
| `novel-characters` | 角色设定 | 可选 |
| `novel-kb-update` | 知识库同步 | 可选 |

### 1.3 主流程调用链

```
选题确认 -> 三句话故事 -> 第1章草稿 -> 第1章正文定稿 -> 分卷确认
    -> 分卷故事线 -> 故事单元 -> 章节规划 -> 后续章节草稿 -> 章节定稿 -> 章节审查
```

---

## 二、核心技术实现

### 2.1 状态管理机制

状态管理是系统的核心，通过JSON文件追踪创作进度：

**文件位置**: `.novel/state.json`

**核心状态字段**:
```json
{
  "topic_confirmed": false,
  "story_3lines_confirmed": false,
  "chapter1_draft_confirmed": false,
  "chapter1_final_confirmed": false,
  "volumes_confirmed": false
}
```

**状态管理器实现要点** (参考 `state_manager.py`):

1. **阶段定义**: 将创作过程划分为11个阶段，每个阶段有顺序和依赖关系
2. **依赖检查**: 某些阶段需要前置阶段完成才能开始
3. **进度追踪**: 记录每个阶段的开始时间、完成时间、产出文件

**阶段依赖关系**:
```python
DEPENDENCIES = {
    "outline": ["topic", "world", "characters"],
    "volumes": ["outline"],
    "storylines": ["outline"],
    "chapter_plans": ["volumes", "storylines"],
    "draft": ["chapter_plans"],
    "polish": ["draft"],
    "review": ["draft"]
}
```

### 2.2 前置检查机制

每个技能在执行前会检查前置条件是否满足：

```markdown
## 前置条件（强制）

必须满足：
1. `topic_confirmed = true`
2. `story_3lines_confirmed = true`

否则不得执行第1章草稿，需引导用户先完成前置阶段。
```

这样做的好处：
- 防止用户跳过关键步骤
- 保证创作的一致性和连贯性
- 减少因前置信息缺失导致的返工

### 2.3 交互规则设计

系统采用"5选项+推荐"的交互模式：

```markdown
每轮必须提供：
- 5 个候选选项（A-E）
- 1 个推荐选项 + 一句推荐理由
- 等待用户反馈后重写下一轮
- 直到用户明确说出"确认/定稿/就这个"才进入下一阶段
```

设计理由：
1. 给用户选择权，而非直接输出结果
2. 推荐选项帮助用户快速决策
3. 多轮迭代确保结果符合用户预期
4. 明确确认机制防止误解

### 2.4 偏好记录机制

系统维护两个偏好记录文件：

- `99-偏好记录/positive-patterns.md`: 用户肯定的创作习惯
- `99-偏好记录/negative-patterns.md`: 用户否定的创作习惯

记录原则：
- 只记录会直接影响创作结果的偏好
- 用户明确肯定的写法记入正向记录
- 用户明确否定的写法记入负向记录
- 后续章节创作时自动参考这些偏好

---

## 三、知识库同步方案

### 3.1 技术选型

采用**混合存储方案**：

- **Markdown文件**: 作为原文存储（主存储）
- **Turso数据库**: 存储向量索引（用于语义检索）
- **SiliconFlow API**: 向量生成服务

**向量模型**: BAAI/bge-m3（1024维）

### 3.2 数据库表结构

```sql
-- 文件表
CREATE TABLE kb_files (
    file_path TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    content_type TEXT NOT NULL,
    modified_time TEXT NOT NULL,
    indexed_at TEXT NOT NULL
);

-- 文本块表（带向量）
CREATE TABLE kb_chunks (
    chunk_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    heading TEXT,
    content TEXT NOT NULL,
    content_vector F32_BLOB(1024) NOT NULL,
    chunk_index INTEGER NOT NULL,
    ...
);

-- 向量索引
CREATE INDEX idx_kb_chunks_vector
ON kb_chunks(libsql_vector_idx(content_vector));
```

### 3.3 文本分块策略

```python
def chunk_text(text: str, chunk_size=500, overlap=100):
    # 500字符为单位，100字符重叠
    # 尽量在句子边界分割（句号、问号、感叹号）
```

### 3.4 同步流程

1. 扫描项目中的所有Markdown文件
2. 计算文件哈希，对比已索引文件
3. 处理新增、修改、删除的文件
4. 对每个变更文件进行分块和向量生成
5. 更新数据库索引

**命令行使用**:
```bash
# 增量同步
python kb_sync.py sync

# 全量重建
python kb_sync.py sync --full

# 语义搜索
python kb_sync.py search "主角的性格特点" -n 5
```

---

## 四、项目文件结构

```
my-novel/
├── .novel/
│   ├── config.json           # 项目配置
│   ├── state.json            # 状态追踪
│   └── vector-index/         # 知识库索引
├── 00-选题/
│   ├── topic.md              # 选题定稿
│   └── story-3lines.md       # 三句话故事
├── 01-第1章/
│   ├── chapter-01-draft.md   # 草稿
│   ├── chapter-01-final.md   # 正文定稿
│   └── style-profile.md      # 写作风格档案
├── 02-分卷/
│   ├── volume-plan.md        # 分卷方案
│   └── volume-storylines.md  # 分卷故事线
├── 03-故事单元/
│   ├── unit-001.md           # 故事单元详情
│   └── unit-002.md
├── 04-正文/
│   ├── chapter-001.md        # 章节正文
│   ├── chapter-002.md
├── 99-偏好记录/
│   ├── positive-patterns.md  # 正向偏好
│   └── negative-patterns.md  # 负向偏好
```

---

## 五、关键设计决策

### 5.1 为什么采用"先内容后风格"？

第1章创作分为两个阶段：
1. 草稿阶段：只写故事事实、行动链、冲突变化
2. 正文阶段：基于草稿确定风格

**好处**：
- 避免过早纠结文风而忽略剧情
- 风格确定后形成 `style-profile.md`，后续章节自动遵循

### 5.2 为什么设计"故事单元"概念？

每个故事单元必须：
- 围绕一个核心目标
- 以一个强卡点收尾
- 包含2-4个核心事件

**好处**：
- 避免章节散乱、偏离主线
- 卡点机制保证读者追更动力
- 单元目标明确，便于检查质量

### 5.3 为什么可选技能不阻塞主流程？

世界观(`novel-world`)和角色(`novel-characters`)设为可选：

- 很多作者不需要完整世界观设计
- 按需补充，不强制一次性完成
- 主流程（选题->第1章->分卷->章节）必须通畅

---

## 六、未来扩展方向

1. **多语言支持**: 当前系统主要为中文小说设计
2. **协作功能**: 多人协作创作的版本管理
3. **智能建议**: 基于历史偏好自动推荐创作方向
4. **导出格式**: 支持多种电子书格式导出

---

## 七、技术栈总结

| 层面 | 技术选型 |
|-----|---------|
| 技能定义 | Markdown + YAML frontmatter |
| 状态管理 | Python + JSON |
| 知识库 | Turso (libSQL) + 向量索引 |
| 向量生成 | SiliconFlow API (BAAI/bge-m3) |
| 文本存储 | Markdown 文件 |

---

## 总结

本次分享介绍了AI辅助小说创作系统的核心架构和关键技术：

1. **模块化技能设计**: 总控技能 + 子技能的路由调用
2. **状态管理机制**: 前置检查、阶段依赖、进度追踪
3. **知识库同步**: Turso + 向量索引的混合存储方案
4. **交互规则**: "5选项+推荐"的多轮确认模式

系统的设计核心是**流程驱动、渐进确认**，通过严格的前置检查和明确的交互规则，确保创作过程的稳定性和可控性。

---

**问答环节** (10分钟)

欢迎各位同事提问交流。