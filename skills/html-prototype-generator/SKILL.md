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
- **复刻模式**：读取已有 .vue 页面，转为HTML原型并在此基础上修改
- **需求模式**：根据需求文档生成全新原型页面
- **对话模式**：读取已有原型HTML，讨论并调整

## 设计核心

原型的核心价值是「与真实页面尽可能一致」。以下是必须遵守的设计规范：

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

### 典型CRUD页结构

每个列表页遵循：筛选栏 + 操作按钮 + 表格 + 抽屉 模式，对应项目的 tl 布局系统。

详细组件规范见 `docs/design-guide.md`。

## 工作流程

### Phase 1: 确定工作模式

| 用户意图 | 模式 | 第一步 |
|---------|------|-------|
| 提到已有页面路径、复制页面、在现有页面上加功能 | 复刻模式 | 读取 .vue 源文件 |
| 提到需求文档、新建页面 | 需求模式 | 读取需求文档 |
| 提到调整已有原型 | 对话模式 | 读取原型HTML |

### Phase 2A: 复刻模式

1. 用户提供 .vue 文件路径（或页面名称，在项目目录 `D:\workspace\Document\input\kt-agent-framework\admin_frontend\src\pages\` 中搜索）
2. 读取 .vue 主文件及其关联的 `data.ts`、子组件
3. 向用户展示分析结果（表格列、搜索字段、表单字段、状态枚举），确认需要修改/新增的部分
4. 基于分析结果生成HTML原型

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
- `<yc-status>` → 状态标签（使用项目配色，带圆点/背景色）
- `useDrawer` → JS 控制抽屉开关（openDrawer/closeDrawer）
- `useTable` → 静态表格数据 + 分页
- `hasButtonPerm()` → 移除权限判断，直接展示按钮
- API 调用 → 硬编码 Mock 数据

### Phase 2B: 需求模式

1. 读取需求文档，提取功能列表
2. 输出页面清单表格，等待用户确认

| 序号 | 页面名称 | 页面类型 | 功能描述 | 优先级 |
|-----|---------|---------|---------|-------|

3. 分轮次澄清需求（每轮最多3问）
4. 确认后生成HTML原型

**生成前检查现有页面：**
- 扫描 `.dev/prototype/` 目录查找现有原型
- 继承现有页面的配色和组件风格

### Phase 2C: 对话模式

1. 读取已有原型HTML文件
2. 与用户讨论需要调整的部分
3. 修改对应的HTML并保存为新版本

### Phase 3: 生成原型

每个页面调用 `scripts/generate_page.py` 生成：

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

多页面使用批量生成：

```bash
python scripts/batch_generate.py --config pages.json
```

### Phase 4: 文件输出

**输出目录：** `.dev/prototype/`

**命名规则：**
- 新原型：`prototype-{YYYYMMDD}-{页面名称}.html`
- 改造原型：`prototype-{YYYYMMDD}-{页面名称}-v{N}.html`

**页面结构：**
- 抽屉、弹窗等交互元素合并到主页面HTML中
- 通过 CSS `display:none` / JavaScript 控制显示隐藏
- 文档面板默认隐藏，点击「交互说明」按钮展开
- 保留旧文件（绝不覆盖）

## 页面类型

| 类型 | 说明 | 典型组件 |
|-----|------|---------|
| list | 列表页 | 筛选区、表格、分页、操作按钮、抽屉 |
| form | 表单页 | 表单字段、提交/取消 |
| detail | 详情页 | 信息分组、描述列表 |
| dashboard | 仪表盘 | 统计卡片、图表、快捷入口 |

## 约束

- **必须使用 Ant Design 4.x CSS**：`antd.min.css` CDN
- **必须应用项目配色**：#3e8dff 主色，非 Ant Design 默认 #1890ff
- **Tailwind 仅用于布局工具类**：flex、grid、间距，不用于组件样式
- **单文件输出**：每个HTML包含完整原型，可直接打开
- **Mock数据**：硬编码，无API调用
- **不使用 @apply**：CDN模式不生效

## 参考资源

- **设计规范**：`docs/design-guide.md` — 完整设计规范和组件HTML示例
- **输出格式**：`docs/output-format.md` — HTML输出格式详细规范
- **页面生成脚本**：`scripts/generate_page.py` — 单页面生成
- **批量生成脚本**：`scripts/batch_generate.py` — 多页面批量生成
- **复刻分析脚本**：`scripts/clone_page.py` — .vue 文件结构提取

**项目前端源码参考：** `D:\workspace\Document\input\kt-agent-framework\admin_frontend\src\`

## 自检清单

- [ ] HTML文件可在浏览器正常打开
- [ ] 配色使用项目色值（#3e8dff 主色等）
- [ ] 侧边栏 #1e202a，顶栏白色
- [ ] 使用 Ant Design 组件类名
- [ ] 抽屉/弹窗合并到主页面
- [ ] 文档面板可切换显示
- [ ] 文件保存到 `.dev/prototype/`
- [ ] 复刻模式：源页面结构已还原
- [ ] Mock数据合理
