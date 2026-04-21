---
name: prototype-generator
description: |
  **确保使用此技能** 当用户需要「根据需求生成UI原型」「创建原型页面」「需求转原型」「/prototype」「改造原型」「优化页面原型」或任何涉及前端页面原型生成的请求时。

  本技能将需求文档转换为高保真HTML原型页面（左侧原型+右侧说明），采用Ant Design风格。

  **触发关键词**: 生成原型、创建原型、需求转原型、原型页面、画原型、/prototype、改造原型、重做原型
---

# Prototype Generator（原型生成器）

## 目标

将需求文档转换为**高保真HTML原型页面**，输出独立HTML文件：
- **左侧**：原型页面（固定宽度1200px，Ant Design风格）
- **右侧**：交互说明文档

## 工作流程

```
读取输入 → 评估页面清单 → 需求澄清 → 生成原型 → 输出文件
```

### Phase 1: 读取输入

**场景A（根据需求生成新原型）：**
- 用户未指定需求文档时，提示指定路径
- 已指定时，读取需求文档，提取：用户故事、功能列表、业务流程、数据结构

**场景B（旧原型改造）：**
- 读取旧原型HTML文件
- 分析页面结构、组件、交互逻辑
- 输出旧页面分析报告，与用户确认改造范围

### Phase 2: 评估页面清单

基于需求分析需要的前端页面，输出表格：

| 序号 | 页面名称 | 页面类型 | 功能描述 | 优先级 |
|-----|---------|---------|---------|-------|
| 1 | xxx列表 | list | 展示xxx数据 | P0 |
| 2 | xxx详情 | detail | 展示详细信息 | P0 |
| 3 | 新建xxx | form | 表单填写 | P0 |

**等待用户确认页面清单后再继续**

### Phase 3: 需求澄清

针对每个页面分轮次澄清（每轮最多3问）：

1. **布局与结构**：整体布局、模块划分、面包屑
2. **数据与展示**：表格列/表单字段/详情分组
3. **交互逻辑**：操作按钮、编辑方式（抽屉/弹窗/页面）、状态流转
4. **边界场景**：空数据、加载中、错误、权限控制

**停止条件**：用户确认达到90%理解度或明确表示「可以开始生成」

### Phase 4: 生成原型（调用脚本）

**生成前检查现有页面：**
- 扫描 `.dev/prototype/` 目录查找现有原型文件
- 读取最新的原型文件（按日期排序）
- 分析现有页面的样式、布局、配色、组件风格
- 在新原型中继承和还原现有页面的视觉效果

**每个页面调用 `scripts/generate_page.py` 生成：**

```bash
python scripts/generate_page.py --input '{
  "page_name": "用户列表",
  "page_type": "list",
  "scenario": "new",
  "output_path": ".dev/prototype",
  "clarification": {
    "layout": {...},
    "data": {...},
    "interactions": {...},
    "boundary": {...}
  }
}'
```

**多页面并行生成时使用：**

```bash
python scripts/batch_generate.py --config pages.json
```

### Phase 5: 文件输出

**输出目录：** `.dev/prototype/`

**命名规则：**
- 新原型：`prototype-{YYYYMMDD}-{页面名称}.html`
- 改造原型：`prototype-{YYYYMMDD}-{页面名称}-v{版本}.html`

**页面结构原则：**
- ✅ 抽屉、弹窗、子页面等交互统一合并到主页面 HTML 中
- ✅ 通过 CSS 控制显示/隐藏，或使用 JavaScript 切换内容
- ✅ 不再单独生成抽屉或子页面的独立 HTML 文件
- ✅ 保留旧文件（绝不覆盖）

## 页面结构规范

### 抽屉/弹窗合并原则

**不再单独生成抽屉 HTML，统一在主页面中实现：**

```html
<!-- 主页面结构 -->
<div class="ant-layout">
  <!-- 主内容区域 -->
  <main>...</main>

  <!-- 抽屉（初始隐藏，通过JS控制显示） -->
  <div id="drawer" class="drawer-container" style="display: none;">
    <div class="drawer-mask" onclick="closeDrawer()"></div>
    <div class="drawer-content">
      <!-- 抽屉表单或详情内容 -->
    </div>
  </div>

  <!-- 弹窗（初始隐藏） -->
  <div id="modal" class="modal-container" style="display: none;">
    <!-- 弹窗内容 -->
  </div>
</div>
```

**交互控制：**
- 使用 JavaScript 控制抽屉/弹窗的显示/隐藏
- 点击主页面按钮时打开对应的抽屉/弹窗
- 点击遮罩层或关闭按钮时隐藏

```
读取旧原型 → 分析结构 → 确认改造需求 → 生成新原型 → 保留旧文件
```

**关键原则：**
- **绝不直接修改旧文件**：生成全新HTML文件
- **保留旧文件**：作为备份和对比参考
- **新文件名区分**：使用新的日期或递增版本号
- **风格继承**：从旧原型提取设计元素，保持视觉一致性

## 输出格式

脚本返回JSON结果：

```json
{
  "file_path": "docs/prototype/prototype-20240325-user-list.html",
  "file_name": "prototype-20240325-user-list.html",
  "status": "success",
  "message": "生成成功",
  "page_info": {
    "name": "用户列表",
    "type": "list",
    "version": 1
  }
}
```

## 页面类型支持

| 类型 | 说明 | 典型组件 |
|-----|------|---------|
| list | 列表页 | 搜索区、表格、分页、操作按钮 |
| form | 表单页 | 表单字段、提交/取消按钮 |
| detail | 详情页 | 信息分组、卡片布局 |
| dashboard | 仪表盘 | 图表、统计卡片、快捷入口 |

## 约束与限制

- **必须使用真正的 Ant Design CSS**：引入 `antd.min.css`
- **使用原生 antd 类名**：如 `ant-btn`、`ant-input`、`ant-table`
- **Tailwind 仅用于页面级布局**：flex、grid、间距
- **固定宽度**：左侧原型区域必须固定1200px
- **Mock数据**：所有数据为硬编码，无真实API调用
- **单页面原型**：每个HTML文件只包含一个页面原型
- **抽屉弹窗合并**：所有抽屉、弹窗、子页面统一合并到主页面 HTML 中
- **参考现有页面**：生成时优先扫描 `.dev/prototype/` 中的现有页面，继承其风格

## 参考资源

- **设计规范**：`docs/design-guide.md` — Ant Design 设计规范
- **输出格式**：`docs/output-format.md` — HTML输出格式详细规范
- **页面生成脚本**：`scripts/generate_page.py` — 单页面生成
- **批量生成脚本**：`scripts/batch_generate.py` — 多页面并行生成

**现有原型参考位置：** `.dev/prototype/`

## 自检清单

- [ ] HTML文件可在浏览器正常打开
- [ ] 左侧原型区域宽度固定为1200px
- [ ] 使用Ant Design风格组件
- [ ] 使用真正的 antd.min.css（非Tailwind模拟）
- [ ] 所有数据为mock数据
- [ ] 右侧说明文档包含完整的交互描述
- [ ] 文件保存到 `.dev/prototype/` 目录
- [ ] 文件名符合命名规范
- [ ] 抽屉、弹窗等交互合并到主页面（无独立HTML）
- [ ] 场景B：旧文件已保留（未被覆盖）
- [ ] 新页面风格与现有页面保持一致
