---
name: html-prototype-generator
description: 用户要求"生成HTML原型"、"创建可分享原型"、"需求转原型页面"、"复刻已有页面为原型"、"改造原型"、"页面原型"、"/htmlproto"，或需要生成可直接浏览器打开的轻量级 HTML 原型时使用。
---

# HTML Prototype Generator

流程型 skill。生成独立 HTML 文件，风格与 kt-agent-framework 管理后台一致，可直接在浏览器打开分享，无需构建工具。核心原则：LLM 只负责识别页面类型、选择片段、填写 SLOT 数据，不重新生成外壳结构、基础样式或引导层逻辑。

## 触发与边界

**触发**：用户要求生成 HTML 原型、需求转原型、复刻页面、改造原型、创建可分享原型；特别适用于 kt-agent-framework 管理后台风格页面，以及在已有 `.vue` 页面上新增功能的原型。

**不触发**：用户只要 UI 需求 Markdown 文档时，调用 `ui-requirements-doc`，见其 SKILL.md；用户要真实前端实现、后端接口、生产代码重构、视觉稿图片或设计系统规范时不使用本 skill。

**与其他 skill 的关系**：可接收 `ui-requirements-doc` 产出的 Markdown 作为需求输入，但该文档不是完成原型的必需前提；不可用时直接从用户提供的需求或代码生成。

## 存储与路径契约

- 输出目录固定为 `.dev/prototype/`。
- 新原型命名：`prototype-{YYYYMMDD}-{页面名称}.html`。
- 改造版命名：`prototype-{YYYYMMDD}-{页面名称}-v{N}.html`。
- 不覆盖已有文件；同名时递增 `-vN`。
- 多页面批量生成时同时生成或更新 `.dev/prototype/index.html`。
- 详细输出格式见 [docs/output-format.md](docs/output-format.md)。

## 阶段与流转

| 状态 | 含义 | 可进入的下一状态 |
|---|---|---|
| `discussing` | 正在判断模式、读取需求或复刻源文件 | `confirmed` / `blocked` |
| `confirmed` | 页面清单或复刻还原分析已确认 | `in_progress` |
| `in_progress` | 正在生成 HTML、填 SLOT、写文件和检查 | `done` / `not_verified` / `blocked` |
| `done` | HTML 已生成且通过自检 | 无 |
| `not_verified` | HTML 已生成但自检或浏览器验证未完成 | 无 |
| `blocked` | 缺少源文件、需求范围或必要确认 | `discussing` |

流转条件：

- 需求模式 `discussing` -> `confirmed`：页面清单已由用户确认，或需求材料足够明确且低风险。
- 复刻模式 `discussing` -> `confirmed`：已输出 1:1 还原分析表并获得用户确认。
- 对话模式 `discussing` -> `confirmed`：已有原型路径和修改点已明确。
- `in_progress` -> `done`：文件写入成功，自检清单通过，且可直接打开。
- `in_progress` -> `not_verified`：文件已写入，但无法完成浏览器或结构检查。

## 执行步骤

1. 判断模式：用户提到 `.vue` 路径、复刻或在现有页面上改，进入复刻模式；提到需求文档或全新页面，进入需求模式；提到调整已有原型 HTML，进入对话模式。模式细则见 [references/mode-rules.md](references/mode-rules.md)。
2. 读取本 skill 自带资产：`assets/page-skeleton.html`、`assets/base.css`、`assets/guide-layer.js`、`assets/fragments/`；不得改写这些源资产。
3. 识别页面类型并选择片段。`SLOT:main_content` 必须由 `assets/fragments/` 片段组合而成，不得自由生成主内容 HTML 结构；片段与 SLOT 规范见 [references/slot-spec.md](references/slot-spec.md)。
4. 复制 `assets/page-skeleton.html` 作为外壳，只填 SLOT；`assets/base.css` 原样内联到 `<style>` 开头，`assets/guide-layer.js` 原样内联到页面末尾。
5. 填入页面数据、导航、表格、表单、抽屉、确认弹窗、文档面板和 `GUIDE_STEPS`。有改动时每处改动都必须写入 `GUIDE_STEPS`，并给目标元素加页面内唯一 selector；无改动时 `GUIDE_STEPS` 为空数组。
6. 遇到未定义样式时按 [references/style-rules.md](references/style-rules.md) 的优先级处理，不修改 `base.css` 现有 Layer。
7. 写入 `.dev/prototype/`，多页面时生成或更新 `index.html`。
8. 执行自检；可以使用浏览器时打开生成文件检查无控制台错误、关键元素存在、引导 selector 可定位。

## 校验与门槛

判定完成前必须满足：

- [ ] 外壳来自 `assets/page-skeleton.html`，未自行重写侧边栏、顶栏、脚本等外壳结构。
- [ ] `main_content` 来自 `assets/fragments/` 片段组合，未自由生成主内容结构。
- [ ] `assets/base.css` 原样内联在 `<style>` 开头，未修改 Layer 1-5。
- [ ] `assets/guide-layer.js` 原样内联，未修改。
- [ ] 主色使用 `#3e8dff`；无 `#1890ff` 作为主色；无 emoji。
- [ ] 图标使用 `anticon` 类名或首字母色块。
- [ ] 状态标签只使用 `kt-status-success` / `kt-status-danger` / `kt-status-warning` / `kt-status-primary` / `kt-status-default`。
- [ ] 抽屉、确认弹窗、文档面板、引导层全部合并到主 HTML。
- [ ] Mock 数据至少 3 行，字段值符合业务语义。
- [ ] 复刻模式已在阶段一停止等待用户确认；阶段二每处改动已写入 `GUIDE_STEPS`。
- [ ] 文件保存至 `.dev/prototype/` 且未覆盖已有文件；多页面已生成或更新 `index.html`。

## 失败与回退

- 复刻源文件缺失：列出已检查路径，标记 `blocked`，等待用户提供真实路径或文件。
- 复刻分析未确认：不得进入叠加需求改动；停在 `discussing` 并只要求确认还原表。
- 需求页面清单不明确：先输出页面清单并等待确认；不得猜测生成多个业务页面。
- 片段无法覆盖页面结构：按实际顺序组合多个片段；仍无法表达时使用最接近片段并在文档面板记录限制，不修改基础资产。
- 浏览器验证不可用：完成文件写入和静态自检后标记 `not_verified`，说明未验证项。

## 提问契约

复刻模式阶段一必须等待用户确认还原分析；需求模式只有页面清单无法从材料可靠推出时才提问。问题放在 `## 需要你确认` 区块，一次只问当前最关键的确认项。

## 证据与完成定义

最终回复必须列出生成或更新的 HTML 文件路径；若完成了浏览器验证，说明打开的文件和检查结果。若只完成静态检查，明确标记为 `not_verified` 并列出未覆盖的验证项。

## 边界声明

本 skill **不做**：

- 不生成生产前端代码，不调用真实 API。
- 不修改 `assets/page-skeleton.html`、`assets/base.css`、`assets/guide-layer.js` 的源文件。
- 不自由重写主内容结构；主内容必须来自片段组合。
- 不用 emoji、项目色板外的新硬编码颜色或 `#1890ff` 作为主色。
- 不在复刻模式跳过 1:1 还原确认直接叠加改动。
