# KT Admin 默认模板的 SLOT 与片段

仅在原型选择本 skill 自带的 KT Admin 模板时使用本文件。项目已有视觉与交互依据时以项目为准，不加载或套用这些规则。

## 使用原则

- 可以复制 `assets/page-skeleton.html` 作为标准后台页面起点。
- 优先复用 `assets/fragments/` 中适合当前页面的主内容片段。
- 可以复制 `assets/base.css` 到输出中使用。
- 不修改 skill 自带的源资产。片段不能准确表达需求时，在原型输出中补充或调整结构。

## 骨架 SLOT

| SLOT | 内容 |
|---|---|
| `SLOT:page_name` | 页面名称，纯文本 |
| `SLOT:page_title` | 顶栏标题 |
| `SLOT:base_css` | `assets/base.css` 全文，原样复制 |
| `SLOT:sidebar_items` | 侧边栏 `<li>` 列表 |
| `SLOT:main_content` | 适合时组合现有片段，否则使用当前原型需要的主内容 |
| `SLOT:drawer` | 复制 `fragments/drawer.html`；无抽屉时留空 |
| `SLOT:confirm_modal` | 复制 `fragments/confirm-modal.html`；无删除操作时留空 |

## 页面类型与片段

| 页面特征 | 页面类型 | 片段 |
|---|---|---|
| 筛选区 + 表格 | `list` | `filter-bar` + `table` |
| Tab，每个 Tab 内含表格 | `tabbed-list` | `tab-container`，每个 panel 内嵌 `filter-bar` + `table` |
| 无表格，只展示字段 | `detail` | 多个 `desc-list` |
| 统计卡片 + 图表/表格 | `dashboard` | `stat-cards` + `table` 或图表占位 |
| 主要是表单输入 | `form` | `form-page` |
| 多种结构组合 | `hybrid` | 按实际顺序拼合多个片段 |

## 常用子 SLOT

`filter_fields` 每个字段使用输入框、下拉、日期区间、开关、单选/多选中最接近的控件；宽度使用片段原有风格。

`filter_buttons` 默认包含查询、重置；新增按钮使用 `ant-btn ant-btn-primary` 并加稳定 `id`。

`table_thead` 必须体现列名、对齐和宽度；操作列通常居中。

`table_tbody` 至少 3 行，字段值必须符合业务语义；操作列使用 `.action-group` 和 `.action-divider`。

`drawer_form_fields` 使用 Ant Design 表单结构；必填字段显示红色星号；详情模式控件加 `disabled` 并使用浅灰背景。
