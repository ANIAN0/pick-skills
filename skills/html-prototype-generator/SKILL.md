---
name: html-prototype-generator
description: |
  **确保使用此技能** 当用户需要「生成HTML原型」「创建可分享原型」「需求转原型页面」「复刻已有页面为原型」「/htmlproto」或任何涉及生成轻量级HTML原型页面的请求时。特别适用于需要与 kt-agent-framework 管理后台风格一致的原型，以及需要在已有页面上新增功能的场景。

  本技能生成独立HTML文件，风格与实际项目页面一致，可直接在浏览器打开分享，无需构建工具。

  **触发关键词**: 生成原型、创建原型、需求转原型、复刻页面、原型页面、/htmlproto、改造原型、页面原型、HTML原型
---

# HTML Prototype Generator

## 设计原则（唯一真理）

**LLM 只负责填写数据，不负责生成结构。**

- 外壳骨架来自 `assets/page-skeleton.html`，机械复制，不得重新生成
- 主内容区来自 `assets/fragments/`，按页面类型组合，不得自由生成
- 样式来自 `assets/base.css`，原样内联，不得修改或重写
- 引导层逻辑来自 `assets/guide-layer.js`，原样内联，不得修改
- LLM 的任务：识别页面类型 → 选取 fragments 组合 → 填入各 SLOT 的数据

---

## 铁律

| 规则 | 违反示例 | 正确做法 |
|------|---------|---------|
| 骨架不变 | 自己写 `<aside>` 结构 | 从 `page-skeleton.html` 复制，只填 SLOT |
| 内容区用片段 | 在 `main_content` 里自由写 HTML | 从 `assets/fragments/` 选取片段组合 |
| 样式不改 | 重写 `.kt-status` CSS | 从 `base.css` 原样复制进 `<style>` |
| 引导层不改 | 重新实现 badge/card JS | `guide-layer.js` 原样复制，只改 `GUIDE_STEPS` |
| 配色固定 | 使用 `#1890ff` 作为主色 | 主色只用 `#3e8dff` |
| 禁止 emoji | 侧边栏用 🏠🤖 | 用 `anticon anticon-home` 或首字母色块 |
| 复刻两阶段 | 直接按需求重写页面 | 先 1:1 还原 → 等用户确认 → 再叠加改动 |
| 改动必引导 | 只在文档面板描述改动 | 每处改动写入 `GUIDE_STEPS` |

---

## 工作流程

### 第一步：判断模式

| 用户描述 | 模式 |
|---------|------|
| 提到 `.vue` 路径 / 复刻 / 在现有页面上改 | **复刻模式** |
| 提到需求文档 / 全新页面 | **需求模式** |
| 提到调整已有原型 HTML | **对话模式** |

---

### 复刻模式（严格两阶段）

#### 阶段一：1:1 还原（不做任何改动）

1. 读取 `.vue` 主文件 + 同目录 `data.ts` + `components/` 子组件
2. 逐一提取，输出确认表，**然后停止等待用户确认**：

```
✅ 还原分析
───────────────────────────────────
筛选字段（来自 searchSchema）：
  · 字段1 [input]   · 字段2 [select]   · 字段3 [date]

表格列（来自 columns）：
  序号 | 字段1(120px) | 字段2 | 状态(center) | 操作(center,180px)

操作按钮（来自 tl-filter-left）：
  [新增XXX primary]  [导出 default]

抽屉表单（来自 EditForm.vue）：
  * 字段1 [input, 必填]   · 字段2 [select]   · 字段3 [textarea]

待叠加改动：{用户描述的需求}
───────────────────────────────────
确认以上还原是否准确？有偏差请指出，确认后进入阶段二。
```

3. 用户确认准确后才进入阶段二；有偏差则修正后再次确认

#### 阶段二：叠加需求改动

- 在还原好的 HTML 基础上增删改元素
- 每处改动必须写入 `GUIDE_STEPS`（见 SLOT:guide_steps 规范）
- 给需要标注的新增/修改元素加 `id` 属性，如 `id="btn-export"`
- 移除的元素插入零高度占位：`<div class="guide-removed-N" style="height:0;overflow:hidden;" aria-hidden="true"></div>`

**.vue → HTML 映射：**

| .vue 组件 | HTML 实现 |
|-----------|----------|
| `<yc-form v-bind="searchVBind">` | 按 searchSchema 生成筛选字段（见 SLOT:filter_fields） |
| `<a-table :columns="columns">` | 按 columns 生成 `<thead>/<tbody>`（见 SLOT:table_thead/tbody） |
| `<yc-status>` | `.kt-status.kt-status-{type}` |
| `<action-group>` | `.action-group` + `<a>` + `.action-divider` |
| `<tl-drawer>` | 抽屉骨架，只填 drawer_width + drawer_form_fields |
| `hasButtonPerm()` | 移除判断，直接展示按钮 |
| API 调用 | 硬编码 ≥3 行 Mock 数据 |

---

### 需求模式

1. 读取需求文档，输出页面清单表格，等待确认：

| 序号 | 页面名称 | 类型 | 功能描述 |
|-----|---------|------|---------|

2. 确认后按 13 个 SLOT 逐一填写，生成 HTML

---

### 对话模式

1. 读取已有原型 HTML
2. 与用户确认修改点
3. 定位对应 SLOT，只修改该位置，输出新版本文件

---

## SLOT 填写规范

### 第一层：骨架固定 SLOT（每个页面必填）

| SLOT | 内容 | 来源 |
|------|------|------|
| `SLOT:page_name` | 纯文本，如 `角色列表` | 手填 |
| `SLOT:page_title` | 顶栏标题文字 | 手填 |
| `SLOT:base_css` | base.css 全文 | **原样复制，不得修改** |
| `SLOT:sidebar_items` | 侧边栏 `<li>` 列表 | 见下方规范 |
| `SLOT:main_content` | 主内容区 HTML | **从 fragments/ 组合，见第二层** |
| `SLOT:drawer` | 抽屉 HTML | 复制 `fragments/drawer.html`，无抽屉时留空 |
| `SLOT:confirm_modal` | 确认弹窗 HTML | 复制 `fragments/confirm-modal.html`，无删除操作时留空 |
| `SLOT:doc_content` | 文档面板内容 | 见下方规范 |
| `SLOT:guide_steps` | 引导层数据数组 | 见下方规范 |
| `SLOT:guide_layer_js` | guide-layer.js 全文 | **原样复制，不得修改** |

---

### 第二层：main_content 片段组合

**核心规则：`SLOT:main_content` 的内容必须从 `assets/fragments/` 选取片段拼合，不得自由生成 HTML 结构。**

#### 第一步：识别源页面类型

| 源页面特征 | 页面类型 | 使用片段 |
|-----------|---------|---------|
| 有筛选区 + 表格 | **list** | `filter-bar` + `table` |
| 有 Tab，每个 Tab 内含表格 | **tabbed-list** | `tab-container`（内嵌 `filter-bar` + `table`）|
| 无表格，只展示字段 | **detail** | 多个 `desc-list`（按分组）|
| 统计卡片 + 图表/表格 | **dashboard** | `stat-cards` + `table` 或图表占位 |
| 无表格，主要是表单输入 | **form** | `form-page` |
| 以上组合 | **hybrid** | 按实际顺序拼合多个片段 |

#### 第二步：按类型拼合片段

**list 页（最常见）：**
```
main_content =
  filter-bar（填 filter_fields + filter_buttons）
  + table（填 table_thead + table_tbody + total_count）
```

**detail 页：**
```
main_content =
  desc-list（基本信息，填 desc_section_title + desc_items）
  + desc-list（其他分组，如有）
  + table（关联记录，如有）
```

**dashboard 页：**
```
main_content =
  stat-cards（填 stat_cards_items）
  + table 或图表占位（如有）
```

**tabbed-list 页：**
```
main_content =
  tab-container（填 tab_items + tab_panels）
  tab_panels 内每个 panel = filter-bar + table
```

**form 页：**
```
main_content =
  form-page（填 form_sections，每个 section 是一个 kt-card）
```

---

### 骨架固定 SLOT 详细规范

#### SLOT:sidebar_items

**激活项（当前页面）：**
```html
<li style="padding: 10px 16px; background: #3e8dff; color: #fff; cursor: pointer; font-size: 14px; border-radius: 4px; margin: 0 8px; display: flex; align-items: center;">
  <span class="anticon anticon-team" style="margin-right: 10px; font-size: 14px;"></span>角色管理
</li>
```

**非激活项：**
```html
<li style="padding: 10px 20px; color: rgba(255,255,255,.65); cursor: pointer; font-size: 14px; display: flex; align-items: center;">
  <span class="anticon anticon-home" style="margin-right: 10px; font-size: 14px;"></span>首页
</li>
```

**无对应 anticon 时用首字母色块（禁止 emoji）：**
```html
<span style="display: inline-flex; width: 18px; height: 18px; border-radius: 3px; background: #3e8dff; color: #fff; font-size: 11px; align-items: center; justify-content: center; margin-right: 10px;">角</span>
```

常用 anticon 映射：

| 菜单名 | anticon 类名 |
|--------|-------------|
| 首页 | `anticon-home` |
| 用户管理 | `anticon-user` |
| 角色管理 | `anticon-team` |
| 系统设置 | `anticon-setting` |
| 日志 | `anticon-file-text` |
| 监控/仪表盘 | `anticon-dashboard` |
| 任务 | `anticon-thunderbolt` |

---

#### SLOT:drawer（复制 fragments/drawer.html 后填入子 SLOT）

子 SLOT 说明：

- `SLOT:drawer_width`：宽度，如 `980px`（大表单）或 `640px`（简单表单）
- `SLOT:drawer_form_fields`：表单字段，见下方表单字段规范

**表单字段规范：**

必填字段：
```html
<div class="ant-form-item">
  <div class="ant-form-item-label">
    <label><span style="color: #ff4d4f; margin-right: 4px;">*</span>字段名称</label>
  </div>
  <div class="ant-form-item-control"><div class="ant-form-item-control-input">
    <input class="ant-input" placeholder="请输入字段名称" style="max-width: 400px;">
  </div></div>
</div>
```

选填输入框：去掉 `<span style="color: #ff4d4f...">*</span>` 即可。

下拉选择：
```html
<div class="ant-form-item">
  <div class="ant-form-item-label"><label>字段名称</label></div>
  <div class="ant-form-item-control"><div class="ant-form-item-control-input">
    <div class="ant-select ant-select-single" style="width: 200px;">
      <div class="ant-select-selector"><span class="ant-select-selection-item">请选择</span></div>
    </div>
  </div></div>
</div>
```

多行文本：
```html
<div class="ant-form-item">
  <div class="ant-form-item-label"><label>描述</label></div>
  <div class="ant-form-item-control"><div class="ant-form-item-control-input">
    <textarea class="ant-input" rows="3" placeholder="请输入描述" style="max-width: 400px; resize: vertical;"></textarea>
  </div></div>
</div>
```

详情模式（disabled）：所有 input/textarea/select 加 `disabled` 属性，背景色 `#f5f5f5`。

---

#### 片段子 SLOT 规范

**filter_fields**（每个字段三选一）：
```html
<!-- 输入框 -->
<input class="ant-input" placeholder="请输入XXX" style="width: 200px;">

<!-- 下拉 -->
<div class="ant-select ant-select-single" style="width: 160px;">
  <div class="ant-select-selector"><span class="ant-select-selection-item">全部状态</span></div>
</div>

<!-- 日期区间 -->
<span class="ant-picker" style="width: 220px;">
  <span class="ant-picker-input">
    <input readonly placeholder="开始 ~ 结束" style="border: none; outline: none; width: 100%; background: transparent; cursor: pointer;">
  </span>
</span>
```

**filter_buttons**：
```html
<button class="ant-btn ant-btn-primary" onclick="mockAction('查询')">查询</button>
<button class="ant-btn" onclick="mockAction('重置')">重置</button>
<!-- 新增按钮（加 id 供引导层定位）-->
<button class="ant-btn ant-btn-primary" id="btn-add" onclick="openDrawer('新增XXX', 'add')">新增XXX</button>
```

**table_thead**：
```html
<th class="ant-table-cell" style="text-align: center; width: 60px;">序号</th>
<th class="ant-table-cell">名称</th>
<th class="ant-table-cell" style="width: 120px;">状态</th>
<th class="ant-table-cell" style="text-align: center; width: 180px;">操作</th>
```

**table_tbody**（≥3 行，字段值符合业务语义）：
```html
<tr class="ant-table-row">
  <td class="ant-table-cell" style="text-align: center;">1</td>
  <td class="ant-table-cell">示例名称</td>
  <td class="ant-table-cell">
    <span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span>
  </td>
  <td class="ant-table-cell" style="text-align: center;">
    <div class="action-group">
      <a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer('详情', 'detail')">详情</a>
      <span class="action-divider"></span>
      <a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer('编辑', 'edit')">编辑</a>
      <span class="action-divider"></span>
      <a style="color: #ff4d4f; cursor: pointer;" onclick="openConfirmModal()">删除</a>
    </div>
  </td>
</tr>
```

状态标签固定映射：

| 语义 | 类名 |
|------|------|
| 启用 / 在线 / 成功 | `kt-status-success` |
| 禁用 / 离线 / 错误 | `kt-status-danger` |
| 待审核 / 处理中 | `kt-status-warning` |
| 运行中 / 主要状态 | `kt-status-primary` |
| 未知 / 默认 | `kt-status-default` |

**desc_items**（detail 页描述列表行）：
```html
<div class="kt-desc-item">
  <div class="kt-desc-label">字段名</div>
  <div class="kt-desc-value">字段值</div>
</div>
<!-- 跨整行的长内容 -->
<div class="kt-desc-item full-width">
  <div class="kt-desc-label">描述</div>
  <div class="kt-desc-value">较长的描述内容</div>
</div>
```

**stat_cards_items**（dashboard 统计卡片）：
```html
<div class="kt-stat-card">
  <div class="kt-stat-card-label">今日请求量</div>
  <div class="kt-stat-card-value is-primary">12,847</div>
  <div class="kt-stat-card-footer">较昨日 +8.3%</div>
</div>
```

**tab_items**（Tab 标签头）：
```html
<div class="ant-tabs-tab ant-tabs-tab-active" style="padding: 12px 0; margin-right: 32px; cursor: pointer; font-size: 14px; color: #3e8dff; border-bottom: 2px solid #3e8dff;">Tab 一</div>
<div class="ant-tabs-tab" style="padding: 12px 0; margin-right: 32px; cursor: pointer; font-size: 14px; color: rgba(0,0,0,.65);">Tab 二</div>
```

**tab_panels**（Tab 内容区，只显示激活项）：
```html
<!-- 激活 panel -->
<div class="ant-tabs-tabpane ant-tabs-tabpane-active">
  <!-- 此处放 filter-bar + table 片段内容 -->
</div>
<!-- 非激活 panel（隐藏）-->
<div class="ant-tabs-tabpane" style="display: none;">
  <!-- 此处放 filter-bar + table 片段内容 -->
</div>
```

**form_sections**（form 页分组卡片）：
```html
<div class="kt-card" style="margin-bottom: 16px;">
  <div class="kt-card-header">
    <div class="kt-card-title">基本信息</div>
  </div>
  <div class="kt-card-body">
    <form class="ant-form ant-form-vertical" onsubmit="return false;">
      <!-- 表单字段，格式同 drawer_form_fields -->
    </form>
  </div>
</div>
```

---

#### SLOT:doc_content

```html
<div style="background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
  <div style="font-size: 15px; font-weight: 600; color: rgba(0,0,0,.85); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">页面说明</div>
  <p style="color: rgba(0,0,0,.65); font-size: 14px; margin: 0;">一句话描述页面用途。</p>
</div>
<div style="background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
  <div style="font-size: 15px; font-weight: 600; color: rgba(0,0,0,.85); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">交互逻辑</div>
  <div style="font-size: 14px; color: rgba(0,0,0,.65); line-height: 2;">
    <div><b>查询：</b>填写筛选条件后点击查询</div>
    <div><b>新增：</b>点击新增按钮打开右侧抽屉</div>
    <div><b>编辑：</b>点击编辑打开抽屉并回填数据</div>
    <div><b>删除：</b>弹出确认弹窗，确认后删除</div>
  </div>
</div>
```

---

#### SLOT:guide_steps

无改动时：空数组 `[]`。

有改动时每项必须包含 5 个字段：
```javascript
{
  id: 1,
  selector: '#btn-export',       // 页面中真实存在的 CSS 选择器
  type: 'new',                   // new | modified | removed
  title: '新增：导出按钮',
  desc: '支持将筛选结果导出为 Excel，运营角色及以上可见',
},
```

移除元素时，在原位置插入占位符：
```html
<div class="guide-removed-1" style="height: 0; overflow: hidden;" aria-hidden="true"></div>
```

---

#### SLOT:guide_layer_js
从 `assets/guide-layer.js` 原样复制全部内容，不修改任何一行。

---

## 遇到未定义样式时怎么办

### 第一步：查表，确认组件归属

遇到任何需要样式的组件，先按下表判断归属，再决定下一步：

| 组件类型 | 归属 | 使用方式 |
|---------|------|---------|
| 按钮、输入框、下拉、日期、开关、单选、多选、表格、表单、弹窗、抽屉、标签页、步骤条、树形、上传、折叠、面包屑 | **Ant Design 自带** | 直接用 `ant-*` 类名，antd CSS 已覆盖，无需额外样式 |
| 状态标签（带圆点背景色） | **`base.css` Layer 3** | `kt-status kt-status-{success\|danger\|warning\|primary\|default}` |
| 操作列按钮组 | **`base.css` Layer 4** | `action-group` + `action-divider` |
| 统计卡片 | **`base.css` Layer 5a** | `kt-stat-card` + `kt-stat-card-label` + `kt-stat-card-value` |
| 详情页描述列表 | **`base.css` Layer 5b** | `kt-desc-list` + `kt-desc-item` + `kt-desc-label` + `kt-desc-value` |
| 通用卡片容器 | **`base.css` Layer 5c** | `kt-card` + `kt-card-header` + `kt-card-title` + `kt-card-body` |
| 空状态 | **`base.css` Layer 5d** | `kt-empty` + `kt-empty-icon` + `kt-empty-text` |
| 代码/JSON展示 | **`base.css` Layer 5e** | `kt-code-block` |

### 第二步：仍然找不到时，按优先级处理

**优先级 1 — 用 Tailwind 工具类拼装（首选）**

Tailwind 的布局和间距类（`flex`、`grid`、`gap-*`、`p-*`、`rounded-*`、`shadow-*`、`text-*`、`bg-*`）可以自由组合，不算"自创样式"。颜色值必须使用 CSS 变量：

```html
<!-- 正确：Tailwind 布局 + CSS 变量配色 -->
<div class="flex items-center gap-3 p-4 rounded-lg" style="background: var(--kt-primary-bg); color: var(--kt-primary);">
  内容
</div>

<!-- 错误：硬编码颜色 -->
<div style="background: #e6f0ff; color: #1a6edb;">内容</div>
```

**优先级 2 — 用 `style=""` 内联，只用 CSS 变量**

当 Tailwind 工具类不够用时，可以写内联样式，但颜色**只能引用 CSS 变量**，不得硬编码新色值：

```html
<!-- 正确：引用变量 -->
<div style="border-left: 3px solid var(--kt-primary); padding: 8px 12px; background: var(--kt-primary-bg);">
  提示内容
</div>

<!-- 错误：新增硬编码颜色 -->
<div style="border-left: 3px solid #4a9eff; background: #e8f2ff;">提示内容</div>
```

**优先级 3 — 在 `<style>` 块末尾追加，命名必须以 `kt-` 开头**

仅当上述两种方式都无法实现时，在 `base.css` 内联块**末尾**追加新类，**不得插入或修改已有内容**：

```html
<style>
  /* ── base.css 内容（原样，不动）── */
  ...

  /* ── 本页扩展（仅此页需要，命名以 kt- 开头）── */
  .kt-timeline-item { ... }
  .kt-tag-group { ... }
</style>
```

规则：
- 类名必须以 `kt-` 开头（与项目命名空间一致）
- 颜色只用 `var(--kt-*)` 变量
- 只追加在末尾，不修改 Layer 1-5 任何内容
- 若该扩展具有通用价值，在文档面板注明「建议将 `.kt-xxx` 补充到 base.css」

**绝对禁止：**
- 修改 `base.css` Layer 1-5 的任何现有规则
- 引入项目色板外的新颜色（不在 `--kt-*` 变量中的色值）
- 覆盖 Ant Design 组件的内部结构样式

---

### 组件使用示例

**统计卡片（dashboard 页）：**
```html
<div class="kt-stat-card">
  <div class="kt-stat-card-label">今日请求量</div>
  <div class="kt-stat-card-value is-primary">12,847</div>
  <div class="kt-stat-card-footer">较昨日 +8.3%</div>
</div>
```

**描述列表（detail 页，双列）：**
```html
<div class="kt-desc-list">
  <div class="kt-desc-item">
    <div class="kt-desc-label">角色名称</div>
    <div class="kt-desc-value">超级管理员</div>
  </div>
  <div class="kt-desc-item">
    <div class="kt-desc-label">创建时间</div>
    <div class="kt-desc-value">2024-01-15 10:30:00</div>
  </div>
  <div class="kt-desc-item full-width">
    <div class="kt-desc-label">描述</div>
    <div class="kt-desc-value">拥有系统所有权限</div>
  </div>
</div>
```

**空状态：**
```html
<div class="kt-empty">
  <div class="kt-empty-icon"></div>
  <div class="kt-empty-text">暂无数据</div>
  <div class="kt-empty-sub">请调整筛选条件后重试</div>
</div>
```

**代码展示：**
```html
<div class="kt-code-block">{"key": "value", "status": 1}</div>
```

**Tailwind 拼装示例（提示条，base.css 无此组件）：**
```html
<div class="flex items-start gap-2 p-3 rounded" style="background: var(--kt-warning-bg);">
  <span class="anticon anticon-warning" style="color: var(--kt-warning); margin-top: 2px;"></span>
  <span style="color: var(--kt-text-secondary); font-size: 14px;">此操作不可撤销，请谨慎操作。</span>
</div>
```

---

## 输出规范

- **目录：** `.dev/prototype/`
- **命名：** `prototype-{YYYYMMDD}-{页面名称}.html`，改造版加 `-v{N}`
- **不覆盖** 已有文件
- **多页面** 时同时生成 `index.html` 目录页（规范见 `docs/output-format.md`）
- **多页面** 时每个页面用独立 Subagent 生成，避免上下文污染

---

## 自检清单（生成后逐项核对）

**结构与资产**
- [ ] 骨架完整复制自 `page-skeleton.html`，未自行重写侧边栏/顶栏/脚本等外壳结构
- [ ] `main_content` 内容来自 `fragments/` 片段组合，未自由生成 HTML 结构
- [ ] `base.css` 原样内联在 `<style>` 块开头，未修改 Layer 1-5 任何内容
- [ ] `guide-layer.js` 原样内联，未修改

**样式规范**
- [ ] 主色为 `#3e8dff`，无 `#1890ff` 作主色
- [ ] 无 emoji，图标用 `anticon` 类名或首字母色块
- [ ] 状态标签只用 5 种固定 `kt-status-*` 类名
- [ ] 扩展样式（若有）：类名以 `kt-` 开头，颜色只用 `var(--kt-*)` 变量，追加在 `<style>` 末尾

**交互与数据**
- [ ] 抽屉/弹窗已合并到主 HTML
- [ ] Mock 数据 ≥3 行，字段值符合业务语义

**复刻模式**
- [ ] 已输出还原确认表并停止等待用户确认
- [ ] 有改动：每处改动已写入 `GUIDE_STEPS`，selector 在页面中可找到
- [ ] 无改动：`GUIDE_STEPS = []`

**输出**
- [ ] 文件保存至 `.dev/prototype/`，未覆盖已有文件
- [ ] 多页面：已生成 `index.html`
