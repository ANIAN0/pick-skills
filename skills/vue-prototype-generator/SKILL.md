---
name: vue-prototype-generator
description: |
  **确保使用此技能** 当用户需要「根据需求生成Vue UI原型」「创建Vue原型页面」「Vue需求转原型」「/vue-prototype」「Vue原型」「Ant Design Vue原型」或任何涉及Vue前端页面原型生成的请求时。

  本技能将需求文档转换为高保真 Vue 3 + Ant Design Vue 原型页面，输出**独立的 HTML 预览文件**（可直接在浏览器打开）。

  **触发关键词**: Vue原型、Ant Design Vue原型、生成Vue原型、Vue页面原型、Vue组件原型
---

# Vue Prototype Generator（Vue原型生成器）

## 目标

将需求文档转换为**高保真 Vue 原型页面**，输出**独立的 HTML 预览文件**：
- 使用 **Vue 3 + Ant Design Vue**（通过 CDN 引入）
- 生成可直接在浏览器中打开的 `.html` 文件
- 无需构建工具，双击即用
- 左侧：Vue 原型页面（固定宽度 1200px）
- 右侧：交互说明文档

## 工作流程

```
读取输入 → 评估页面清单 → 需求澄清 → 生成原型 → 输出文件
```

### Phase 1: 读取输入

**场景A（根据需求生成新原型）：**
- 用户未指定需求文档时，提示指定路径
- 已指定时，读取需求文档，提取：用户故事、功能列表、业务流程、数据结构

**场景B（旧原型改造）：**
- 读取旧 HTML 原型文件
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
- 新原型：`VuePrototype{页面名}.html`（大驼峰命名）
- 改造原型：`VuePrototype{页面名}V{版本}.html`

**重要原则（场景B）：**
- ✅ 生成新文件（新版本号）
- ✅ 保留旧文件（绝不覆盖）

## 场景B（旧原型改造）特殊处理

```
读取旧原型 → 分析结构 → 确认改造需求 → 生成新原型 → 保留旧文件
```

**关键原则：**
- **绝不直接修改旧文件**：生成全新 HTML 文件
- **保留旧文件**：作为备份和对比参考
- **新文件名区分**：使用递增版本号
- **风格继承**：从旧原型提取设计元素，保持视觉一致性

## 输出格式

脚本返回JSON结果：

```json
{
  "file_path": ".dev/prototype/VuePrototypeUserList.html",
  "file_name": "VuePrototypeUserList.html",
  "status": "success",
  "message": "生成成功",
  "page_info": {
    "name": "用户列表",
    "type": "list",
    "version": 1
  }
}
```

## HTML 文件结构

生成的 HTML 文件包含：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- Vue 3 CDN -->
  <script src="https://cdn.jsdmirror.com/npm/vue@3/dist/vue.global.js"></script>
  <!-- Ant Design Vue CSS -->
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/reset.css" />
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.css" />
  <!-- Ant Design Vue JS -->
  <script src="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.js"></script>
</head>
<body>
  <div class="prototype-container">
    <!-- 左侧：Vue原型页面（1200px） -->
    <div class="prototype-left" id="app">
      <!-- Vue 组件内容 -->
    </div>
    <!-- 右侧：说明文档 -->
    <div class="prototype-right">
      <!-- 交互说明 -->
    </div>
  </div>
  <script>
    // Vue 3 Composition API 代码
    const { createApp, ref, reactive } = Vue;
    const { message, Modal } = antd;
    // ... 组件逻辑
  </script>
</body>
</html>
```

## 页面类型支持

| 类型 | 说明 | 典型组件 |
|-----|------|---------|
| list | 列表页 | 搜索表单、表格、分页、操作按钮 |
| form | 表单页 | 表单字段、验证、提交/取消按钮 |
| detail | 详情页 | 描述列表、卡片、操作栏 |

## 约束与限制

- **Vue 3 + Composition API**：使用 `setup` 语法
- **Ant Design Vue 组件**：通过 CDN 引入
- **Mock 数据**：使用 `ref`/`reactive` 定义
- **可直接预览**：生成 HTML 文件，无需构建工具
- **左侧原型区域**：固定宽度 1200px
- **右侧说明区域**：自适应宽度

## 参考资源

- **设计规范**：`docs/design-guide.md` — Ant Design Vue 设计规范
- **输出格式**：`docs/output-format.md` — HTML 输出格式详细规范
- **页面生成脚本**：`scripts/generate_page.py` — 单页面生成
- **批量生成脚本**：`scripts/batch_generate.py` — 多页面并行生成

## 自检清单

- [ ] HTML 文件可在浏览器直接打开预览
- [ ] 使用 Vue 3 + Ant Design Vue（CDN 版本）
- [ ] 左侧原型区域宽度固定为 1200px
- [ ] 包含完整的交互功能（搜索、新增、编辑、删除等）
- [ ] 抽屉组件可正常打开/关闭
- [ ] Mock 数据正确显示
- [ ] 文件保存到 `.dev/prototype/` 目录
- [ ] 文件名符合大驼峰命名规范
- [ ] 场景B：旧文件已保留（未被覆盖）
