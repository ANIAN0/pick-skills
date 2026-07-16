---
name: project-knowledge
description: 以 OKF 稳定格式增量建设、查询、维护和审计本地知识库：设计结构，建立完整文件清单与持久化摄入队列，逐来源分析、写入和验证，并把对话中发现的问题、决定或经验固化为可追溯来源。用户提到 OKF/project-kb、个人知识库、项目 Wiki、产品/需求 Wiki、知识遗漏或错误、记录当前对话发现、文档摄入、队列处理、项目背景检索、经验归档，或基于历史需求生成上下文与候选草稿时使用；不处理正式需求确认、远程发布或跨库同步。
---

# 增量 OKF 知识库

知识库是持续生长的编译产物，不是一次对话生成的文档集合。建设类任务必须产出 OKF 规范层；每个来源只有在独立完成“分析 → 写入 → 验证”后才算进入知识库。

## 触发与边界

用于本地知识库的设计、初始化、摄入、查询、维护、迁移和审计。按读者任务只读取 [个人](references/personal-profile.md)、[项目](references/project-wiki-profile.md) 或 [产品](references/product-wiki-profile.md) 中选中的 profile。

单份材料的一次性总结不触发。知识库需求对象是既有材料的投影，不修改库外研发流程。

## 存储与路径契约

- 每个建设任务确定唯一 `<okf-root>`；项目库默认 `<项目根>/project-kb/`。
- `<okf-root>` 遵循 [OKF 知识契约](references/knowledge-contract.md)。已有 Wiki 是导入来源或 `<publish-root>` 视图，不能取代规范层。
- `_meta/state.json` 保存阶段与设计门槛；`_meta/coverage.json` 保存完整来源清单；`_meta/capture-registry.json` 锁定 Capture 身份与原始指纹；`_meta/ingest-queue.json` 保存可恢复队列；`_meta/ingest/*.json` 保存逐来源分析产物。
- 对话发现按 [对话 Capture 协议](references/conversation-capture.md) 保存到 OKF 根外的来源目录，再进入同一 coverage/queue。

## 阶段与流转

每次执行只完成当前阶段并停止；后续阶段由下一次“继续”进入。查询不改变阶段。
Capture 可在任一阶段发生，只新增来源和待办，不推进当前阶段，也不直接修改正文。

1. **design**：填写 `_meta/state.json` 的读者、3–7 个问题、边界、来源优先级和 operational 条件，并完成 purpose/schema/维护契约。不得顺带生成业务正文。
2. **inventory**：结构已确定但 coverage/queue 尚未与当前来源根同步。完成后所有发现项进入队列，知识状态为 `growing`。
3. **ingest**：队列存在。默认只处理一个 `pending` 来源事务；成功后处理下一文件仍是新的执行，不连续批量铺页。
4. **milestone**：声明某个问题范围可用或准备发布时，对该范围做综合、真实检索和 fresh-context review，再由工具绑定来源指纹并验证；通过后仅该范围为 `operational`。

## 执行步骤

1. **定位状态**：读取 `purpose.md`、schema、coverage 和队列；选择唯一当前阶段。缺少前一阶段产物时回到前一阶段。
2. **捕获对话发现**：用户要求记录问题、决定或经验时，先创建不可变 Capture；报告只证明“有人这样陈述”，用户决定只在声明 scope 内具规范权威。捕获后停止，不顺带摄入或改正文。
3. **设计结构**：读取 [OKF 知识契约](references/knowledge-contract.md) 与选中 profile，确定读者、3–7 个问题、类型、身份、关系、来源优先级、队列优先级和 operational 条件；只写控制面。
4. **建立清单**：按 [覆盖与里程碑审查](references/coverage-and-review.md) 从真实来源根生成 inventory，再同步 ingest queue。目录、读取失败、内容指纹和每个文件都进入确定性记录。
5. **摄入一个来源**：按 [单来源摄入事务](references/ingestion-queue.md) 和 [本地工具](references/tooling.md) claim 队首文件；先生成分析 artifact，再合并 OKF 页面，运行来源级校验，最后提交指纹。真实软件来源按 [项目理解契约](references/project-understanding.md) 补足其调用/数据上下文。
6. **查询或投影视图**：只把 `done` 且具事实资格的来源结论作为事实；`reported` 只支持“曾被报告”，`normative` 只支持声明 scope 内的用户决定。披露 pending/blocked/review 缺口；发布视图只投影 operational 范围。
7. **验收里程碑**：按 [语义与检索验收](references/quality-criteria.md) 测试声明范围，再运行全量/范围审查；未通过就产生队列或 review backlog 项，不批量补模板页。

## 校验与门槛

- design 完成只证明结构可执行；inventory 完成只证明文件未漏；两者都不能宣称知识可用。
- 每个来源的 SHA-256、analysis artifact、coverage disposition、claims、目标反向来源和来源级 validator 必须一致，成功后才能标 `done`。
- Capture claim 必须保留 `reported` 或 `normative` 真值类型；工具用 registry 拒绝修改后脱离 Capture 边界，且任何原始 Capture 都不能直接绑定到 operational milestone。
- `pending` 在 growing 阶段是正常进度；`blocked`、`not_verified` 和 blocker review item 不能进入事实回答或 operational 范围。
- 现有页面合并时保留其他来源贡献；工具在写入前保存 coverage 与目标页快照，共享写入串行执行，失败事务由工具恢复快照后才重新排队。

## 失败与回退

- 分析失败可直接回到 `pending`；写入或验证阶段中断先标 `blocked`，检查并回滚受影响页面后再重置。
- 来源变化使旧分析和提交指纹失效，任务回到 `pending`。删除来源进入 cleanup 事务，不直接删除多来源页面。
- 冲突进入 review backlog；无法裁决时页面保持 `draft`，来源为 `not_verified`。

## 证据与完成定义

design 交付 state/purpose/schema/维护契约；inventory 交付目录统计、coverage 和队列统计；单来源 ingest 交付来源、分析 artifact、页面 diff、来源级校验和队列状态；milestone 交付绑定来源指纹的声明范围、真实检索、未覆盖来源与独立 review。不得把 `design` 或 `growing` 表述为“知识库搭建完成”。

## 边界声明

不修改正式路线图或需求确认状态，不执行远程部署/同步，不按目录生成一页一文件的纸盒子结构，不把内部证据或秘密投影到公开层。
