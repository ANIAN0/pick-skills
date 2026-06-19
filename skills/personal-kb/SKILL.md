---
name: personal-kb
description: 项目与个人知识库管理 skill。用于维护项目内按代码路径镜像的 code 知识库，以及由多个项目复用的全局 research Knowledge Report。当用户提到知识库、project-kb、代码文件说明、功能点、测试覆盖、技术调研、研究报告、来源追踪、报告过期或全局知识复用时触发。
---

# 项目知识库管理 Skill

本 skill 提供两种明确模式。先按用户目标路由，不要混合存储边界：

- `code`：维护项目内 `project-kb/` 的代码镜像说明，服务于影响分析和定向测试。
- `research`：维护 `knowledge.global_dir` 下的全局 Knowledge Report，服务于跨项目调研复用和来源追踪。

研究模式读取 [research-kb.md](references/research-kb.md)，并从 `assets/research-report.md` 创建报告。代码模式继续使用下文及现有 references，保持原行为。

`scripts/kb_cli.py` 是 `workspace-setup` 与本 Skill 的确定性接口：使用 `init-project` 初始化项目知识库，使用 `check-global` 检查全局知识库边界。`workspace-setup` 不得复制本 Skill 的模板或自行实现知识库初始化。

## Research 模式硬规则

- 将完整报告只存入全局知识库，不复制进项目 `graph/nodes/`。
- 使用稳定报告 ID；项目仅保存 Research Task、决策摘要和 `uses-knowledge` 正向关系。
- 来源不足、`review_after` 已过期或 `knowledge.global_dir` 不可访问时保持 blocked/stale，不把搜索摘要包装成结论。
- 更新被项目引用的报告时保留变化摘要、`updated_at` 与旧结论历史，不静默替换。

## 与三层结构的关系

```
第 1 层：AGENTS.md / CLAUDE.md
  ↓ 固定要求读取
第 2 层：PROJECT_RULES.md
  ↓ 链接并约束
第 3 层：project-kb/
```

`PROJECT_RULES.md` 记录当前项目必须知道的规则和重要文件；`project-kb/` 记录可持续积累的项目知识。修改代码前，必须阅读目标代码文件对应的知识库条目。

## 默认目录结构

```
project-kb/
├── README.md              ← 知识库入口
├── code/                  ← 按源码相对路径镜像的代码文件说明
│   ├── README.md
│   └── path/to/file.ext.md
├── decisions/             ← 重要设计决策，可选
├── workflows/             ← 跨文件流程说明，可选
└── changelog.md           ← 知识库操作日志
```

初始只创建确定需要的目录。`code/` 是必需目录，其他目录按需创建。

## 核心原则

### 1. 代码结构镜像

每个代码文件对应一份说明文档，路径放在 `project-kb/code/` 下并保留源码相对路径。

示例：

| 源码文件 | 知识库条目 |
|---|---|
| `src/app/page.tsx` | `project-kb/code/src/app/page.tsx.md` |
| `lib/db/client.ts` | `project-kb/code/lib/db/client.ts.md` |
| `scripts/build.py` | `project-kb/code/scripts/build.py.md` |

目录级概览使用该目录下的 `README.md`，例如 `project-kb/code/src/README.md`。

### 2. 为修改服务

单文件说明不是普通 API 文档，而是回答：
- 这个代码文件有哪些功能点？
- 修改它会影响哪些文件？
- 哪些逻辑容易被破坏？
- 应该运行哪些测试验证？

### 3. 使用 Obsidian 双向链接

相关文件必须使用 wiki link：

```markdown
- [[project-kb/code/lib/db/client.ts]]
- [[project-kb/code/app/api/chat/route.ts]]
```

当 A 文档链接 B 文档时，应在 B 文档中补充反向关联，除非该关联只是临时阅读线索。

### 4. 与项目规则分工

`PROJECT_RULES.md` 放“所有修改前必须知道的项目规则和重要文件入口”。

`project-kb/` 放“按文件和流程展开的详细知识”。

如果某条知识只对单个代码文件有意义，放入对应代码说明；如果跨多个文件但不是强规则，放入 `workflows/` 或 `decisions/`。

## 初始化流程

首次使用时：

1. 确认项目根目录存在 `PROJECT_RULES.md`；没有则提醒先运行 `workspace-setup` 或创建该文件。
2. 创建 `project-kb/README.md`。
3. 创建 `project-kb/code/README.md`。
4. 扫描项目代码文件，优先为核心文件创建说明文档。
5. 在 `PROJECT_RULES.md` 中确认已链接知识库入口。

### 代码文件识别

默认纳入：
- 源码：`.ts`、`.tsx`、`.js`、`.jsx`、`.py`、`.go`、`.rs`、`.java`、`.kt`、`.cs`、`.php`、`.rb`
- 配置：`package.json`、`tsconfig.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`Dockerfile`、`docker-compose.yml`
- 脚本：`scripts/`、`bin/`、`tools/` 下的可执行或构建脚本
- 测试：测试文件本身也可以有说明，但主要应被业务代码条目引用

默认排除：
- `.git/`
- `node_modules/`
- `.venv/`、`venv/`
- `dist/`、`build/`、`coverage/`
- 缓存、产物、日志和锁文件，除非项目规则明确要求说明

## 单文件说明模板

```markdown
# 源码相对路径

## 功能点

- 说明该文件对外承担的功能。
- 拆分到可验证的功能点，不只描述技术实现。

## 相关文件

- [[project-kb/code/path/to/related.ext]]：说明关联原因。

## 重要逻辑

- 说明容易被修改破坏的业务规则、状态流转、边界条件、兼容约束。
- 记录“为什么这样做”，不要只复述代码。

## 测试文件

- `tests/...`：覆盖哪些功能点。
- `src/.../*.test.ts`：覆盖哪些边界。

## 修改注意事项

- 修改前需要检查的配置、迁移、兼容性或数据影响。
- 修改后建议运行的定向命令。

## 最近更新

- YYYY-MM-DD：记录本条目因什么代码变更而更新。
```

## 更新流程

当用户要求更新知识库，或代码修改影响已有文件时：

1. 读取 `PROJECT_RULES.md`，确认项目规则和知识库入口。
2. 定位被修改或将被修改的代码文件。
3. 找到对应 `project-kb/code/...ext.md`；不存在则创建。
4. 对比代码当前状态，更新功能点、相关文件、重要逻辑和测试文件。
5. 如果相关文件缺少反向链接，补齐。
6. 在 `project-kb/changelog.md` 追加操作记录。
7. 如发现“所有修改前都必须知道”的新规则，更新 `PROJECT_RULES.md`。

## 查询流程

当用户询问项目代码或影响范围：

1. 先查 `PROJECT_RULES.md`。
2. 再查 `project-kb/code/` 中对应文件说明。
3. 沿 `相关文件` 双向链接查找影响面。
4. 综合测试文件字段给出建议验证命令。
5. 如果知识库缺失或过时，明确指出并建议补充。

## 健康检查

检查维度：

| 维度 | 检查内容 |
|---|---|
| 覆盖率 | 核心代码文件是否有对应说明 |
| 路径一致 | 知识库路径是否与源码相对路径一致 |
| 双向链接 | 相关文件是否存在双向链接 |
| 测试映射 | 代码文件是否列出相关测试 |
| 逻辑完整 | 是否记录重要业务规则和边界条件 |
| 过时条目 | 文档描述是否与代码现状不一致 |
| 孤立条目 | 是否存在没有入口或关联的说明 |

发现问题后，优先修复会影响当前修改判断的条目。

## 操作日志

每次批量更新在 `project-kb/changelog.md` 追加：

```markdown
## YYYY-MM-DD | 操作类型 | 简述

- 触发：用户请求 / 代码变更 / 健康检查
- 变更：创建或更新了哪些条目
- 影响：覆盖了哪些代码文件和测试映射
- 待跟进：仍缺失或需要人工确认的信息
```

## 使用参考

- `references/project-templates.md`：三层结构和代码镜像知识库模板。
- `references/quality-criteria.md`：代码说明条目的质量评估标准。
