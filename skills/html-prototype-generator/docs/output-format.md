# 原型HTML输出格式规范

## 文件输出位置

**默认输出目录：** `.dev/prototype/`

## 文件命名

- 新原型：`prototype-{YYYYMMDD}-{页面名称}.html`
- 改造原型：`prototype-{YYYYMMDD}-{页面名称}-v{N}.html`
- 示例：`prototype-20260506-role-list.html`、`prototype-20260506-role-list-v2.html`

## HTML 文件结构

每个HTML文件必须包含完整原型，可直接在浏览器打开。

### 必需的 HEAD 部分

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {页面名称}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- 项目配色覆盖 + 自定义组件样式 -->
  <style>/* 见 design-guide.md 中的完整样式 */</style>
</head>
```

### BODY 结构

```
<body>
  <div class="ant-layout">               ← 整体布局
    <aside>                               ← 深色侧边栏 (固定定位)
    <div>                                 ← 右侧区域
      <header>                            ← 白色顶栏 (sticky)
      <main>                              ← 内容区 (#f0f2f5 背景)
        <div class="tl-filter">           ← 筛选区
        <div class="tl-table">            ← 表格区
      </main>
    </div>
  </div>

  <div id="drawer">                       ← 抽屉 (display:none)
  <div id="confirmModal">                 ← 确认弹窗 (display:none)

  <button class="doc-toggle">             ← 文档面板切换按钮
  <div class="doc-panel">                 ← 文档面板 (默认隐藏)

  <script>                                ← 交互脚本
</body>
```

## 文档面板（可切换）

文档面板默认隐藏在右侧，点击固定在右侧的「交互说明」按钮展开。

### 实现方式

```html
<!-- 切换按钮，固定在视口右侧中间 -->
<button class="doc-toggle" onclick="toggleDoc()">交互说明</button>

<!-- 文档面板，默认 right: -400px 隐藏 -->
<div class="doc-panel" id="docPanel">
  <div class="doc-section">
    <div class="doc-title">页面说明</div>
    <!-- 页面功能描述 -->
  </div>
  <div class="doc-section">
    <div class="doc-title">交互逻辑</div>
    <!-- 各操作的行为说明 -->
  </div>
  <div class="doc-section">
    <div class="doc-title">字段说明</div>
    <!-- 表格列、表单字段说明 -->
  </div>
</div>
```

### 文档内容要求

| 板块 | 内容 |
|------|------|
| 页面说明 | 一句话概述页面用途 |
| 交互逻辑 | 每个按钮/操作的行为描述 |
| 字段说明 | 表格列含义、表单字段校验规则 |
| 状态说明 | 各状态值对应的颜色和含义 |
| 边界场景 | 空数据、加载中、错误等场景处理 |

## 抽屉/弹窗合并规则

所有抽屉和弹窗统一合并到主页面HTML中：

1. **抽屉**：一个 `<div id="drawer">` 容器，通过 JS 切换标题和内容
   - `openDrawer(title, mode)` - 打开抽屉，mode 可为 add/edit/detail
   - `closeDrawer()` - 关闭抽屉
   - detail 模式：只显示「返回」按钮，表单字段 disabled
   - add/edit 模式：显示「取消」和「保存」按钮

2. **确认弹窗**：一个 `<div id="confirmModal">` 容器
   - `openConfirmModal()` - 打开确认弹窗
   - `closeConfirmModal()` - 关闭确认弹窗

3. **多状态抽屉**：如果页面需要多种抽屉内容（如新增和编辑表单不同），通过 JS 动态切换内部 HTML

## Mock 交互脚本

每个HTML文件底部必须包含交互脚本：

```javascript
<script>
// 抽屉控制
function openDrawer(title, mode) {
  document.getElementById('drawer').style.display = 'block';
  document.getElementById('drawerTitle').textContent = title;
  const footer = document.getElementById('drawerFooter');
  if (mode === 'detail') {
    footer.innerHTML = '<button class="ant-btn" onclick="closeDrawer()">返回</button>';
  } else {
    footer.innerHTML = '<button class="ant-btn" style="margin-right:8px" onclick="closeDrawer()">取消</button><button class="ant-btn ant-btn-primary">保存</button>';
  }
}
function closeDrawer() {
  document.getElementById('drawer').style.display = 'none';
}

// 确认弹窗
function openConfirmModal() {
  document.getElementById('confirmModal').style.display = 'block';
}
function closeConfirmModal() {
  document.getElementById('confirmModal').style.display = 'none';
}

// 文档面板
function toggleDoc() {
  document.getElementById('docPanel').classList.toggle('open');
}

// 通用操作
function mockAction(action, data) {
  console.log('[Mock]', action, data);
}
</script>
```

## 复刻模式输出

复刻模式生成的HTML应尽可能还原源 .vue 页面的完整结构：

1. **筛选区**：根据 searchSchema 生成所有搜索字段
2. **操作按钮**：保留原有按钮，移除权限判断（`hasButtonPerm` 直接为 true）
3. **表格列**：根据 columns 配置生成所有列
4. **状态标签**：使用 `.kt-status` 替代 `<yc-status>`
5. **抽屉**：根据 EditForm 组件生成表单
6. **详情模式**：详情展示替代为描述列表

## 自检规则

1. HTML 可直接在浏览器打开，无控制台报错
2. 配色使用项目色值（#3e8dff 主色）
3. 侧边栏 #1e202a
4. 抽屉/弹窗可正常打开关闭
5. 文档面板可切换显示
6. 文件保存到 `.dev/prototype/`
7. 不覆盖已有文件
