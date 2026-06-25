# KT Admin 原型设计参考

> 本文档供查阅参考。**生成时以 SKILL.md 的 SLOT 规范为准**，不要从本文档重新推导结构。

---

## 配色速查

| 变量名 | 色值 | 背景色 | 用途 |
|--------|------|--------|------|
| `--kt-primary` | `#3e8dff` | `#d6e7ff` | 主按钮、链接、选中态 |
| `--kt-success` | `#00e5c7` | `#effffb` | 启用、在线、成功 |
| `--kt-danger` | `#ff8b78` | `#fff5f3` | 删除、错误、禁用 |
| `--kt-warning` | `#ffb71d` | `#fff2d6` | 警告、待审核 |
| `--kt-default` | `#bfc6d1` | `#f5f6f9` | 默认、未知 |
| 侧边栏背景 | `#1e202a` | — | 左侧深色导航 |
| 内容区背景 | `#f0f2f5` | — | 页面主背景 |
| 顶栏背景 | `#ffffff` | — | 顶部固定栏 |
| 文字主要 | `rgba(0,0,0,.85)` | — | 标题 |
| 文字次要 | `rgba(0,0,0,.65)` | — | 正文 |
| 文字提示 | `rgba(0,0,0,.45)` | — | placeholder |
| 边框 | `#f0f0f0` | — | 分割线、卡片 |

---

## anticon 图标速查

| 菜单 / 场景 | 类名 |
|------------|------|
| 首页 | `anticon anticon-home` |
| 用户管理 | `anticon anticon-user` |
| 角色管理 | `anticon anticon-team` |
| 权限 | `anticon anticon-safety` |
| 系统设置 | `anticon anticon-setting` |
| 日志 | `anticon anticon-file-text` |
| 监控 | `anticon anticon-dashboard` |
| 任务 | `anticon anticon-thunderbolt` |
| 数据 | `anticon anticon-bar-chart` |
| 搜索 | `anticon anticon-search` |

无对应 anticon 时用首字母色块（**禁止 emoji**）：
```html
<span style="display:inline-flex;width:18px;height:18px;border-radius:3px;background:#3e8dff;color:#fff;font-size:11px;align-items:center;justify-content:center;margin-right:10px;">角</span>
```

---

## 状态标签速查

| 语义 | 类名组合 |
|------|---------|
| 启用 / 成功 / 在线 | `kt-status kt-status-success` |
| 禁用 / 错误 / 离线 | `kt-status kt-status-danger` |
| 待审核 / 处理中 | `kt-status kt-status-warning` |
| 运行中 / 主要 | `kt-status kt-status-primary` |
| 未知 / 默认 | `kt-status kt-status-default` |

```html
<span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span>
```

---

## 引导层改动类型速查

| type | 高亮色 | 标签 | 适用场景 |
|------|--------|------|---------|
| `new` | `#3e8dff` 蓝色实线 | 新增 | 新增按钮、新增列、新增功能区 |
| `modified` | `#ffb71d` 橙色实线 | 修改 | 现有元素的文案/样式/行为变化 |
| `removed` | `#ff8b78` 红色虚线 | 移除 | 已删除的元素位置 |

移除占位元素写法：
```html
<div class="guide-removed-1" style="height:0;overflow:hidden;" aria-hidden="true"></div>
```

---

## 页面类型说明

| 类型 | 典型结构 | 抽屉宽度 |
|------|---------|---------|
| `list` | 筛选区 + 表格 + 分页 + 操作抽屉 | `980px` |
| `form` | 独立表单页，无表格 | 不需要 |
| `detail` | 描述列表，字段展示为只读 | `640px` |
| `dashboard` | 统计卡片 + 图表 | 不需要 |

---

## 需求引导层 GUIDE_STEPS 字段说明

```javascript
{
  id: Number,        // 序号，从 1 开始，页面内唯一
  selector: String,  // CSS 选择器，必须能被 document.querySelector() 找到
  type: String,      // 'new' | 'modified' | 'removed'
  title: String,     // 格式：「类型：元素名」，如「新增：导出按钮」
  desc: String,      // 一句话说明改了什么 + 为什么 / 权限 / 注意事项
}
```

---

## base.css Layer 5 扩展组件速查

> 所有类名在 `base.css` 中已定义，原样使用即可。

### 5a. 统计卡片 `kt-stat-card`

| 类名 | 说明 |
|------|------|
| `kt-stat-card` | 外层容器，白色卡片带阴影 |
| `kt-stat-card-label` | 指标标签（次要文字色） |
| `kt-stat-card-value` | 数值，大字号粗体 |
| `kt-stat-card-value.is-primary/success/danger/warning` | 数值颜色变体 |
| `kt-stat-card-footer` | 底部补充信息（分割线上方） |

### 5b. 描述列表 `kt-desc-list`

| 类名 | 说明 |
|------|------|
| `kt-desc-list` | 外层网格，默认双列 |
| `kt-desc-list.cols-1` | 单列模式 |
| `kt-desc-list.cols-3` | 三列模式 |
| `kt-desc-item` | 单个字段行 |
| `kt-desc-item.full-width` | 跨满整行（长文本/描述字段） |
| `kt-desc-label` | 字段名，灰色背景 120px |
| `kt-desc-value` | 字段值 |

### 5c. 通用卡片 `kt-card`

| 类名 | 说明 |
|------|------|
| `kt-card` | 容器，白色圆角卡片 |
| `kt-card-header` | 头部区域，含分割线 |
| `kt-card-title` | 标题文字 |
| `kt-card-body` | 内容区 |
| `kt-card-footer` | 底部区域，浅灰背景 |

### 5d. 空状态 `kt-empty`

| 类名 | 说明 |
|------|------|
| `kt-empty` | 居中容器 |
| `kt-empty-icon` | SVG 空表图标 |
| `kt-empty-text` | 主提示文字 |
| `kt-empty-sub` | 副提示文字 |

### 5e. 代码块 `kt-code-block`

单个 `<div class="kt-code-block">` 即可，内含 `<pre>` 格式的代码或 JSON 内容。

---

## 未覆盖组件的兜底优先级

```
1. Ant Design 自带（ant-* 类）
      ↓ 不够用时
2. Tailwind 工具类 + var(--kt-*) 变量
      ↓ 不够用时
3. style="" 内联 + var(--kt-*) 变量（禁止硬编码新色值）
      ↓ 仍不够用时
4. <style> 末尾追加 .kt-xxx 类（类名 kt- 开头，颜色用变量）
```

---

## CDN 引用（固定，不得更改版本）

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://at.alicdn.com/t/c/font_3649831_vn4l2gpuij.js"></script>
```
