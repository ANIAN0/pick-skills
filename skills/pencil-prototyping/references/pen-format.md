# .pen 格式参考

程序化读写 `.pen` 时使用本参考，勿臆造结构。完整与权威定义见 [Pencil 开发者文档](https://docs.pencil.dev/for-developers/the-pen-format) 及该页末尾 TypeScript schema。

## 目录

1. [文档根结构](#文档根结构)
2. [对象通用规则](#对象通用规则)
3. [对象类型](#对象类型)
4. [布局](#布局)
5. [组件与实例](#组件与实例)
6. [变量与主题](#变量与主题)

---

## 文档根结构

- 根为 JSON 对象，必须包含：
  - `version`: 字符串
  - `children`: 顶层对象数组（每个元素须有 `id`、`type`、以及位置 `x`、`y`）
- 可选：`themes`、`imports`、`variables`

## 对象通用规则

- 每个对象必须有唯一 `id`（字符串，不可含 `/`）和 `type`（见下表）
- 顶层对象必须有 `x`、`y`（相对画布左上角）
- 父子关系：子对象在父的 `children` 数组中，子位置相对父左上角
- 可选：`name`、`reusable`、`theme`、`opacity`、`fill`、`stroke`、`effect` 等

## 对象类型

| type       | 说明           | 常用属性 |
|-----------|----------------|----------|
| `frame`   | 可含子元素的矩形 | `width`, `height`, `cornerRadius`, `children`, `layout`, `padding`, `clip`, `slot` |
| `group`   | 容器，可布局   | `children`, `layout`, `width`/`height` 可为 SizingBehavior |
| `rectangle` | 矩形         | `width`, `height`, `cornerRadius`, `fill`, `stroke` |
| `ellipse` | 椭圆/圆/弧     | `width`, `height`, `innerRadius`, `startAngle`, `sweepAngle` |
| `line`    | 线             | `width`, `height`, `stroke` |
| `path`    | 矢量路径       | `geometry`（SVG path）, `fill`, `stroke` |
| `polygon` | 正多边形       | `width`, `height`, `polygonCount`, `cornerRadius` |
| `text`    | 文本           | `content`, `fontSize`, `fontFamily`, `textGrowth`（`auto` \| `fixed-width` \| `fixed-width-height`）, `width`/`height` 需配合 `textGrowth` |
| `note`    | 注释           | `content`, `width`, `height` |
| `prompt`  | 提示块         | `content`, `model` |
| `context` | 上下文块       | `content` |
| `icon_font` | 图标         | `iconFontFamily`（如 `lucide`）, `icon`/`iconFontName` |
| `ref`     | 组件实例       | `ref`（目标组件 id）, `descendants`（覆盖子节点属性） |

## 布局

- 父对象可通过 `layout`（`"none"` \| `"vertical"` \| `"horizontal"`）、`padding`、`justifyContent`、`alignItems`、`gap` 控制子级排布
- 父为 flex 时，子的 `x`/`y` 会被忽略
- 尺寸：`width`/`height` 可为数字、或 `"fit_content"`/`"fill_container"` 等 SizingBehavior（可带 fallback，如 `"fit_content(100)"`）

## 组件与实例

- **组件**：对象设 `reusable: true` 即成为可复用组件
- **实例**：`type: "ref"`，`ref` 为组件 `id`，可带 `x`、`y` 及属性覆盖
- **覆盖子节点**：`descendants` 为对象，键为子节点 `id` 或 `"实例id/子id"` 路径，值为要覆盖的属性（不要写 `id`/`type`/`children`）；也可用完整新对象替换该子节点
- **插槽**：父组件内某 frame 设 `slot: ["组件id1", "组件id2"]` 表示此处可放入的推荐组件

## 变量与主题

- `variables`：键为名（如 `color.background`），值为 `{ type: "color"|"number"|"string"|"boolean", value: ... }`；属性可引用为 `"$变量名"`
- 主题：`themes` 定义轴（如 `mode: ["light","dark"]`）；变量 `value` 可为 `[{ value, theme: { mode: "dark" } }, ...]`；对象上 `theme: { mode: "dark" }` 使子树使用该主题

---

生成或解析 .pen 时，请严格按上述结构与官方 schema 编写，避免缺少必填字段或使用未定义类型。
