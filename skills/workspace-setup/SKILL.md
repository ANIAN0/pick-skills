---
name: workspace-setup
description: 用户首次建工作区、开启新迭代、关闭旧迭代、或把本地 AGENTS.md/CLAUDE.md 同步到 FileBrowser 时使用。
---

# 工作区维护

维护项目工作区的迭代生命周期。同一时间最多一个活跃版本。

```text
项目根目录/
├── AGENTS.md            ← 始终从 FileBrowser 拉最新（覆盖本地）
├── CLAUDE.md            ← 始终从 FileBrowser 拉最新（覆盖本地）
└── workplace/
    ├── <进行中版本>/     ← 最多 1 个
    │   ├── requirements/
    │   ├── tech-design/
    │   ├── implementation-planning/
    │   └── acceptance/
    └── archive/         ← 已关闭的迭代，只增不减
        └── <旧版本>/
```

## 确定项目与版本

- 项目根目录：用户明确给出 > 当前工作区根目录。
- 版本号：用户必须显式给出；不允许自动推断。
- 版本只接受整数或两段数字，例如 `3`、`3.1`。

## 维护动作

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

4. 报告完成。

### B. 关闭旧迭代（归档）

按顺序执行「抽 → 扫 → 移」三步；任何一步失败立即停下并报告。

1. **抽**：调起负责维护 `project-kb/` 的 skill 的 archive intake 入口；该 skill 自己决定抽取哪些内容到 `project-kb/`。本 skill 不参与判定。

2. **扫垃圾**：删除 `workplace/<version>/` 下匹配以下任一条件的文件：
   - 文件名匹配 `*.tmp`、`*.bak`、`*.swp`、`*~`
   - 文件字节数为 0

   文件删除后递归清理变空的子目录（保留 `workplace/<version>/` 顶层目录本身）。

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

## 失败处理

- 任一命令失败：立刻停下，告知用户哪一步失败、哪些已完成、哪些未完成。
- 不重试、不回滚、不清除部分完成的状态。

## 边界

不做的：

- 不创建 `PROJECT_RULES.md`——需要时由调用方按其规则创建。
- 不初始化 personal-kb——需要时由调用方按其规则调用。
- 不预建执行目录、任务、需求、方案、验收、调研、证据、UI、原型、审查、日志、缺陷文件。
- 不校验既有 AGENTS.md / CLAUDE.md 内容。
- 不替用户决定抽取哪些内容到 `project-kb/`——由负责该目录的 skill 在 archive intake 时自行判定。
- 不维护项目配置文件。
- 不删除 `workplace/archive/` 下的旧迭代。
- 不创建 / 删除版本（仅移动到 `workplace/archive/`）。
- 不修改研发阶段状态、用户确认、项目代码。