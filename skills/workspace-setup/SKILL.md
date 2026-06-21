---
name: workspace-setup
description: 初始化当前项目的最小研发工作区，创建项目规则、项目级 OKF 知识库，以及真实版本下的需求、方案、任务和验收目录。用于新项目首次建立研发文档结构、为新版本创建空阶段目录或检查既有工作区是否符合 V3 契约；不创建业务文档、不管理同步、技能安装或版本归档。
---

# 工作区初始化

只建立当前项目开展 V3 研发所需的最小结构：

```text
项目根目录/
├── AGENTS.md
├── PROJECT_RULES.md
├── project-kb/
│   ├── index.md
│   ├── log.md
│   └── code/
│       └── index.md
└── workplace/
    └── 3/                 ← 示例，实际使用用户确认的真实版本
        ├── requirements/
        ├── tech-design/
        ├── implementation-planning/
        └── acceptance/
```

执行阶段直接复用 `implementation-planning/` 中的任务入口和 `T-*`，不创建执行目录。调研、证据、UI、原型、审查、日志和缺陷由阶段 Skill 在具体入口旁按需创建，不在初始化时预建。

## 确定项目与版本

项目根目录优先使用用户明确给出的路径；否则使用当前工作区根目录。版本优先使用用户明确给出的数字；未给出时，只有在 `workplace/` 中能够唯一判断当前活跃数字版本时才沿用，否则询问。

版本只接受整数或两段数字，例如 `3`、`3.1`。持久化路径必须直接使用这个真实值。

## 初始化

可直接创建目录和入口，也可运行确定性初始化器：

```text
python skills/workspace-setup/scripts/init_workspace.py --project-root D:\workspace\project --version 3
```

初始化器只执行以下工作：

1. 校验真实项目根目录和数字版本。
2. 创建 `workplace/<实际数字>/` 及四个阶段目录。
3. 只在缺失时创建最小 `AGENTS.md` 和 `PROJECT_RULES.md`；已有文件保持不变。
4. 调用 `personal-kb init-project` 创建最小 OKF bundle。
5. 调用 `personal-kb validate-project` 校验知识库格式和本地链接。
6. 返回新建、保留、警告和错误。

重复执行不得覆盖已有入口、规则、知识库或阶段文档。旧知识库或旧工作区不符合当前契约时只报告问题，不自动移动、删除或迁移。

## 入口边界

`AGENTS.md` 只负责要求 Agent 先读取同级 `PROJECT_RULES.md`。`PROJECT_RULES.md` 只保存修改当前项目前必须知道的规则、真实验证命令和知识库入口，使用标准 Markdown 链接指向 `project-kb/index.md`。

完整领域、架构、代码、决策和工作流知识归 `personal-kb` 管理，不复制进项目规则。研发阶段入口和支撑材料归对应阶段 Skill 管理。

## 检查与完成

完成前检查：

- 版本目录使用确认过的真实数字。
- 版本目录只包含四个预建阶段目录，没有额外执行入口。
- 已有文件内容未被覆盖。
- `PROJECT_RULES.md` 能进入 `project-kb/index.md`。
- personal-kb 初始化和校验均成功。
- 没有生成示例需求、方案、任务、验收或空支撑材料。

只有无法可靠确定项目根目录或真实版本时才提问。问题必须是回复最后的 `## 需要你确认` 区块，一次只问一个并说明推荐处理和影响。

## 边界

- 不维护项目配置文件。
- 不同步本地或远程文件。
- 不搜索、安装或更新 skills。
- 版本创建、归档和删除由用户在独立操作中明确执行。
- 不修改研发阶段状态、用户确认或项目代码。
