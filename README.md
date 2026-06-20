# pick-skills

挑选一些比较好的 skill，自用。

## 研发流程

### v3 图谱化研发套件

- [unattended-development-v3](./skills/unattended-development-v3/SKILL.md) — full/extension/task/bug 统一入口、四个人工确认闸门和可恢复运行记录
- [requirements-workshop-v3](./skills/requirements-workshop-v3/SKILL.md) — 自适应 Story/Module/Feature 需求文档
- [tech-design-v3](./skills/tech-design-v3/SKILL.md) — 按需求范围生成技术设计
- [implementation-planning-v3](./skills/implementation-planning-v3/SKILL.md) — 生成同范围任务清单并校验依赖 DAG
- [plan-execution-v3](./skills/plan-execution-v3/SKILL.md) — 按依赖、运行时资历、执行断言和正负验证执行任务
- [project-verification-v3](./skills/project-verification-v3/SKILL.md) — 生成 Test Plan、聚合正负验证并独立请求 G-ACCEPT
- [project-development-review-v3](./skills/project-development-review-v3/SKILL.md) — 局部影响评审及证据化关闭
- [project-research-v3](./skills/project-research-v3/SKILL.md) — 项目调研与全局知识复用
- [project-development-v3-common](./skills/project-development-v3-common/SKILL.md) — 图、确认、影响、证据和派生视图公共协议

阶段生成动作不会代替用户确认。先生成决策包，再由独立确认动作记录 `G-REQ/G-DESIGN/G-PLAN/G-ACCEPT`；修改已有文档必须使用显式 revision 更新，生成器不会静默覆盖。

### 旧版线性流程

- [requirements-workshop](./skills/requirements-workshop/SKILL.md) — 交互式讨论需求，产出需求文档
- [code-to-requirements](./skills/code-to-requirements/SKILL.md) — 从代码反向生成需求文档
- [tech-design](./skills/tech-design/SKILL.md) — 基于需求产出技术方案
- [implementation-planning](./skills/implementation-planning/SKILL.md) — 把技术方案拆成任务清单
- [plan-execution](./skills/plan-execution/SKILL.md) — 按任务清单逐项执行
- [test-suite-maintainer](./skills/test-suite-maintainer/SKILL.md) — 维护并执行全量测试用例
- [project-doc-sync](./skills/project-doc-sync/SKILL.md) — 代码变更后同步项目文档
- [version-doc-updater](./skills/version-doc-updater/SKILL.md) — 迭代后生成面向非技术人员的版本说明

## 小说创作（三件套闭环）

- [novel-setup](./skills/novel-setup/SKILL.md) — 项目冷启动、大纲、主角档案、故事状态、伏笔追踪
- [novel-lite](./skills/novel-lite/SKILL.md) — 单章创作：摘要/正文/实体三件套、多版本探索、定稿
- [novel-review](./skills/novel-review/SKILL.md) — 七维度章节审查，驱动"审-改-再审"循环

## 内容与知识

- [share-creator](./skills/share-creator/SKILL.md) — 技术分享、项目汇报、培训演示
- [personal-kb](./skills/personal-kb/SKILL.md) — Obsidian 个人知识库管理

## 原型设计

- [prototype-generator](./skills/prototype-generator/SKILL.md) — 通用 UI 页面原型生成
- [vue-prototype-generator](./skills/vue-prototype-generator/SKILL.md) — Vue + Ant Design Vue 原型生成

## 工具集成

- [memos-skill](./skills/memos-skill/SKILL.md) — Memos 备忘录系统
- [filebrowser-skill](./skills/filebrowser-skill/SKILL.md) — FileBrowser 文件管理与分享
- [chrome-devtools](./skills/chrome-devtools/SKILL.md) — Chrome DevTools 调试与自动化
- [specstory-sync](./skills/specstory-sync/SKILL.md) — Claude Code 对话历史自动记录

## 基础设施

- [workspace-setup](./skills/workspace-setup/SKILL.md) — 工作区初始化、版本管理、配置同步、skill 管理
