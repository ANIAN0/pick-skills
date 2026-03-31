# Ant Design 原型设计规范

本规范专门用于指导原型生成，确保所有原型页面风格统一。**基于 Ant Design 4.x 官方样式**。

## 核心原则

**必须引入真正的 Ant Design CSS**，而不是用 Tailwind 模拟：

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
```

## 配色方案（Ant Design 4.x）

| 名称 | 色值 | CSS 变量 | 用途 |
|-----|------|---------|-----|
| Primary | `#1890ff` | `--primary-color` | 主按钮、链接、选中态 |
| Primary Hover | `#40a9ff` | - | 悬停状态 |
| Primary Active | `#096dd9` | - | 按下状态 |
| Success | `#52c41a` | `--success-color` | 成功状态、启用标签 |
| Warning | `#faad14` | `--warning-color` | 警告状态 |
| Error | `#f5222d` | `--error-color` | 错误状态、危险操作 |
| Info | `#1890ff` | - | 信息提示 |

### 中性色
| 名称 | 色值 | 用途 |
|-----|------|-----|
| Text Primary | `rgba(0, 0, 0, 0.85)` | 主要文字 |
| Text Secondary | `rgba(0, 0, 0, 0.45)` | 次要文字、提示 |
| Border | `#d9d9d9` | 边框 |
| Background | `#f0f2f5` | 页面背景 |
| Background Container | `#ffffff` | 容器背景 |

## HTML 头部模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {页面名称}</title>
  <!-- Ant Design 4.x 样式 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <!-- Tailwind CSS（仅用于布局工具类，不用于组件样式） -->
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* 仅用于页面级布局，不覆盖 antd 组件样式 */
    .prototype-container {
      width: 1200px;
      min-height: 100vh;
      background: #fff;
    }

    /* 右侧说明区域样式 */
    .doc-panel {
      flex: 1;
      background: #f5f5f5;
      padding: 24px;
      overflow-y: auto;
    }

    .doc-section {
      background: #fff;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 16px;
    }

    .doc-title {
      font-size: 18px;
      font-weight: 600;
      color: rgba(0, 0, 0, 0.85);
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #f0f0f0;
    }

    .doc-item {
      display: flex;
      gap: 12px;
      margin-bottom: 12px;
      font-size: 14px;
      line-height: 1.6;
    }

    .doc-label {
      font-weight: 500;
      color: rgba(0, 0, 0, 0.65);
      min-width: 100px;
      flex-shrink: 0;
    }

    .doc-content {
      color: rgba(0, 0, 0, 0.45);
    }
  </style>
</head>
```

## 组件使用规范

### 按钮（使用 antd 原生类）

```html
<!-- 主按钮 -->
<button class="ant-btn ant-btn-primary">
  <span>主要按钮</span>
</button>

<!-- 默认按钮 -->
<button class="ant-btn">
  <span>默认按钮</span>
</button>

<!-- 危险按钮 -->
<button class="ant-btn ant-btn-danger">
  <span>删除</span>
</button>

<!-- 带图标的按钮 -->
<button class="ant-btn ant-btn-primary">
  <span class="anticon anticon-plus"></span>
  <span>新增</span>
</button>
```

### 输入框

```html
<input class="ant-input" placeholder="请输入">

<!-- 带前缀的输入框 -->
<span class="ant-input-affix-wrapper">
  <span class="ant-input-prefix">
    <span class="anticon anticon-search"></span>
  </span>
  <input class="ant-input" placeholder="搜索">
</span>
```

### 下拉选择

```html
<div class="ant-select ant-select-single" style="width: 200px;">
  <div class="ant-select-selector">
    <span class="ant-select-selection-search">
      <input class="ant-select-selection-search-input" style="opacity: 0;">
    </span>
    <span class="ant-select-selection-item">全部状态</span>
  </div>
</div>
```

### 表格

```html
<div class="ant-table-wrapper">
  <div class="ant-spin-nested-loading">
    <div class="ant-spin-container">
      <div class="ant-table">
        <div class="ant-table-container">
          <div class="ant-table-content">
            <table style="table-layout: auto;">
              <thead class="ant-table-thead">
                <tr>
                  <th class="ant-table-cell">列标题</th>
                </tr>
              </thead>
              <tbody class="ant-table-tbody">
                <tr class="ant-table-row">
                  <td class="ant-table-cell">数据内容</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 标签

```html
<!-- 状态标签 - 启用 -->
<span class="ant-tag ant-tag-success">启用</span>

<!-- 状态标签 - 禁用 -->
<span class="ant-tag ant-tag-error">禁用</span>

<!-- 状态标签 - 待审核 -->
<span class="ant-tag ant-tag-warning">待审核</span>

<!-- 状态标签 - 默认 -->
<span class="ant-tag">默认</span>
```

### 卡片

```html
<div class="ant-card">
  <div class="ant-card-head">
    <div class="ant-card-head-wrapper">
      <div class="ant-card-head-title">卡片标题</div>
    </div>
  </div>
  <div class="ant-card-body">
    卡片内容
  </div>
</div>
```

### 抽屉

```html
<div class="ant-drawer ant-drawer-right" style="position: fixed; top: 0; right: 0; width: 520px; z-index: 1000;">
  <div class="ant-drawer-mask"></div>
  <div class="ant-drawer-content-wrapper" style="width: 520px;">
    <div class="ant-drawer-content">
      <div class="ant-drawer-wrapper-body">
        <div class="ant-drawer-header">
          <div class="ant-drawer-title">抽屉标题</div>
          <button class="ant-drawer-close">
            <span class="anticon anticon-close"></span>
          </button>
        </div>
        <div class="ant-drawer-body">
          抽屉内容
        </div>
        <div class="ant-drawer-footer" style="border-top: 1px solid #f0f0f0; padding: 16px 24px; text-align: right;">
          <button class="ant-btn" style="margin-right: 8px;">取消</button>
          <button class="ant-btn ant-btn-primary">确定</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 分页

```html
<ul class="ant-pagination">
  <li class="ant-pagination-prev ant-pagination-disabled">
    <button class="ant-pagination-item-link" disabled>
      <span class="anticon anticon-left"></span>
    </button>
  </li>
  <li class="ant-pagination-item ant-pagination-item-1 ant-pagination-item-active">
    <a>1</a>
  </li>
  <li class="ant-pagination-item ant-pagination-item-2">
    <a>2</a>
  </li>
  <li class="ant-pagination-next">
    <button class="ant-pagination-item-link">
      <span class="anticon anticon-right"></span>
    </button>
  </li>
</ul>
```

## 布局模式

### 标准后台布局

```html
<div class="ant-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <header class="ant-layout-header" style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08);">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">L</div>
      <span style="font-size: 18px; font-weight: 500;">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <div style="width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%;"></div>
    </div>
  </header>

  <div class="ant-layout" style="display: flex;">
    <!-- 侧边栏 -->
    <aside class="ant-layout-sider" style="background: #001529; width: 200px; flex-shrink: 0;">
      <ul class="ant-menu ant-menu-dark ant-menu-root" style="background: #001529;">
        <li class="ant-menu-item" style="padding-left: 24px;">
          <span class="anticon anticon-home"></span>
          <span style="margin-left: 10px;">首页</span>
        </li>
        <li class="ant-menu-item ant-menu-item-selected" style="background: #1890ff; padding-left: 24px;">
          <span class="anticon anticon-table"></span>
          <span style="margin-left: 10px;">用户管理</span>
        </li>
      </ul>
    </aside>

    <!-- 主内容 -->
    <main class="ant-layout-content" style="margin: 24px; padding: 24px; background: #fff; min-height: 280px;">
      内容区域
    </main>
  </div>
</div>
```

## 列表页完整示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>原型 - 用户列表</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .prototype-container { width: 1200px; min-height: 100vh; background: #f0f2f5; }
    .doc-panel { flex: 1; background: #f5f5f5; padding: 24px; overflow-y: auto; }
  </style>
</head>
<body class="bg-gray-100">
  <div class="flex h-screen">
    <!-- 左侧原型 -->
    <div class="prototype-container overflow-auto">
      <div class="ant-layout" style="min-height: 100vh;">
        <!-- 顶栏 -->
        <header class="ant-layout-header" style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">L</div>
            <span style="font-size: 18px; font-weight: 500;">系统后台</span>
          </div>
          <div style="display: flex; align-items: center; gap: 16px;">
            <span style="color: rgba(0,0,0,0.65);">管理员</span>
          </div>
        </header>

        <div class="ant-layout" style="display: flex;">
          <!-- 侧边栏 -->
          <aside class="ant-layout-sider" style="background: #001529; width: 200px;">
            <ul class="ant-menu ant-menu-dark ant-menu-root">
              <li class="ant-menu-item ant-menu-item-selected" style="background: #1890ff;">
                <span>用户管理</span>
              </li>
            </ul>
          </aside>

          <!-- 主内容 -->
          <main style="flex: 1; padding: 24px;">
            <!-- 面包屑 -->
            <div class="ant-breadcrumb" style="margin-bottom: 16px;">
              <span class="ant-breadcrumb-link">首页</span>
              <span class="ant-breadcrumb-separator">/</span>
              <span class="ant-breadcrumb-link">用户管理</span>
            </div>

            <h1 style="font-size: 20px; font-weight: 500; margin-bottom: 24px;">用户列表</h1>

            <!-- 筛选卡 -->
            <div class="ant-card" style="margin-bottom: 24px;">
              <div class="ant-card-body">
                <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                  <input class="ant-input" placeholder="用户名" style="width: 200px;">
                  <input class="ant-input" placeholder="邮箱" style="width: 200px;">
                  <div class="ant-select" style="width: 120px;">
                    <div class="ant-select-selector">
                      <span class="ant-select-selection-item">全部状态</span>
                    </div>
                  </div>
                  <button class="ant-btn ant-btn-primary">搜索</button>
                  <button class="ant-btn">重置</button>
                </div>
              </div>
            </div>

            <!-- 操作栏 -->
            <div style="margin-bottom: 16px;">
              <button class="ant-btn ant-btn-primary">
                <span class="anticon anticon-plus"></span>
                <span>新增用户</span>
              </button>
            </div>

            <!-- 表格 -->
            <div class="ant-card">
              <div class="ant-table-wrapper">
                <div class="ant-spin-container">
                  <div class="ant-table">
                    <div class="ant-table-container">
                      <div class="ant-table-content">
                        <table>
                          <thead class="ant-table-thead">
                            <tr>
                              <th class="ant-table-cell">用户名</th>
                              <th class="ant-table-cell">邮箱</th>
                              <th class="ant-table-cell">状态</th>
                              <th class="ant-table-cell">操作</th>
                            </tr>
                          </thead>
                          <tbody class="ant-table-tbody">
                            <tr class="ant-table-row">
                              <td class="ant-table-cell">admin</td>
                              <td class="ant-table-cell">admin@example.com</td>
                              <td class="ant-table-cell"><span class="ant-tag ant-tag-success">启用</span></td>
                              <td class="ant-table-cell">
                                <a style="color: #1890ff;">编辑</a>
                                <span style="margin: 0 8px; color: #d9d9d9;">|</span>
                                <a style="color: #ff4d4f;">删除</a>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>

    <!-- 右侧说明 -->
    <div class="doc-panel">
      <!-- 说明内容 -->
    </div>
  </div>
</body>
</html>
```

## 重要提醒

1. **必须使用 `antd.min.css`**，这是保证风格一致的关键
2. **使用原生 antd 类名**：`ant-btn`、`ant-input`、`ant-table` 等
3. **Tailwind 仅用于**：页面级布局（flex、grid、间距等），不用于组件样式
4. **不要使用 `@apply`**：在 CDN 模式下可能不生效
5. **颜色使用 Ant Design 标准色**：`#1890ff` 为主色
