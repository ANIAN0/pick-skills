# Vue Prototype Generator

基于需求生成 **Vue 3 + Element Plus** 高保真原型页面，输出可直接在浏览器中打开的独立 HTML 预览文件。

## 功能

- 生成独立的 `.html` 预览文件（双击即可在浏览器打开）
- 使用 Vue 3 + Element Plus（通过 CDN 引入）
- 使用 Vue 3 Composition API (`setup`)
- 支持列表页、表单页、详情页
- Mock 数据使用 `ref`/`reactive`
- 左侧原型（1200px）+ 右侧交互说明
- 抽屉、弹窗等交互组件合并到主页面

## 支持的页面类型

| 类型 | 说明 |
|-----|------|
| list | 列表页 - 搜索、表格、分页、抽屉编辑 |
| form | 表单页 - 表单验证、提交 |
| detail | 详情页 - 信息展示、操作栏 |

## 输出示例

生成的 HTML 文件可直接在浏览器中打开预览：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- Vue 3 + Element Plus CDN -->
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css" />
  <script src="https://unpkg.com/element-plus/dist/index.full.js"></script>
</head>
<body>
  <div class="prototype-container">
    <!-- 左侧：Vue 原型页面（1200px） -->
    <div class="prototype-left" id="app">
      <!-- Element Plus 组件 -->
      <el-container>
        <el-header>...</el-header>
        <el-container>
          <el-aside>...</el-aside>
          <el-main>...</el-main>
        </el-container>
      </el-container>
    </div>

    <!-- 右侧：交互说明文档 -->
    <div class="prototype-right">
      <div class="doc-section">
        <div class="doc-title">页面交互说明</div>
        ...
      </div>
    </div>
  </div>

  <script>
    const { createApp, ref, reactive } = Vue;
    const { ElMessage, ElMessageBox } = ElementPlus;

    const app = createApp({
      setup() {
        const tableData = ref([...]);
        const drawerVisible = ref(false);
        // ... 组件逻辑
        return { tableData, drawerVisible, ... };
      }
    });
    app.use(ElementPlus);
    app.mount('#app');
  </script>
</body>
</html>
```

## 文件结构

```
skills/vue-prototype-generator/
├── SKILL.md                      # Skill 定义文件
├── README.md                     # 说明文档
├── docs/
│   ├── design-guide.md           # Element Plus 设计规范
│   └── output-format.md          # HTML 输出格式规范
└── scripts/
    ├── generate_page.py          # 单页面生成脚本
    └── batch_generate.py         # 批量生成脚本
```

## 使用方式

### 单页面生成

```bash
python scripts/generate_page.py --input '{
  "page_name": "用户列表",
  "page_type": "list",
  "output_path": ".dev/prototype"
}'
```

### 批量生成

```bash
python scripts/batch_generate.py --config pages.json
```

## 输出目录

```
.dev/prototype/
├── VuePrototypeUserList.html     # 用户列表页
├── VuePrototypeUserForm.html     # 用户表单页
├── VuePrototypeUserDetail.html   # 用户详情页
└── ...
```

## 与 React 版本的区别

| 特性 | React 版本 | Vue 版本 |
|-----|-----------|---------|
| 输出格式 | `.html` 文件 | `.html` 文件 |
| UI 库 | Ant Design 4.x | Element Plus |
| 框架 | React 18 (CDN) | Vue 3 (CDN) |
| 语法 | React JSX + antd 类名 | Vue Composition API + Element Plus 组件 |
| 状态管理 | useState | ref/reactive |

## 特点

1. **无需构建工具**：生成的 HTML 文件双击即可在浏览器打开
2. **完整的交互功能**：搜索、新增、编辑、删除等操作均可交互
3. **抽屉/弹窗集成**：合并到主页面，使用 Vue 响应式数据控制显示
4. **右侧交互说明**：每个页面都包含详细的交互说明文档
5. **Element Plus 风格**：遵循 Element Plus 设计规范
