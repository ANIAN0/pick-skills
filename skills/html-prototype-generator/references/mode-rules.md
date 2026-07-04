# 模式规则

## 复刻模式

触发信号：用户提到 `.vue` 路径、"复刻"、"在现有页面上改"、"基于当前页面新增"。

阶段一只做 1:1 还原分析，不生成叠加改动：

1. 读取 `.vue` 主文件、同目录 `data.ts`、`components/` 子组件、schema、columns、mock 或类型文件。
2. 提取筛选字段、表格列、操作按钮、抽屉/弹窗表单、状态标签、待叠加改动。
3. 输出还原确认表后停止，等待用户确认。

确认表格式：

```text
还原分析
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

阶段二在确认后的 HTML 基础上叠加需求改动：

- 每处新增、修改、移除都写入 `GUIDE_STEPS`。
- 新增或修改元素必须有稳定 `id` 或 CSS selector。
- 移除元素在原位置插入零高度占位：`<div class="guide-removed-N" style="height:0;overflow:hidden;" aria-hidden="true"></div>`。
- API 调用统一替换为至少 3 行业务语义合理的 Mock 数据。

常见 `.vue` 到 HTML 映射：

| `.vue` 组件 | HTML 实现 |
|---|---|
| `<yc-form v-bind="searchVBind">` | 按 searchSchema 生成筛选字段 |
| `<a-table :columns="columns">` | 按 columns 生成 `<thead>/<tbody>` |
| `<yc-status>` | `.kt-status.kt-status-{type}` |
| `<action-group>` | `.action-group` + `<a>` + `.action-divider` |
| `<tl-drawer>` | 抽屉骨架，只填 drawer 宽度和字段 |
| `hasButtonPerm()` | 移除判断，直接展示按钮 |

## 需求模式

触发信号：用户提供需求文档、PRD、页面描述或全新页面要求。

1. 读取需求文档，输出页面清单表格：序号、页面名称、类型、功能描述。
2. 页面清单确认后生成 HTML。
3. 多页面时每个页面独立生成，并更新 `index.html`。

## 对话模式

触发信号：用户要求调整已有原型 HTML。

1. 读取已有原型 HTML。
2. 明确修改点。
3. 定位对应 SLOT 或片段位置，只修改该位置。
4. 输出新版本文件，不覆盖原文件。
