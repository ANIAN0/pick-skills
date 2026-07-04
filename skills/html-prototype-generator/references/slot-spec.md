# SLOT 与片段规范

## 固定原则

- 外壳骨架来自 `assets/page-skeleton.html`，机械复制，只填 SLOT。
- 主内容区来自 `assets/fragments/`，按页面类型组合。
- 样式来自 `assets/base.css`，原样内联。
- 引导层逻辑来自 `assets/guide-layer.js`，原样内联。

## 骨架 SLOT

| SLOT | 内容 |
|---|---|
| `SLOT:page_name` | 页面名称，纯文本 |
| `SLOT:page_title` | 顶栏标题 |
| `SLOT:base_css` | `assets/base.css` 全文，原样复制 |
| `SLOT:sidebar_items` | 侧边栏 `<li>` 列表 |
| `SLOT:main_content` | 从 `assets/fragments/` 组合出的主内容 |
| `SLOT:drawer` | 复制 `fragments/drawer.html`；无抽屉时留空 |
| `SLOT:confirm_modal` | 复制 `fragments/confirm-modal.html`；无删除操作时留空 |
| `SLOT:doc_content` | 文档面板内容 |
| `SLOT:guide_steps` | 引导层数据数组 |
| `SLOT:guide_layer_js` | `assets/guide-layer.js` 全文，原样复制 |

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

`doc_content` 说明页面用途和交互逻辑，不代替页面内真实控件。

## GUIDE_STEPS

无改动时使用空数组 `[]`。有改动时每项必须包含：

```javascript
{
  id: 1,
  selector: '#btn-export',
  type: 'new',
  title: '新增：导出按钮',
  desc: '支持将筛选结果导出为 Excel，运营角色及以上可见',
}
```

字段规则：

- `id` 从 1 开始，页面内唯一。
- `selector` 必须能被 `document.querySelector()` 找到。
- `type` 只能是 `new`、`modified`、`removed`。
- `title` 使用"新增：元素名"、"修改：元素名"、"移除：元素名"。
- `desc` 一句话说明改了什么，以及权限、条件或注意事项。
