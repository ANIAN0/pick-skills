# 项目知识库结构模板

本模板用于第 3 层 `project-kb/`。知识库结构以代码文件镜像为核心，不再按项目类型预设大量分类。

## 标准结构

```
project-kb/
├── README.md
├── code/
│   ├── README.md
│   ├── src/
│   │   └── app.ts.md
│   └── scripts/
│       └── build.py.md
├── decisions/
│   └── 0001-example.md
├── workflows/
│   └── example-flow.md
└── changelog.md
```

## 与三层结构的关系

```
AGENTS.md / CLAUDE.md
└── PROJECT_RULES.md
    └── project-kb/
        ├── code/
        ├── decisions/
        └── workflows/
```

`PROJECT_RULES.md` 应链接到：
- `[[project-kb/README]]`
- `[[project-kb/code/README]]`
- 当前项目最重要的代码说明或流程说明

## code 目录

`code/` 必须按源码相对路径镜像。

| 源码路径 | 文档路径 |
|---|---|
| `src/index.ts` | `project-kb/code/src/index.ts.md` |
| `src/lib/db/client.ts` | `project-kb/code/src/lib/db/client.ts.md` |
| `sandbox-service/src/main.py` | `project-kb/code/sandbox-service/src/main.py.md` |

### 单文件模板

```markdown
# src/example.ts

## 功能点

- 

## 相关文件

- [[project-kb/code/src/related.ts]]：

## 重要逻辑

- 

## 测试文件

- `src/example.test.ts`：

## 修改注意事项

- 

## 最近更新

- YYYY-MM-DD：
```

## decisions 目录

用于记录跨多个文件的重要设计决策。只有当信息无法自然归入单个代码文件时才创建。

模板：

```markdown
# 决策标题

## 背景

## 决策

## 影响文件

- [[project-kb/code/path/to/file.ext]]

## 取舍

## 最近更新

- YYYY-MM-DD：
```

## workflows 目录

用于记录跨文件业务流程、启动流程、数据流、构建流程或测试流程。

模板：

```markdown
# 流程标题

## 流程目标

## 参与文件

- [[project-kb/code/path/to/file.ext]]

## 执行顺序

1. 

## 关键分支

- 

## 相关测试

- 
```

## README 模板

`project-kb/README.md`：

```markdown
# 项目知识库

本知识库用于代码修改前的影响分析、原有功能对比和定向测试选择。

## 入口

- 代码文件说明：[[code/README]]
- 重要设计决策：[[decisions/README]]
- 跨文件流程：[[workflows/README]]

## 维护规则

- 每个代码文件对应 `code/` 下同路径说明文档。
- 相关文件使用 Obsidian 双向链接。
- 修改代码后同步更新对应说明文档。
```

`project-kb/code/README.md`：

```markdown
# 代码文件说明

本目录按源码相对路径镜像项目代码结构。

## 覆盖状态

| 源码路径 | 说明文档 | 状态 |
|---|---|---|
| `src/example.ts` | [[src/example.ts]] | 待完善 |
```

## 初始化策略

不要一次性为空文件创建大量空文档。优先顺序：

1. 当前任务会修改的文件。
2. `PROJECT_RULES.md` 标记的重要文件。
3. 项目入口文件和核心配置。
4. 与当前修改相关的测试文件。

## 命名规则

- 文档文件名保留源码文件完整文件名，并追加 `.md`。
- 例如 `client.ts` 对应 `client.ts.md`，不要写成 `client.md`。
- Obsidian 链接可省略 `.md` 后缀，但路径必须能唯一定位。
