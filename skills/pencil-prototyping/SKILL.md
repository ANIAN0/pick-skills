---
name: pencil-prototyping
description: 使用 Pencil 创建产品原型与需求文档中的界面草图。在以下情况使用：用户要求画产品原型、线框图、界面草图；需求文档需要配图（页面结构、流程、关键界面）；需要创建或编辑 .pen 文件；讨论设计到代码一致性（Design-to-Code）。若已配置 Pencil MCP（user-pencil），优先调用其工具进行创建或编辑。
---

# Pencil 产品原型与需求文档

在 Cursor/IDE 中使用 Pencil 绘制产品原型并配合需求文档。Pencil 为集成在 IDE 中的矢量设计工具，使用 `.pen` 文件（JSON、可版本控制），适合与代码同仓维护。

## 工作流程

### 1. 创建或打开原型文件

- 在项目内新建 `.pen` 文件，例如：`docs/prototype/wireframe.pen` 或 `docs/requirements/screens.pen`
- 命名建议：`[模块或页面]-[类型].pen`（如 `dashboard.pen`、`auth-flow.pen`）

### 2. 绘制产品原型

- **页面/屏幕**：每个主要界面一页或一组组件，便于在需求文档中引用
- **关键元素**：标出导航、主要区块、关键按钮与表单，便于写需求说明
- **流程**：多页时用链接或标注说明跳转关系（如登录→首页→详情）

### 3. 与需求文档配合

- 在需求文档（Markdown 等）中引用原型：说明「见 `docs/prototype/xxx.pen` 中某页/某组件」，或导出为图片后嵌入：`![登录页](../prototype/exports/login.png)`
- 需求文档应包含：功能说明、交互说明、与原型页/组件的对应关系

### 4. 保存与版本控制

- `.pen` 为 JSON，适合 Git。提醒用户经常保存（当前无自动保存）
- 建议将 `.pen` 放在与文档、代码同一仓库内，便于评审与追溯

## 输出与协作

- **仅讨论不落盘**：给出页面列表、线框描述、建议的 `.pen` 文件名与目录结构
- **需要产出文件**：在项目内创建或修改 `.pen` 文件，并在需求文档中写明引用路径与说明
- **导出图**：若需嵌入文档，说明在 Pencil 中导出为 PNG/SVG 等并放到指定路径

## 程序化读写 .pen

不要臆造 `.pen` 的 JSON 结构。需程序化读写时，查阅 [references/pen-format.md](references/pen-format.md) 或 [Pencil 开发者文档](https://docs.pencil.dev/for-developers/the-pen-format)。

## 约定

- 若已配置 Pencil MCP（user-pencil），优先调用其工具创建或编辑设计
- 新工作若需放在 Obsidian 的 Document 下，先使用 `Document/input` 目录，获许可后再迁移
