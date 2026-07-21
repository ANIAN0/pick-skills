# KT Admin 默认模板样式规则

仅在原型选择本 skill 自带的 KT Admin 模板时使用。项目已有设计依据时服从项目规范，不用本文件覆盖项目样式。

## 默认资源

- 复制 `assets/base.css` 或 `assets/page-skeleton.html` 使用，不修改 skill 内的源文件。
- 使用默认骨架时沿用其中的 CDN 依赖；依赖无法访问时应改为可离线运行的方案并完成验证。

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

## 未定义样式处理

优先复用模板已有组件类和 `var(--kt-*)` 颜色变量。在原型输出中增加当前页面确实需要的布局或组件样式，并保持与默认模板一致；不要为了迁就现有片段省略需求中的重要结构。

使用默认模板时：

- 不修改 `assets/` 中的任何源文件，只修改复制到原型目录中的内容。
- 不随意引入与 KT Admin 风格冲突的色板或组件外观。
- 扩展骨架或片段时保持页面可离线打开、交互可用且视觉连贯。
