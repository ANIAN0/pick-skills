# 迁移到统一模板：操作说明

这份文档说明怎么把 `pick-skills` 仓库里已有的 skill 套进新模板，以及为什么这套结构能让"改动影响可预期"。批量迁移存量 skill 时查阅；新建 skill 直接看 [`skills/skill-meta-protocol/SKILL_template.md`](skills/skill-meta-protocol/SKILL_template.md) 即可。

## 整体结构

```text
pick-skills/
├── CHANGE_CHECKLIST.md                                    <- 改动前/中/后自检清单
├── MIGRATION_GUIDE.md                                     <- 本文档
└── skills/
    ├── skill-meta-protocol/
    │   ├── SKILL.md                                       <- 共享元协议正文，定义模块清单、表达规范、命名规则
    │   ├── SKILL_template.md                              <- 可直接复制的脚手架
    │   └── references/
    │       ├── glossary.md                                <- 表达规范详细词汇、正反例
    │       └── optional_modules.md                        <- 按需模块（环境配置契约、质量轨迹）的完整机制
    └── <你的具体 skill>/SKILL.md                           <- 实际内容，按模板的模块分节
```

`skill-meta-protocol` 不参与任何任务执行，只在你新建/重构/审查 skill 时读取。具体 skill 的 SKILL.md 互相之间不读取彼此的内部步骤，只通过"触发与边界"模块里的统一引用格式互相指向。

## 三种形态怎么判断：用本仓库现有 skill 举例

| 现有 skill | 形态 | 判断依据 |
|---|---|---|
| `plan-execution-v3` | 流程型 | 有明确状态机（`pending/executing/confirmed`）、需要用户确认才能流转 |
| `project-development-v3-common` | 流程型的元协议（仓库内自己的元协议，与本次新增的 skill-meta-protocol 是同类角色但管的是研发流程域） | 定义跨阶段共享契约，本身不执行任务 |
| `filebrowser-skill` | 工具型 | 封装 CLI 调用，没有跨会话状态机，失败处理是"排错"而不是"回退状态" |
| `personal-kb` | 知识型 | 核心是一份持续积累的结构化目录，有"写入门槛""校验"但没有用户确认才能流转的阶段 |
| `novel-setup` / `novel-lite` / `novel-review` | 流程型 | "审-改-再审"循环，本质是阶段流转 |

本仓库里已经有 `project-development-v3-common` 承担"研发流程域"的元协议角色，这是对的做法——它和新增的 `skill-meta-protocol` 不冲突，是两层：`skill-meta-protocol` 管"所有 skill 共享的结构和命名"，`project-development-v3-common` 管"研发流程这一组 skill 内部的领域契约"（比如 `F-*/D-*/T-*` 怎么用、入口文档放哪）。后者本质上是遵循 skill-meta-protocol 的一个领域实例。

如果将来小说创作三件套或工具集成那组也发展出跨 skill 共享的领域规则，可以照 `project-development-v3-common` 的样子，各自建一个域内元协议（例如 `novel-suite-common`），同样挂在 `skill-meta-protocol` 之下，不需要把所有领域规则都塞进顶层元协议。

## 三个新概念在仓库里的具体落点

这三个概念是后续补充的，不在最初的九模块里，这里单独说明对应到仓库哪些 skill。

**环境配置契约**：如果某组 skill 里有多个 skill 都要知道"问题追踪用什么系统""哪个目录是入口文档目录"这类项目级设置，而目前是每个 skill 各自硬编码或反复询问用户，可以参考这个模式新建一个一次性的 setup skill（类比 mattpocock 仓库里 `setup-matt-pocock-skills` 的角色），生成一份配置文件，其余 skill 在自己的"环境配置契约"模块里只引用这份配置，不重复定义。如果目前各 skill 之间并不共享这类配置，不需要为了套用这个模块而强行新建，先按"标准模块清单"里"按需"的标注处理：不需要就删除这一节。

**多轮迭代场景下的质量轨迹**：`novel-review` 这类审-改-再审循环，以及如果 v3 套件里存在类似的多轮审查流程，在"校验与门槛"模块里只检查"这一轮是否通过"是不够的——还应该补一个"相比上一轮是否退步"的判据，并定义退步到什么程度要强制加一次检查点。这不需要复杂的打分系统，几个跟该 skill 产出物相关的关键维度，加一个具体的退步阈值即可。具体机制见 skill-meta-protocol 的 [`references/optional_modules.md`](skills/skill-meta-protocol/references/optional_modules.md)。

**多入口场景的路由文档**：如果小说三件套（`novel-setup` / `novel-lite` / `novel-review`）或其他相近 skill 群之间，用户经常拿不准该用哪一个，不要让每个 skill 的"触发与边界"里都写一遍完整对比，应该单独建一份路由文档放在这组 skill 的共同上级目录，集中定义判断标准。具体写作要求见 [`skills/skill-meta-protocol/SKILL.md`](skills/skill-meta-protocol/SKILL.md) 的"多入口场景的路由文档"小节。

## 迁移步骤（以现有 skill 为例）

对仓库里任意一个现有 SKILL.md：

1. 判断形态（流程型/工具型/知识型），按上表的判断依据。
2. 复制 `skills/skill-meta-protocol/SKILL_template.md`，删除不适用的模块标题。
3. 把现有内容的每一段，问一句"这段话回答的是哪个模块该回答的问题"，填进对应模块。
   - 例如 `project-development-v3-common` 里的"入口与支撑契约"对应模板的"存储与路径契约"；"调研契约""审查契约"是该 skill 特有的额外模块（领域元协议可以有自己的额外模块，这是允许的，只要新模块职责单一、不与标准模块重叠）；"状态契约"对应"阶段与流转"；"回退与重新确认契约"对应"失败与回退"；"提问契约"对应"提问契约"；"证据与完成契约"对应"证据与完成定义"。
   - `filebrowser-skill` 里的"执行流程"对应"执行步骤"；"排错"对应"失败与回退"（工具型的失败处理不涉及状态回退，可以保留"排错"这个更贴切的标题，只要职责单一就允许形态特化命名）；"Shell 和路径规则"对应"存储与路径契约"的工具型变体。
4. 检查迁移后是否出现了同一条规则被两个模块同时表达——如果有，合并到职责更匹配的那个模块，另一处改成一句话引用。
5. 用 `CHANGE_CHECKLIST.md` 的"新建 skill 时额外检查"清单过一遍。

## 这套结构如何让改动影响可预期

回到最初的问题："每次改动都很容易出现负面作用"通常来自三个原因，这套模板分别针对性解决：

1. **职责重叠**：同一条规则散落在文件不同位置，改一处忘了改另一处。模板用"模块内容互斥规则"强制每条规则只能出现在一个槽位。
2. **隐藏依赖**：你改了 A skill 的某个细节，没意识到 B skill 内部悄悄依赖了这个细节的具体措辞。模板用"跨 skill 引用规则"强制跨 skill 引用只能引用入口契约，不能引用对方内部实现，这样 A 的内部改动天然不会波及 B。
3. **没有改动影响清单可查**：改完才发现漏了同步的地方。`skill-meta-protocol` 里的"改动影响自检表"和 `CHANGE_CHECKLIST.md` 把"该检查哪里"显式列出来，变成一个可以照着做的清单，而不是依赖记忆。

这三点解决之后，"改一个模块，影响范围可预期"就不再是靠经验判断，而是靠结构本身的约束——这是本协议最初要的效果。

## 推荐的迁移节奏

**不要一次性迁移所有 skill。** 这会导致大规模改动合并、审查成本失控、与"小步快跑"的工程节奏冲突。建议：

1. 优先迁移下次要主动修改的 skill（顺手用本指南对齐结构）。
2. 其次迁移形态清晰的小 skill（如 `personal-kb`、`code-to-requirements`），积累迁移样例。
3. 最后处理大型 skill（`novel-*` 系列、`v3` 研发套件），它们涉及编号语义和阶段机改动，可能还要写存量数据迁移说明。
4. 已迁移的 skill 在 commit message 里加 `[migrated]` 前缀，便于事后回看迁移进展。