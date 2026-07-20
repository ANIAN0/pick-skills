---
name: project-knowledge
description: 以 OKF 规范层持续建设、查询、维护和审计可追溯的本地知识库。当用户要求初始化或维护 project-kb、项目 Wiki、产品或需求知识库、个人知识库，摄入或刷新来源，查询项目历史与经验，记录对话中的问题或决定，处理知识冲突、遗漏、过期、迁移和完整性审计，或者声明某个知识范围可用时使用；通过来源清单、持久化队列、单来源事务、指纹、验证和里程碑保证长期一致性。
---

# 可持续 OKF 知识库

把分散来源持续转换成可追溯、可更新、可验证、可查询的长期知识，并在来源增加、变化或删除时保持知识库一致。知识库是由来源编译出的规范层，不是一次对话生成的文档集合。

## 核心约束

- 每个知识库确定唯一 `<okf-root>`；项目库默认位于 `<项目根>/project-kb/`。
- 始终遵循 [OKF 知识契约](references/knowledge-contract.md)。控制文件使用契约规定的稳定英文路径，不因中文命名偏好改名；面向人的概念页可在身份稳定、链接可维护时使用清楚的中文名称。
- 现有 Wiki、PRD、项目文档和源码是来源或发布视图，不能替代 OKF 规范层。一个稳定概念只能有一个规范身份和当前入口。
- 使用脚本维护来源清单、队列、指纹、Capture registry、快照和状态流转，不手工伪造 `done`、修改已提交指纹或绕过 validator。
- 默认一次处理一个 primary source。用户明确要求连续处理时，只执行约定的有限批次；每个来源仍是独立事务，任一事务失败立即停止，不能开启无边界摄入循环。
- 不要求每个来源生成页面。没有长期贡献的来源可以有证据地标记为重复、被替代、忽略或其他适用 disposition，但必须仍在 coverage 中得到解释。

## 选择知识库类型

只读取当前任务需要的 profile：

- 建设项目说明、开发和运维知识时读取 [项目 Wiki profile](references/project-wiki-profile.md)。
- 整理产品能力、需求演进、迭代和决策时读取 [产品 Wiki profile](references/product-wiki-profile.md)。
- 汇总跨项目经验、参考项目和长期主题时读取 [个人知识库 profile](references/personal-profile.md)。

不同 profile 共用同一套 OKF、coverage、queue、事务和验证契约，不把某个 profile 的类型和完成条件强加给其他知识库。

## 生命周期

### 1. 设计

初始化或重构知识库前，确定主要读者、需要回答的 3–7 个关键问题、来源和知识边界、权威范围、优先级、schema、维护方式以及何时可以声明某个范围可用。只建立控制面，不根据目录批量生成正文。

设计完成只表示结构可以执行，不表示已经拥有可用知识。

### 2. 建立来源清单

按 [覆盖与里程碑审查](references/coverage-and-review.md) 扫描真实来源根，生成完整 inventory 和 `coverage.json`，然后同步持久化摄入队列。记录每个发现项、读取失败、排除理由、内容指纹、权威范围和当前 disposition，使 coverage 始终能够说明全部来源的去向。

Inventory 完成只表示来源分母明确；`pending` 是正常生长进度，不能据此声称知识库已经完成。

### 3. 摄入来源

按 [单来源摄入事务](references/ingestion-queue.md) 和 [本地工具](references/tooling.md) 执行 `sync → next → claim → record-analysis → record-write → finish`。一个事务只有一个 primary source，可以读取依赖和现有知识帮助理解，但不能顺便把依赖标为已处理。

先读取完整来源并固定 analysis artifact，把每条 claim 绑定到精确 evidence 和目标页；确认对象身份、冲突和完整 write set 后再写正文。合并现有页面时保留其他来源贡献，同步必要的来源反链、强关系、索引和日志。

写入前由工具保存 coverage 和完整 write set 快照，写入后运行来源级 validator。指纹、artifact、claims、目标正文、反向来源、对象身份和受影响链接一致后才能 `finish`。存在 blocker review item 时保持 `not_verified`，不能降级成 warning 或静默裁决。

分析阶段失败可以安全返回 `pending`；写入或验证阶段失败必须根据工具状态进入 `blocked`，只有存在有效快照时才能由工具回滚。不要人工宣称页面已经恢复。

真实软件来源按 [软件项目理解](references/project-understanding.md) 沿调用、事件和数据链补足上下文。跨文件才能成立的架构、业务旅程和机制结论进入 synthesis 或 review 工作项，不由单个文件直接定稿。

### 4. 捕获对话发现

用户要求记录问题、决定、观察或经验时，按 [对话 Capture 协议](references/conversation-capture.md) 创建不可变原始来源，并通过工具登记身份、scope 和 SHA-256。知识库已经进入 growing 阶段时，可以在同一次调用中完成 Capture 创建和队列同步，但不能把 Capture 直接写成已验证事实。

`reported` 只证明某项内容曾被报告；`normative` 只证明有权用户在声明 scope 内作出了决定。二者都不能证明当前系统已经如此实现，也不能直接进入 operational milestone。修正、解决和补充使用新的来源关联原 Capture，不覆盖历史陈述。

### 5. 查询

查询不改变建设阶段。优先使用工具定位相关规范页，再回查来源任务、claim 资格和当前指纹。只有 `done` 且具备事实资格的来源可以支撑项目事实；历史、计划、用户决定、报告、推断、冲突和未知必须分别表达。

答案应披露与问题直接相关的 `pending`、`not_verified`、`blocked`、Review Backlog 和失效里程碑。局部事实已经验证时可以回答局部事实，但不能用局部完成暗示整个知识库已经完整。

### 6. 验收可用范围

只有需要声明某个问题范围可用、准备投影视图或发布知识库时，才创建 operational milestone。按 [语义与检索验收](references/quality-criteria.md) 使用 3–5 个不包含文件名提示的真实问题验证精确事实、跨页关系、历史或冲突，以及应当返回知识缺口的情况。

Milestone 绑定范围内来源及其 SHA-256、相关对象、检索证据和独立 fresh-context review。Reviewer 不读取建设者自评，应从原始来源、文件系统和真实检索重新核对。只有范围内来源、检索和审查都通过时才能声明该范围 operational；任一绑定来源变化后，里程碑自动失效并重新验证。

## 持续维护

- 来源新增或指纹变化时重新进入 queue，旧 analysis 和基于旧指纹的里程碑失效。
- 来源删除或移动时创建 cleanup 事务，先判断它对多来源页面的贡献，不直接删除共享概念页。
- 来源冲突、稳定身份冲突和缺少权威证据时进入 Review Backlog；无法裁决的页面保持 `draft`。
- 共享页面串行写入。并发任务不得绕过 queue 直接修改同一控制面或概念页。
- 定期根据 `review_after`、失效来源、未解决 blocker、链接和真实检索结果维护知识，而不是按目录批量补模板页。
- 内部证据、秘密和敏感来源不能自动投影到公开 Wiki；发布视图只使用已通过的 operational 范围。

## 输出

每次操作只向用户简洁报告：当前生命周期位置、本次处理的来源或查询、修改的规范页、验证或回滚结果、队列中的 `done/pending/not_verified/blocked` 数量、关键缺口和下一步。详细状态保存在 OKF 控制面，不在对话中重复完整 JSON 或生成额外流程报告。

## 边界

- `project-research` 的调研结果只有在被明确选为长期来源后才进入摄入流程，不自动沉淀。
- 不修改库外的需求、方案、任务、Roadmap、项目规则、代码状态或验收结论。
- 不执行远程发布、跨库同步或生产部署。
- 不把 design、inventory、growing、Capture 创建或单个来源完成表述成“知识库已经完成”。
