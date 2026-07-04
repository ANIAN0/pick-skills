# 样式规则

## 固定资源

- `assets/base.css` 原样内联在 `<style>` 开头，不修改 Layer 1-5。
- `assets/guide-layer.js` 原样内联，不修改。
- CDN 版本沿用 `assets/page-skeleton.html` 中的引用，不自行更换。

## 颜色与图标

- 主色只用 `#3e8dff` 或 `var(--kt-primary)`。
- 禁止使用 `#1890ff` 作为主色。
- 禁止 emoji；图标使用 `anticon` 类名或首字母色块。
- 无对应 `anticon` 时用首字母色块，背景使用 `#3e8dff`。

常用图标：

| 菜单/场景 | 类名 |
|---|---|
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

## 状态标签

| 语义 | 类名 |
|---|---|
| 启用 / 在线 / 成功 | `kt-status kt-status-success` |
| 禁用 / 离线 / 错误 | `kt-status kt-status-danger` |
| 待审核 / 处理中 | `kt-status kt-status-warning` |
| 运行中 / 主要状态 | `kt-status kt-status-primary` |
| 未知 / 默认 | `kt-status kt-status-default` |

## 未定义样式处理优先级

1. Ant Design 自带组件类：按钮、输入框、下拉、日期、开关、单选、多选、表格、表单、弹窗、抽屉、标签页、步骤条、树形、上传、折叠、面包屑。
2. Tailwind 工具类组合布局和间距；颜色必须使用 `var(--kt-*)` 变量。
3. `style=""` 内联样式；颜色只能引用 `var(--kt-*)` 变量。
4. 在页面 `<style>` 末尾追加本页扩展类；类名必须以 `kt-` 开头，颜色使用 `var(--kt-*)` 变量。

绝对禁止：

- 修改 `base.css` Layer 1-5 的任何现有规则。
- 引入项目色板外的新硬编码颜色。
- 覆盖 Ant Design 组件内部结构样式。
- 为了视觉效果重写骨架或片段结构。
