# KT Admin 原型设计规范

本规范确保原型页面与 kt-agent-framework 管理后台风格一致。

## 1. 技术栈

- **Ant Design 4.x CSS**：`https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css`
- **Tailwind CSS**：`https://cdn.tailwindcss.com`（仅用于布局工具类）
- 纯 HTML/CSS/JavaScript，无框架依赖

## 2. 配色方案

### 主色与状态色（来自项目 const.less）

| 名称 | 色值 | 背景色 | 用途 |
|-----|------|-------|------|
| Primary | `#3e8dff` | `#d6e7ff` | 主按钮、链接、选中态、主标签 |
| Success | `#00e5c7` | `#effffb` | 启用、在线、成功状态 |
| Danger | `#ff8b78` | `#fff5f3` | 删除、错误、禁用状态 |
| Warning | `#ffb71d` | `#fff2d6` | 警告、待审核状态 |
| Default | `#bfc6d1` | `#f5f6f9` | 默认、未知状态 |
| Ant Blue | `#1890ff` | - | Ant Design 默认主色（仅用于组件内部hover等） |

### 中性色

| 名称 | 色值 | 用途 |
|-----|------|------|
| 侧边栏背景 | `#1e202a` | 左侧深色导航 |
| 侧边栏选中 | `#3e8dff` | 菜单项选中态 |
| 内容区背景 | `#f0f2f5` | 页面主背景 |
| 顶栏背景 | `#fff` | 顶部栏 |
| 文字主要 | `rgba(0,0,0,0.85)` | 标题、正文 |
| 文字次要 | `rgba(0,0,0,0.65)` | 描述、辅助文字 |
| 文字提示 | `rgba(0,0,0,0.45)` | placeholder、提示 |
| 边框 | `#f0f0f0` | 分割线、卡片边框 |
| 分割线 | `#e8e8e8` | 较明显的分割 |

## 3. HTML 头部模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {页面名称}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --kt-primary: #3e8dff;
      --kt-primary-bg: #d6e7ff;
      --kt-success: #00e5c7;
      --kt-success-bg: #effffb;
      --kt-danger: #ff8b78;
      --kt-danger-bg: #fff5f3;
      --kt-warning: #ffb71d;
      --kt-warning-bg: #fff2d6;
      --kt-default: #bfc6d1;
      --kt-default-bg: #f5f6f9;
      --kt-sidebar: #1e202a;
      --kt-content-bg: #f0f2f5;
    }

    /* 覆盖 Ant Design 主色 */
    .ant-btn-primary { background-color: #3e8dff; border-color: #3e8dff; }
    .ant-btn-primary:hover { background-color: #5ea3ff; border-color: #5ea3ff; }
    .ant-btn-primary:active { background-color: #2a75d4; border-color: #2a75d4; }
    a, .ant-btn-link { color: #3e8dff; }
    a:hover, .ant-btn-link:hover { color: #5ea3ff; }

    /* yc-status 状态标签 */
    .kt-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 0 8px;
      height: 24px;
      border-radius: 4px;
      font-size: 12px;
      line-height: 24px;
    }
    .kt-status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      display: inline-block;
    }
    .kt-status-primary { background: #d6e7ff; color: #3e8dff; }
    .kt-status-primary .kt-status-dot { background: #3e8dff; }
    .kt-status-success { background: #effffb; color: #00a89a; }
    .kt-status-success .kt-status-dot { background: #00e5c7; }
    .kt-status-danger { background: #fff5f3; color: #d4634f; }
    .kt-status-danger .kt-status-dot { background: #ff8b78; }
    .kt-status-warning { background: #fff2d6; color: #c99200; }
    .kt-status-warning .kt-status-dot { background: #ffb71d; }
    .kt-status-default { background: #f5f6f9; color: #8c95a6; }
    .kt-status-default .kt-status-dot { background: #bfc6d1; }

    /* TL 布局系统 */
    .tl-main { flex: 1; overflow: auto; display: flex; flex-direction: column; gap: 0; }
    .tl-filter {
      background: #fff;
      padding: 16px 24px;
      border-radius: 8px;
      margin-bottom: 16px;
    }
    .tl-filter-left {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
    }
    .tl-table {
      background: #fff;
      padding: 24px;
      padding-top: 16px;
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }

    /* 文档面板 */
    .doc-toggle {
      position: fixed;
      top: 50%;
      right: 0;
      transform: translateY(-50%);
      z-index: 1001;
      background: #3e8dff;
      color: #fff;
      border: none;
      padding: 12px 4px;
      border-radius: 4px 0 0 4px;
      cursor: pointer;
      writing-mode: vertical-rl;
      font-size: 13px;
      letter-spacing: 2px;
      transition: right 0.3s;
    }
    .doc-panel {
      position: fixed;
      top: 0;
      right: -400px;
      width: 400px;
      height: 100vh;
      background: #fafafa;
      border-left: 1px solid #e8e8e8;
      padding: 24px;
      overflow-y: auto;
      z-index: 1000;
      transition: right 0.3s;
    }
    .doc-panel.open { right: 0; }
    .doc-panel .doc-section {
      background: #fff;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
    }
    .doc-panel .doc-title {
      font-size: 15px;
      font-weight: 600;
      color: rgba(0,0,0,0.85);
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #f0f0f0;
    }

    /* 表格 bordered small */
    .kt-table .ant-table { font-size: 13px; }
    .kt-table .ant-table-thead > tr > th { padding: 10px 12px; font-weight: 600; }
    .kt-table .ant-table-tbody > tr > td { padding: 10px 12px; }
    .kt-table .ant-table-thead > tr > th,
    .kt-table .ant-table-tbody > tr > td { border-right: 1px solid #f0f0f0; }
    .kt-table .ant-table-thead > tr > th:last-child,
    .kt-table .ant-table-tbody > tr > td:last-child { border-right: none; }
    .kt-table .ant-table-container { border: 1px solid #f0f0f0; border-radius: 4px; }

    /* 操作按钮组 */
    .action-group { display: inline-flex; align-items: center; gap: 0; }
    .action-group .ant-btn-link { padding: 0 4px; height: auto; }
    .action-group .action-divider { width: 1px; height: 14px; background: #e8e8e8; margin: 0 4px; }
  </style>
</head>
```

## 4. 整体布局结构

模拟项目 layout 的侧边栏 + 顶栏 + 内容区。

```html
<body>
<div class="ant-layout" style="min-height: 100vh;">
  <!-- 侧边栏 -->
  <aside style="background: #1e202a; width: 220px; flex-shrink: 0; position: fixed; left: 0; top: 0; bottom: 0; z-index: 100;">
    <!-- Logo -->
    <div style="height: 56px; display: flex; align-items: center; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.08);">
      <span style="color: #fff; font-size: 16px; font-weight: 600;">KT Agent</span>
    </div>
    <!-- 菜单 -->
    <ul style="list-style: none; padding: 8px 0; margin: 0;">
      <li style="padding: 10px 20px; color: rgba(255,255,255,0.65); cursor: pointer; font-size: 14px;">
        <span style="margin-right: 10px;">🏠</span>首页
      </li>
      <li style="padding: 10px 20px; color: rgba(255,255,255,0.65); cursor: pointer; font-size: 14px;">
        <span style="margin-right: 10px;">🤖</span>Agent 管理
      </li>
      <li style="padding: 10px 20px; background: #3e8dff; color: #fff; cursor: pointer; font-size: 14px; border-radius: 4px; margin: 0 8px;">
        <span style="margin-right: 10px;">📋</span>当前页面
      </li>
    </ul>
  </aside>

  <!-- 右侧 -->
  <div style="margin-left: 220px; flex: 1; display: flex; flex-direction: column;">
    <!-- 顶栏 -->
    <header style="height: 56px; background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); position: sticky; top: 0; z-index: 99;">
      <span style="font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85);">页面标题</span>
      <div style="display: flex; align-items: center; gap: 16px;">
        <span style="color: rgba(0,0,0,0.65); font-size: 14px;">管理员</span>
      </div>
    </header>

    <!-- 内容区 -->
    <main style="flex: 1; padding: 16px; background: #f0f2f5; overflow: auto;">
      <!-- 页面内容 -->
    </main>
  </div>
</div>
</body>
```

## 5. 组件规范

### yc-status 状态标签

替代项目的 `<yc-status>` 组件，使用自定义 `.kt-status` 类：

```html
<!-- 启用/成功 -->
<span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span>

<!-- 禁用/危险 -->
<span class="kt-status kt-status-danger"><span class="kt-status-dot"></span>禁用</span>

<!-- 警告 -->
<span class="kt-status kt-status-warning"><span class="kt-status-dot"></span>待审核</span>

<!-- Primary -->
<span class="kt-status kt-status-primary"><span class="kt-status-dot"></span>运行中</span>

<!-- Default -->
<span class="kt-status kt-status-default"><span class="kt-status-dot"></span>未知</span>
```

### yc-form 筛选表单

替代项目的 `<yc-form>` 搜索表单。每个字段根据 schema 生成对应输入控件：

```html
<div class="tl-filter">
  <div class="tl-filter-left">
    <!-- 输入框 -->
    <input class="ant-input" placeholder="请输入关键词" style="width: 200px;">

    <!-- 下拉选择 -->
    <div class="ant-select ant-select-single" style="width: 160px;">
      <div class="ant-select-selector">
        <span class="ant-select-selection-item">全部状态</span>
      </div>
    </div>

    <!-- 日期选择 -->
    <span class="ant-picker" style="width: 220px;">
      <span class="ant-picker-input">
        <input readonly placeholder="选择日期" style="border: none; outline: none; width: 100%;">
      </span>
    </span>

    <!-- 操作按钮 -->
    <button class="ant-btn ant-btn-primary">查询</button>
    <button class="ant-btn">重置</button>
    <button class="ant-btn ant-btn-primary">新增</button>
  </div>
</div>
```

### 表格（bordered + small）

使用 `.kt-table` 容器，与项目 `@kt/unity-antd-table` 全局配置一致：

```html
<div class="tl-table kt-table">
  <div class="ant-table-wrapper">
    <div class="ant-table">
      <div class="ant-table-container">
        <div class="ant-table-content">
          <table style="table-layout: auto; width: 100%;">
            <thead class="ant-table-thead">
              <tr>
                <th class="ant-table-cell" style="text-align: center; width: 60px;">序号</th>
                <th class="ant-table-cell">名称</th>
                <th class="ant-table-cell">状态</th>
                <th class="ant-table-cell" style="text-align: center; width: 180px;">操作</th>
              </tr>
            </thead>
            <tbody class="ant-table-tbody">
              <tr class="ant-table-row">
                <td class="ant-table-cell" style="text-align: center;">1</td>
                <td class="ant-table-cell">示例数据</td>
                <td class="ant-table-cell">
                  <span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span>
                </td>
                <td class="ant-table-cell" style="text-align: center;">
                  <div class="action-group">
                    <a style="color: #3e8dff; cursor: pointer;">详情</a>
                    <span class="action-divider"></span>
                    <a style="color: #3e8dff; cursor: pointer;">编辑</a>
                    <span class="action-divider"></span>
                    <a style="color: #ff4d4f; cursor: pointer;">删除</a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- 分页 -->
  <div style="padding: 16px 0 0; display: flex; justify-content: flex-end;">
    <ul class="ant-pagination">
      <li class="ant-pagination-total-text">共 50 条</li>
      <li class="ant-pagination-prev ant-pagination-disabled"><button class="ant-pagination-item-link" disabled>&lt;</button></li>
      <li class="ant-pagination-item ant-pagination-item-active"><a>1</a></li>
      <li class="ant-pagination-item"><a>2</a></li>
      <li class="ant-pagination-item"><a>3</a></li>
      <li class="ant-pagination-next"><button class="ant-pagination-item-link">&gt;</button></li>
    </ul>
  </div>
</div>
```

### 抽屉

模拟 `<tl-drawer>` 组件，宽度通常为 980px 或 600px：

```html
<div id="drawer" style="display: none;">
  <div class="ant-drawer" style="position: fixed; top: 0; right: 0; bottom: 0; z-index: 1000;">
    <div class="ant-drawer-mask" onclick="closeDrawer()" style="background: rgba(0,0,0,0.45);"></div>
    <div class="ant-drawer-content-wrapper" style="width: 980px; position: fixed; top: 0; right: 0; bottom: 0;">
      <div class="ant-drawer-content">
        <div class="ant-drawer-wrapper-body" style="display: flex; flex-direction: column; height: 100%;">
          <div class="ant-drawer-header" style="padding: 16px 24px; border-bottom: 1px solid #f0f0f0;">
            <div class="ant-drawer-title" style="font-size: 16px; font-weight: 500;">抽屉标题</div>
            <button class="ant-drawer-close" onclick="closeDrawer()" style="border: none; background: none; font-size: 16px; cursor: pointer;">✕</button>
          </div>
          <div class="ant-drawer-body" style="flex: 1; overflow: auto; padding: 24px;">
            <!-- 表单或详情内容 -->
          </div>
          <div class="ant-drawer-footer" style="border-top: 1px solid #f0f0f0; padding: 12px 24px; text-align: right;">
            <button class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
            <button class="ant-btn ant-btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 确认弹窗

```html
<div id="confirmModal" style="display: none;">
  <div class="ant-modal-mask" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0; z-index: 1001;"></div>
  <div class="ant-modal-wrap" style="position: fixed; inset: 0; z-index: 1002; display: flex; align-items: center; justify-content: center;">
    <div class="ant-modal" style="width: 420px;">
      <div class="ant-modal-content">
        <button class="ant-modal-close" onclick="closeConfirmModal()" style="border: none; background: none; font-size: 16px; cursor: pointer;">✕</button>
        <div class="ant-modal-header"><div class="ant-modal-title">确认删除</div></div>
        <div class="ant-modal-body" style="padding: 24px;">
          <p>确定要删除此记录吗？此操作不可撤销。</p>
        </div>
        <div class="ant-modal-footer">
          <button class="ant-btn" onclick="closeConfirmModal()">取消</button>
          <button class="ant-btn ant-btn-primary" style="background: #ff4d4f; border-color: #ff4d4f;">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 表单（抽屉内）

模拟 `<a-form layout="vertical">` + `<a-form-item>`：

```html
<form class="ant-form ant-form-vertical">
  <div class="ant-form-item">
    <div class="ant-form-item-label"><label><span style="color: #ff4d4f; margin-right: 4px;">*</span>名称</label></div>
    <div class="ant-form-item-control">
      <div class="ant-form-item-control-input">
        <input class="ant-input" placeholder="请输入名称" style="max-width: 400px;">
      </div>
    </div>
  </div>

  <div class="ant-form-item">
    <div class="ant-form-item-label"><label>描述</label></div>
    <div class="ant-form-item-control">
      <div class="ant-form-item-control-input">
        <textarea class="ant-input" placeholder="请输入描述" rows="3" style="max-width: 400px; resize: vertical;"></textarea>
      </div>
    </div>
  </div>

  <div class="ant-form-item">
    <div class="ant-form-item-label"><label>状态</label></div>
    <div class="ant-form-item-control">
      <div class="ant-select ant-select-single" style="width: 200px;">
        <div class="ant-select-selector">
          <span class="ant-select-selection-item">请选择</span>
        </div>
      </div>
    </div>
  </div>
</form>
```

### 详情描述列表

模拟 `<a-descriptions>` 样式：

```html
<div style="display: grid; grid-template-columns: 120px 1fr 120px 1fr; gap: 16px 0;">
  <div style="color: rgba(0,0,0,0.45); font-size: 13px;">名称</div>
  <div style="color: rgba(0,0,0,0.85); font-size: 14px;">示例数据</div>
  <div style="color: rgba(0,0,0,0.45); font-size: 13px;">状态</div>
  <div><span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span></div>
  <div style="color: rgba(0,0,0,0.45); font-size: 13px;">创建时间</div>
  <div style="color: rgba(0,0,0,0.65); font-size: 14px;">2024-03-25 10:30:00</div>
  <div style="color: rgba(0,0,0,0.45); font-size: 13px;">描述</div>
  <div style="color: rgba(0,0,0,0.65); font-size: 14px;">这是一段描述信息</div>
</div>
```

## 6. 完整列表页示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - 角色列表</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root { --kt-primary: #3e8dff; --kt-primary-bg: #d6e7ff; --kt-success: #00e5c7; --kt-success-bg: #effffb; --kt-danger: #ff8b78; --kt-danger-bg: #fff5f3; --kt-warning: #ffb71d; --kt-warning-bg: #fff2d6; --kt-default: #bfc6d1; --kt-default-bg: #f5f6f9; --kt-sidebar: #1e202a; --kt-content-bg: #f0f2f5; }
    .ant-btn-primary { background-color: #3e8dff; border-color: #3e8dff; }
    .ant-btn-primary:hover { background-color: #5ea3ff; border-color: #5ea3ff; }
    a, .ant-btn-link { color: #3e8dff; }
    a:hover, .ant-btn-link:hover { color: #5ea3ff; }
    .kt-status { display: inline-flex; align-items: center; gap: 6px; padding: 0 8px; height: 24px; border-radius: 4px; font-size: 12px; line-height: 24px; }
    .kt-status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .kt-status-success { background: #effffb; color: #00a89a; }
    .kt-status-success .kt-status-dot { background: #00e5c7; }
    .kt-status-danger { background: #fff5f3; color: #d4634f; }
    .kt-status-danger .kt-status-dot { background: #ff8b78; }
    .kt-status-default { background: #f5f6f9; color: #8c95a6; }
    .kt-status-default .kt-status-dot { background: #bfc6d1; }
    .tl-filter { background: #fff; padding: 16px 24px; border-radius: 8px; margin-bottom: 16px; }
    .tl-filter-left { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
    .tl-table { background: #fff; padding: 24px; padding-top: 16px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .action-group { display: inline-flex; align-items: center; gap: 0; }
    .action-group .action-divider { width: 1px; height: 14px; background: #e8e8e8; margin: 0 4px; }
    .doc-toggle { position: fixed; top: 50%; right: 0; transform: translateY(-50%); z-index: 1001; background: #3e8dff; color: #fff; border: none; padding: 12px 4px; border-radius: 4px 0 0 4px; cursor: pointer; writing-mode: vertical-rl; font-size: 13px; letter-spacing: 2px; }
    .doc-panel { position: fixed; top: 0; right: -400px; width: 400px; height: 100vh; background: #fafafa; border-left: 1px solid #e8e8e8; padding: 24px; overflow-y: auto; z-index: 1000; transition: right 0.3s; }
    .doc-panel.open { right: 0; }
    .doc-panel .doc-section { background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .doc-panel .doc-title { font-size: 15px; font-weight: 600; color: rgba(0,0,0,0.85); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0; }
  </style>
</head>
<body>
<div class="ant-layout" style="min-height: 100vh;">
  <!-- 侧边栏 -->
  <aside style="background: #1e202a; width: 220px; flex-shrink: 0; position: fixed; left: 0; top: 0; bottom: 0; z-index: 100;">
    <div style="height: 56px; display: flex; align-items: center; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.08);">
      <span style="color: #fff; font-size: 16px; font-weight: 600;">KT Agent</span>
    </div>
    <ul style="list-style: none; padding: 8px 0; margin: 0;">
      <li style="padding: 10px 20px; color: rgba(255,255,255,0.65); font-size: 14px; cursor: pointer;">
        <span style="margin-right: 10px;">🏠</span>首页
      </li>
      <li style="padding: 10px 16px; background: #3e8dff; color: #fff; font-size: 14px; cursor: pointer; border-radius: 4px; margin: 0 8px;">
        <span style="margin-right: 10px;">📋</span>角色管理
      </li>
    </ul>
  </aside>

  <!-- 右侧 -->
  <div style="margin-left: 220px; flex: 1; display: flex; flex-direction: column;">
    <!-- 顶栏 -->
    <header style="height: 56px; background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); position: sticky; top: 0; z-index: 99;">
      <span style="font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85);">角色管理</span>
      <div style="display: flex; align-items: center; gap: 16px;">
        <span style="color: rgba(0,0,0,0.65); font-size: 14px;">管理员</span>
      </div>
    </header>

    <!-- 内容区 -->
    <main style="flex: 1; padding: 16px; background: #f0f2f5; overflow: auto;">
      <!-- 筛选区 -->
      <div class="tl-filter">
        <div class="tl-filter-left">
          <input class="ant-input" placeholder="角色名称" style="width: 200px;">
          <button class="ant-btn ant-btn-primary" onclick="mockAction('搜索')">查询</button>
          <button class="ant-btn">重置</button>
          <button class="ant-btn ant-btn-primary" onclick="openDrawer('新增角色', 'add')">新增角色</button>
        </div>
      </div>

      <!-- 表格区 -->
      <div class="tl-table">
        <div class="ant-table-wrapper">
          <div class="ant-table">
            <div class="ant-table-container">
              <div class="ant-table-content">
                <table style="table-layout: auto; width: 100%;">
                  <thead class="ant-table-thead">
                    <tr>
                      <th class="ant-table-cell">角色名称</th>
                      <th class="ant-table-cell">描述</th>
                      <th class="ant-table-cell">类型</th>
                      <th class="ant-table-cell" style="width: 180px; text-align: center;">操作</th>
                    </tr>
                  </thead>
                  <tbody class="ant-table-tbody">
                    <tr class="ant-table-row">
                      <td class="ant-table-cell">超级管理员</td>
                      <td class="ant-table-cell">拥有所有权限</td>
                      <td class="ant-table-cell"><span class="kt-status kt-status-primary"><span class="kt-status-dot"></span>内置</span></td>
                      <td class="ant-table-cell" style="text-align: center;">
                        <div class="action-group">
                          <a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer('角色详情', 'detail')">详情</a>
                        </div>
                      </td>
                    </tr>
                    <tr class="ant-table-row">
                      <td class="ant-table-cell">运营专员</td>
                      <td class="ant-table-cell">负责灰度与发布操作</td>
                      <td class="ant-table-cell"><span class="kt-status kt-status-default"><span class="kt-status-dot"></span>自定义</span></td>
                      <td class="ant-table-cell" style="text-align: center;">
                        <div class="action-group">
                          <a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer('角色详情', 'detail')">详情</a>
                          <span class="action-divider"></span>
                          <a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer('编辑角色', 'edit')">编辑</a>
                          <span class="action-divider"></span>
                          <a style="color: #ff4d4f; cursor: pointer;" onclick="openConfirmModal()">删除</a>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <!-- 分页 -->
        <div style="padding: 16px 0 0; display: flex; justify-content: flex-end;">
          <ul class="ant-pagination">
            <li class="ant-pagination-total-text">共 5 条</li>
            <li class="ant-pagination-prev ant-pagination-disabled"><button class="ant-pagination-item-link" disabled>&lt;</button></li>
            <li class="ant-pagination-item ant-pagination-item-active"><a>1</a></li>
            <li class="ant-pagination-next ant-pagination-disabled"><button class="ant-pagination-item-link" disabled>&gt;</button></li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</div>

<!-- 抽屉 -->
<div id="drawer" style="display: none;">
  <div class="ant-drawer" style="position: fixed; top: 0; right: 0; bottom: 0; z-index: 1000;">
    <div class="ant-drawer-mask" onclick="closeDrawer()" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0;"></div>
    <div class="ant-drawer-content-wrapper" style="width: 980px; position: fixed; top: 0; right: 0; bottom: 0;">
      <div class="ant-drawer-content">
        <div class="ant-drawer-wrapper-body" style="display: flex; flex-direction: column; height: 100%;">
          <div class="ant-drawer-header" style="padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between;">
            <div class="ant-drawer-title" id="drawerTitle" style="font-size: 16px; font-weight: 500;">新增角色</div>
            <button onclick="closeDrawer()" style="border: none; background: none; font-size: 16px; cursor: pointer; color: rgba(0,0,0,0.45);">✕</button>
          </div>
          <div class="ant-drawer-body" style="flex: 1; overflow: auto; padding: 24px;">
            <form class="ant-form ant-form-vertical">
              <div class="ant-form-item">
                <div class="ant-form-item-label"><label><span style="color: #ff4d4f; margin-right: 4px;">*</span>角色名称</label></div>
                <div class="ant-form-item-control"><div class="ant-form-item-control-input"><input class="ant-input" placeholder="例如：运营专员" style="max-width: 400px;"></div></div>
              </div>
              <div class="ant-form-item">
                <div class="ant-form-item-label"><label>描述</label></div>
                <div class="ant-form-item-control"><div class="ant-form-item-control-input"><textarea class="ant-input" placeholder="例如：负责灰度与发布操作" rows="3" style="max-width: 400px; resize: vertical;"></textarea></div></div>
              </div>
            </form>
          </div>
          <div class="ant-drawer-footer" id="drawerFooter" style="border-top: 1px solid #f0f0f0; padding: 12px 24px; text-align: right;">
            <button class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
            <button class="ant-btn ant-btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- 确认弹窗 -->
<div id="confirmModal" style="display: none;">
  <div class="ant-modal-mask" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0; z-index: 1001;"></div>
  <div class="ant-modal-wrap" style="position: fixed; inset: 0; z-index: 1002; display: flex; align-items: center; justify-content: center;">
    <div class="ant-modal" style="width: 420px;">
      <div class="ant-modal-content">
        <div class="ant-modal-header"><div class="ant-modal-title">确认删除</div></div>
        <div class="ant-modal-body" style="padding: 24px;"><p>确定要删除此角色吗？此操作不可撤销。</p></div>
        <div class="ant-modal-footer">
          <button class="ant-btn" onclick="closeConfirmModal()">取消</button>
          <button class="ant-btn ant-btn-primary" style="background: #ff4d4f; border-color: #ff4d4f;">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- 文档面板 -->
<button class="doc-toggle" onclick="toggleDoc()">交互说明</button>
<div class="doc-panel" id="docPanel">
  <div class="doc-section">
    <div class="doc-title">页面说明</div>
    <p style="color: rgba(0,0,0,0.65); font-size: 14px;">角色管理列表页，支持角色的新增、编辑、删除和查看详情。</p>
  </div>
  <div class="doc-section">
    <div class="doc-title">交互逻辑</div>
    <div style="font-size: 14px; color: rgba(0,0,0,0.65); line-height: 2;">
      <div><b>查询：</b>输入关键词后点击查询按钮筛选列表</div>
      <div><b>重置：</b>清空筛选条件恢复默认列表</div>
      <div><b>新增：</b>点击新增按钮打开右侧抽屉</div>
      <div><b>编辑：</b>点击编辑打开抽屉并回填数据，内置角色不可编辑</div>
      <div><b>删除：</b>弹出确认弹窗，内置角色不可删除</div>
      <div><b>详情：</b>点击详情打开只读抽屉</div>
    </div>
  </div>
</div>

<script>
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
function closeDrawer() { document.getElementById('drawer').style.display = 'none'; }
function openConfirmModal() { document.getElementById('confirmModal').style.display = 'block'; }
function closeConfirmModal() { document.getElementById('confirmModal').style.display = 'none'; }
function toggleDoc() { document.getElementById('docPanel').classList.toggle('open'); }
function mockAction(action) { console.log('[Mock]', action); }
</script>
</body>
</html>
```

## 7. 重要规则

1. **必须使用项目配色**：#3e8dff 主色，非 Ant Design 默认 #1890ff
2. **使用自定义状态组件**：`.kt-status` 替代 `ant-tag`
3. **TL 布局模式**：`.tl-filter` + `.tl-table` + 抽屉
4. **表格 bordered small**：与项目 `@kt/unity-antd-table` 全局配置一致
5. **操作按钮用 action-group**：替代 `<action-group>` 组件
6. **Tailwind 仅用于布局**：flex、grid、间距
7. **不使用 @apply**：CDN 模式不生效
