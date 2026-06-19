---
name: html-prototype-generator
description: |
  **确保使用此技能** 当用户需要「生成HTML原型」「创建可分享原型」「需求转原型页面」「复刻已有页面为原型」「/htmlproto」或任何涉及生成轻量级HTML原型页面的请求时。特别适用于需要与 kt-agent-framework 管理后台风格一致的原型，以及需要在已有页面上新增功能的场景。

  本技能生成独立HTML文件，风格与实际项目页面一致，可直接在浏览器打开分享，无需构建工具。

  **触发关键词**: 生成原型、创建原型、需求转原型、复刻页面、原型页面、/htmlproto、改造原型、页面原型、HTML原型
---

# HTML Prototype Generator

## 目标

生成与 kt-agent-framework 管理后台风格一致的独立HTML原型页面。产物为单个HTML文件，可直接在浏览器打开，方便分享。

三种工作模式：
- **复刻模式**：读取已有 .vue 页面，**1:1 还原**后再叠加需求改动
- **需求模式**：根据需求文档生成全新原型页面
- **对话模式**：读取已有原型HTML，讨论并调整

---

## 设计核心

原型的核心价值是「与真实页面尽可能一致」。以下是必须遵守的设计规范：

### 样式原则

1. **Ant Design 组件结构优先**：组件 HTML 结构和类名必须遵循 Ant Design 4.x 规范（如 `ant-btn`、`ant-table`、`ant-form` 等），项目配色覆盖主色但不改变组件结构
2. **禁止使用 Emoji**：侧边栏图标、按钮图标、状态标识等一律使用 CSS/SVG 实现或 Ant Design 图标类名（如 `anticon anticon-home`），绝不使用 emoji 字符（🏠🤖📋 等）
3. **状态标签**：简单状态优先使用 `ant-tag` 系列，需要带圆点和背景色时才用自定义 `.kt-status`

### 配色（来自项目 const.less）

| 用途 | 色值 | 背景色 |
|-----|------|-------|
| Primary | #3e8dff | #d6e7ff |
| Success | #00e5c7 | #effffb |
| Danger | #ff8b78 | #fff5f3 |
| Warning | #ffb71d | #fff2d6 |
| Default | #bfc6d1 | #f5f6f9 |
| Ant Blue | #1890ff | - |

### 布局参数

- 侧边栏：#1e202a，220px宽
- 顶栏：#fff，56px高
- 内容区背景：#f0f2f5
- 卡片：白色，8px圆角，shadow-sm
- 表格：bordered + small 模式

详细组件规范见 `docs/design-guide.md`。

---

## 工作流程

### Phase 1: 确定工作模式

| 用户意图 | 模式 | 第一步 |
|---------|------|-------|
| 提到已有页面路径、复制页面、在现有页面上加功能 | 复刻模式 | 读取 .vue 源文件 |
| 提到需求文档、新建页面 | 需求模式 | 读取需求文档 |
| 提到调整已有原型 | 对话模式 | 读取原型HTML |

---

### Phase 2A: 复刻模式（⚠️ 必须严格遵守两阶段原则）

**核心原则：先 1:1 完整还原，再叠加需求改动。** 绝不能跳过还原阶段直接按需求重写。

#### 阶段一：1:1 还原源页面（不做任何改动）

1. 读取 .vue 主文件及其关联的 `data.ts`、子组件（路径在 `D:\workspace\Document\input\kt-agent-framework\admin_frontend\src\pages\`）
2. **逐一还原以下所有元素**（缺一不可）：
   - 侧边栏菜单项（完全按源页面菜单结构）
   - 筛选区所有字段（来自 `searchSchema`，字段顺序、label、组件类型必须一致）
   - 操作按钮（来自 `tl-filter-left` 区域，按钮文案、顺序一致）
   - 表格所有列（来自 `columns`，列顺序、title、宽度、对齐方式一致）
   - 操作列按钮（来自 `action-group`，按钮文案、顺序一致；移除 `hasButtonPerm` 判断直接展示）
   - 状态标签（来自 `yc-status`，还原为 `.kt-status` + 对应颜色）
   - 抽屉/表单（来自子组件 EditForm，还原所有表单字段、required 标记）
   - Mock 数据（≥3行，字段值与业务语义一致）
3. 还原完成后，向用户展示分析结果表格：

   ```
   ✅ 已还原：[筛选字段 N 个] [表格列 N 个] [操作按钮 N 个] [表单字段 N 个]
   📋 待叠加改动：[用户需求描述]
   ```

   等待用户确认还原是否准确，如有偏差先修正再进入阶段二。

#### 阶段二：叠加需求改动

在已还原的 HTML 基础上，按需求增删改元素。**改动必须通过需求引导层标注**（见 Phase 3 引导层规范）：
- 新增的元素：加 `data-guide-new` 属性
- 修改的元素：加 `data-guide-modified` 属性
- 删除的位置：插入 `data-guide-removed` 占位注释

**.vue → HTML 映射规则：**
- `<tl>` → 整个页面容器
- `<tl-main>` → 主内容区（flex: 1, overflow auto）
- `<tl-filter>` → 筛选区卡片
- `<tl-filter-left>` → 筛选区内容（flex wrap）
- `<yc-form v-bind="searchVBind" />` → 根据 searchSchema 生成筛选字段
- `<tl-table>` → 表格卡片容器（白色背景 + 圆角 + shadow）
- `<a-table>` → Ant Design 表格（HTML版）
- `<tl-drawer>` → 右侧抽屉
- `<action-group>` → 操作按钮组（a-space + link buttons）
- `<yc-status>` → 状态标签（简单状态用 `ant-tag`，需要圆点背景色用 `.kt-status`）
- `useDrawer` → JS 控制抽屉开关（openDrawer/closeDrawer）
- `useTable` → 静态表格数据 + 分页
- `hasButtonPerm()` → 移除权限判断，直接展示按钮
- API 调用 → 硬编码 Mock 数据

---

### Phase 2B: 需求模式

1. 读取需求文档，提取功能列表
2. 输出页面清单表格，等待用户确认

   | 序号 | 页面名称 | 页面类型 | 功能描述 | 优先级 |
   |-----|---------|---------|---------|-------|

3. 分轮次澄清需求（每轮最多3问）
4. 确认后生成HTML原型，**需求描述通过引导层展示**（见 Phase 3）

**生成前检查现有页面：**
- 扫描 `.dev/prototype/` 目录查找现有原型
- 继承现有页面的配色和组件风格

---

### Phase 2C: 对话模式

1. 读取已有原型HTML文件
2. 与用户讨论需要调整的部分
3. 修改对应的HTML并保存为新版本

---

### Phase 3: 需求引导层（⚠️ 新功能，所有含需求改动的原型必须包含）

**什么是需求引导层？**

类似新手引导的交互效果：原型页面上叠加一个半透明蒙版，对每一处需求改动（新增/修改/删除）显示高亮框 + 气泡说明，让查看者直观理解"这里改了什么、为什么改"。

**实现规则：**

1. 默认显示引导层（首次打开即展示）
2. 右上角提供「关闭引导」/「开启引导」切换按钮
3. 引导项按序号排列，可点击序号跳转到对应元素
4. 高亮框自动定位到目标元素（使用 `getBoundingClientRect()`）
5. 气泡显示在元素旁边，避免遮挡关键内容

**引导项数据结构（在 `<script>` 中定义）：**

```javascript
const guideSteps = [
  {
    id: 1,
    selector: '#btn-export',       // 目标元素 CSS 选择器
    type: 'new',                   // new | modified | removed
    title: '新增：导出按钮',
    desc: '支持将当前筛选结果导出为 Excel 文件，权限：运营角色及以上可见',
  },
  {
    id: 2,
    selector: 'th[data-col="status"]',
    type: 'modified',
    title: '修改：状态列',
    desc: '原「启用/禁用」两态改为「启用/禁用/待审核」三态，新增黄色待审核样式',
  },
  {
    id: 3,
    selector: '.guide-removed-placeholder-1',
    type: 'removed',
    title: '移除：批量操作栏',
    desc: '经产品确认，当前版本不需要批量操作，已移除，后续迭代再加',
  },
];
```

**视觉规范：**

| 改动类型 | 高亮色 | 气泡标签色 |
|---------|-------|----------|
| new（新增）| #3e8dff（蓝色边框） | #3e8dff 背景，白字「新增」 |
| modified（修改） | #ffb71d（橙色边框） | #ffb71d 背景，白字「修改」 |
| removed（移除） | #ff8b78（红色边框） | #ff8b78 背景，白字「移除」|

完整HTML实现示例见 `docs/design-guide.md` → 第8节「需求引导层」。

---

### Phase 4: 生成原型

**单页面生成**：直接调用脚本或手写 HTML。

```bash
python scripts/generate_page.py --input '{
  "page_name": "角色列表",
  "page_type": "list",
  "scenario": "clone",
  "source_vue": "src/pages/role/index.vue",
  "output_path": ".dev/prototype",
  "clarification": {
    "layout": {},
    "data": {},
    "interactions": {},
    "modifications": "新增启用/禁用开关列"
  }
}'
```

**多页面生成 — 使用 Subagent 隔离上下文**：

当需要同时生成多个原型页面时，必须为每个页面启动独立的 Subagent，避免上下文污染。

```python
# 每个页面一个 subagent，并行生成
# 使用 Agent 工具，subagent_type 为 "general-purpose"
# 每个 subagent 独立读取 SKILL.md 和 docs/
# 每个 subagent 独立完成一个页面的生成并写入文件
```

---

### Phase 5: 文件输出

**输出目录：** `.dev/prototype/`

**命名规则：**
- 新原型：`prototype-{YYYYMMDD}-{页面名称}.html`
- 改造原型：`prototype-{YYYYMMDD}-{页面名称}-v{N}.html`

**页面结构：**
- 抽屉、弹窗等交互元素合并到主页面HTML中
- 通过 CSS `display:none` / JavaScript 控制显示隐藏
- 需求引导层默认展示，右上角可关闭
- 文档面板（交互说明）默认隐藏，点击「交互说明」按钮展开
- 保留旧文件（绝不覆盖）

**目录页（index.html）：**
- 多页面生成完成后，必须在 `.dev/prototype/` 下生成 `index.html` 目录页
- 详细规范见 `docs/output-format.md`

---

## 页面类型

| 类型 | 说明 | 典型组件 |
|-----|------|---------|
| list | 列表页 | 筛选区、表格、分页、操作按钮、抽屉 |
| form | 表单页 | 表单字段、提交/取消 |
| detail | 详情页 | 信息分组、描述列表 |
| dashboard | 仪表盘 | 统计卡片、图表、快捷入口 |

---

## 约束

- **必须使用 Ant Design 4.x CSS**：`antd.min.css` CDN
- **必须应用项目配色**：#3e8dff 主色，非 Ant Design 默认 #1890ff
- **遵循 Ant Design 组件结构**：即使配色被覆盖，HTML 结构和类名遵循 Ant Design 4.x 规范
- **禁止使用 Emoji**：所有图标使用 Ant Design 图标类名或 CSS 实现
- **Tailwind 仅用于布局工具类**：flex、grid、间距，不用于组件样式
- **单文件输出**：每个HTML包含完整原型，可直接打开
- **Mock数据**：硬编码，无API调用
- **不使用 @apply**：CDN模式不生效
- **复刻模式两阶段**：必须先1:1还原，再叠加改动
- **有需求改动必须有引导层**：不能用文档面板替代
- **多页面用 Subagent**：同时生成多个页面时，每个页面在独立 subagent 中生成

---

## 参考资源

- **设计规范**：`docs/design-guide.md` — 完整设计规范和组件HTML示例（第8节为引导层实现）
- **输出格式**：`docs/output-format.md` — HTML输出格式详细规范
- **页面生成脚本**：`scripts/generate_page.py` — 单页面生成
- **批量生成脚本**：`scripts/batch_generate.py` — 多页面批量生成
- **复刻分析脚本**：`scripts/clone_page.py` — .vue 文件结构提取

**项目前端源码参考：** `D:\workspace\Document\input\kt-agent-framework\admin_frontend\src\`

---

## 自检清单

- [ ] HTML文件可在浏览器正常打开
- [ ] 配色使用项目色值（#3e8dff 主色等）
- [ ] 侧边栏 #1e202a，顶栏白色
- [ ] 使用 Ant Design 组件类名（ant-btn、ant-table 等）
- [ ] 无 emoji 字符，图标使用 anticon 类名或 CSS 实现
- [ ] 状态标签：简单用 ant-tag，需圆点用 .kt-status
- [ ] 抽屉/弹窗合并到主页面
- [ ] 文档面板可切换显示
- [ ] 文件保存到 `.dev/prototype/`
- [ ] **复刻模式：源页面所有字段/列/按钮已1:1还原（不遗漏）**
- [ ] **有需求改动：已包含需求引导层，改动项已全部标注**
- [ ] Mock数据合理（≥3行，语义正确）
- [ ] 多页面时已生成 index.html 目录页
- [ ] 多页面时使用了 subagent 隔离上下文
