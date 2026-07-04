---
name: project-workspace
description: 用户首次建工作区、开启新迭代、关闭旧迭代、审查项目文件结构、维护 PROJECT_RULES.md、或把本地 AGENTS.md/CLAUDE.md 同步到 FileBrowser 时使用。
---

# 项目工作区维护

维护项目工作区的迭代生命周期、工作区结构和项目规则文件。同一时间最多一个活跃版本。

## 触发与边界

使用本 skill 的情况：

- 用户要首次建立工作区、开启新迭代、关闭旧迭代。
- 用户要检查当前项目文件结构是否符合本 skill 的工作区约定，并在确认后调整。
- 用户要创建或维护项目根目录下的 `PROJECT_RULES.md`。
- 用户要把本地 `AGENTS.md` / `CLAUDE.md` 同步到 FileBrowser。

不使用本 skill 的情况：

- 只是在某个研发阶段内写需求、方案、任务、验收或执行代码变更。
- 需要判断业务知识是否应沉淀到 `project-kb/`，该判断交给 `project-knowledge`。

## 存储与路径契约

```text
项目根目录/
├── AGENTS.md            <- 始终从 FileBrowser 拉最新（覆盖本地）
├── CLAUDE.md            <- 始终从 FileBrowser 拉最新（覆盖本地）
├── PROJECT_RULES.md     <- 项目出发点、原则、边界和必要开发信息
└── workplace/
    ├── <进行中版本>/     <- 最多 1 个
    │   ├── requirements/
    │   ├── tech-design/
    │   ├── implementation-planning/
    │   └── acceptance/      <- 验收测试和验收过程产物，归档前清理
    └── archive/         <- 已关闭的迭代，只增不减
        └── <旧版本>/
```

- 项目根目录：用户明确给出 > 当前工作区根目录。
- 版本号：用户必须显式给出；不允许自动推断。
- 版本只接受整数或两段数字，例如 `3`、`3.1`。
- `PROJECT_RULES.md` 只放在项目根目录，不放入 `workplace/` 或 `project-kb/`。

`PROJECT_RULES.md` 的固定结构：

```markdown
# PROJECT_RULES

## 项目的出发点、原则和边界

用于项目启动、某个需求感觉哪里不对、或用户说“我们好像跑偏了”时校准方向。

## 开发必须了解的信息

每次最多增减一条；只记录不看就容易做错当前项目开发的信息。
```

## 阶段与流转

- `pending`：已识别动作，但还缺用户明确输入或确认。
- `in_progress`：正在执行已确认的动作。
- `done`：动作完成且通过本 skill 的校验。
- `not_verified`：文件或目录已变更，但校验条件未满足。
- `blocked`：继续执行会越权、破坏用户文件，或缺少必须由用户提供的确认。

结构调整动作必须先输出调整方案并等待用户确认；只有用户确认后才能从 `pending` 进入 `in_progress`。

## 执行步骤

按用户要求执行以下动作之一。每个动作独立完成，中途失败立即停下并报告。

### A. 开启新迭代（含首次建立）

1. **预检**：`workplace/` 下不存在任何非 archive 子目录则继续；否则停下并告知先调动作 B。

   ```bash
   [ -z "$(find '<root>/workplace' -mindepth 1 -maxdepth 1 -type d ! -name archive 2>/dev/null)" ] || {
     echo "error: an active iteration exists under <root>/workplace; archive it first (action B)" >&2
     exit 1
   }
   ```

2. **建目录**：

   ```bash
   mkdir -p "<root>/workplace/<version>/{requirements,tech-design,implementation-planning,acceptance}"
   ```

3. **拉两份标准文件**（始终覆盖本地）：

   ```text
   filebrowser-cli download /AGENTS.md <root>/AGENTS.md
   filebrowser-cli download /CLAUDE.md <root>/CLAUDE.md
   ```

   远程根固定 `/`，不询问其他路径。下载失败按 filebrowser-skill 排错，不重试。

4. 如果 `<root>/PROJECT_RULES.md` 不存在，按固定结构创建空规则文件；不要替用户编造项目原则或必要信息。
5. 报告完成。

### B. 关闭旧迭代（归档）

按顺序执行“抽 -> 清 -> 移”三步；任何一步失败立即停下并报告。

1. **抽**：调起 `project-knowledge` 的 archive intake 入口；`project-knowledge` 自己决定抽取哪些内容到 `project-kb/`。本 skill 不参与判定。若 `project-knowledge` 不可用，报告该步骤跳过的原因，再继续清和移。

2. **清理过程产物**：删除 `workplace/<version>/` 下所有开发过程产物，只保留需要归档的阶段交付内容。

   必须删除：

   - 测试和验收资产目录与文件：`acceptance/`、`test/`、`tests/`、`fixtures/`、`smoke/`、`e2e/`，以及明显的测试脚本、测试数据、验收脚本和测试报告。
   - 审查材料：`review/`、`reviews/`、`checklists/`，以及审查清单、review notes、review report。
   - 问题清单：`issues/`、`defects/`、`bugs/`、`troubleshooting/`，以及问题列表、缺陷列表、排查记录。
   - 执行记录：`logs/`、`runs/`、`workflow-runs/`、`unattended/`、`execution/`，以及运行日志、执行记录、临时状态文件。
   - 临时文件：文件名匹配 `*.tmp`、`*.bak`、`*.swp`、`*~`，或文件字节数为 0。

   默认保留：

   - `requirements/`
   - `tech-design/`
   - `implementation-planning/`

   如果过程产物混在上述保留目录内，仍按“必须删除”规则删除对应文件；不要删除保留目录本身。文件删除后递归清理变空的子目录（保留 `workplace/<version>/` 顶层目录本身和三个保留目录）。

3. **移**：

   ```bash
   [ -d "<root>/workplace/<version>" ] || { echo "error: iteration <version> not found at <root>/workplace/<version>" >&2; exit 1; }
   [ ! -e "<root>/workplace/archive/<version>" ] || { echo "error: archive/<version> already exists at <root>/workplace/archive/<version>" >&2; exit 1; }
   mkdir -p "<root>/workplace/archive"
   mv "<root>/workplace/<version>" "<root>/workplace/archive/<version>"
   ```

4. 报告完成。

### C. 上传 AGENTS.md / CLAUDE.md 到云端

仅当用户修改了本地副本、想同步到云端时执行：

```text
filebrowser-cli upload <root>/AGENTS.md /AGENTS.md
filebrowser-cli upload <root>/CLAUDE.md /CLAUDE.md
```

### D. 检查并调整项目文件结构

1. 扫描 `<root>` 第一层和 `<root>/workplace` 第一层；需要查看更深层时，只进入已识别的活跃版本目录和 `workplace/archive/` 的直接子目录。
2. 按“校验与门槛”的结构规则判断违规项。不要把普通源码目录、配置文件、文档目录判为违规；本动作只审查本 skill 管辖的工作区结构。
3. 给出调整方案，至少包含：
   - 发现的违规项。
   - 每项拟执行的文件操作。
   - 不会触碰的目录或文件。
   - 调整后的目标结构。
4. 等待用户确认。用户未确认前不得移动、删除、创建或覆盖任何文件。
5. 用户确认后执行调整方案；执行中发现计划外路径或会影响未列出的文件时停止并重新请求确认。
6. 执行后重新扫描同一范围，报告仍存在的违规项或确认已通过。

### E. 创建和维护 PROJECT_RULES.md

1. 如果 `<root>/PROJECT_RULES.md` 不存在，按固定结构创建。
2. 如果文件存在但缺少固定结构中的任一二级标题，只补齐缺失标题；保留已有内容。
3. 维护“项目的出发点、原则和边界”时，只写项目级方向约束，不写一次性任务、实现步骤或临时偏好。
4. 维护“开发必须了解的信息”时，只写不看就容易做错当前项目开发的信息，不写通用工程常识。
5. 每次最多增减一条规则或一条必要信息。用户一次提出多条时，先执行最关键的一条，并把其余列为待确认项。
6. 删除或改写既有条目前，必须说明目标条目和理由，并取得用户确认。

## 校验与门槛

开启新迭代完成前必须满足：

- `workplace/<version>/requirements/`、`tech-design/`、`implementation-planning/`、`acceptance/` 均存在。
- `workplace/` 下最多只有一个非 `archive` 子目录。
- `AGENTS.md` 和 `CLAUDE.md` 已成功从 FileBrowser 下载，或明确报告下载失败且动作未标记为 `done`。

关闭旧迭代完成前必须满足：

- `workplace/archive/<version>/` 存在，且 `workplace/<version>/` 不再存在。
- 归档目录内不包含 `acceptance/`、`test/`、`tests/`、`fixtures/`、`smoke/`、`e2e/`、`review/`、`reviews/`、`checklists/`、`issues/`、`defects/`、`bugs/`、`troubleshooting/`、`logs/`、`runs/`、`workflow-runs/`、`unattended/`、`execution/` 这些过程产物目录。
- 归档目录内不包含 `*.tmp`、`*.bak`、`*.swp`、`*~` 或 0 字节文件。

结构检查的违规项只包括：

- `workplace/` 下存在超过一个非 `archive` 子目录。
- 活跃版本目录缺少 `requirements/`、`tech-design/`、`implementation-planning/`、`acceptance/` 中任一目录。
- `workplace/archive/` 下的旧迭代与活跃版本同名。
- `PROJECT_RULES.md` 缺失或不在项目根目录。
- `PROJECT_RULES.md` 缺少固定结构中的任一二级标题。
- `AGENTS.md` 或 `CLAUDE.md` 缺失。

`PROJECT_RULES.md` 维护完成前必须满足：

- 文件位于项目根目录。
- 固定结构中的两个二级标题存在。
- 本次变更最多新增、删除或改写一条条目。
- 新增条目不包含占位符、泛泛的通用工程常识或临时任务说明。

涉及审查-修订多轮循环时，后一轮方案不得比前一轮扩大未确认的文件操作范围；如果扩大，必须重新进入用户确认。

## 失败与回退

- 任一命令失败：立刻停下，告知用户哪一步失败、哪些已完成、哪些未完成。
- 不重试、不回滚、不清除部分完成的状态。
- 结构调整执行中遇到计划外文件影响，停止在 `blocked`，报告新增风险并等待用户确认。
- `PROJECT_RULES.md` 已存在但内容无法可靠归类时，不重排全文；只报告需要用户确认的具体条目。

## 边界声明

本 skill 不做：

- 不预建执行目录、任务、需求、方案、验收、调研、证据、UI、原型、审查、日志、缺陷文件。
- 不校验既有 `AGENTS.md` / `CLAUDE.md` 内容。
- 不替用户决定抽取哪些内容到 `project-kb/`，由 `project-knowledge` 在 archive intake 时自行判定。
- 不删除 `workplace/archive/` 下的旧迭代。
- 不凭空创建未指定版本，不删除版本；新建版本仅限动作 A，归档仅限移动到 `workplace/archive/`。
- 不修改研发阶段状态、用户确认、项目代码。
- 不把普通源码目录、构建配置、依赖目录或产品文档目录纳入违规结构判断。
