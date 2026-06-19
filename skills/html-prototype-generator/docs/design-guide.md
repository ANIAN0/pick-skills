# KT Admin 原型设计规范

本规范确保原型页面与 kt-agent-framework 管理后台风格一致。

## 0. 设计原则

1. **Ant Design 优先**：组件结构和交互模式必须遵循 Ant Design 4.x 规范，项目配色覆盖主色但不改变组件结构
2. **禁止使用 Emoji**：侧边栏图标、按钮图标、状态标识等一律使用 CSS/SVG 实现或 Ant Design 图标类名（如 `anticon anticon-home`），绝不使用 emoji 字符（🏠🤖📋 等），emoji 在不同系统渲染不一致，显得不专业
3. **项目配色覆盖**：主色使用 #3e8dff 替代 Ant Design 默认 #1890ff，但 Ant Design 组件类名和结构保持不变
4. **需求可见性**：所有对源页面的改动（新增/修改/移除）必须通过引导层在原型上直接标注，不能仅在文档面板中描述

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
  <!-- Ant Design 图标（SVG symbol 方式） -->
  <script src="https://at.alicdn.com/t/c/font_3649831_vn4l2gpuij.js"></script>
  <style>
    /* CSS 变量 + 覆盖 + 组件样式（见第3节完整版） */
  </style>
</head>
```

完整样式块（每个HTML文件必须包含）：

```css
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
.kt-status { display: inline-flex; align-items: center; gap: 6px; padding: 0 8px; height: 24px; border-radius: 4px; font-size: 12px; line-height: 24px; }
.kt-status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
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
.tl-filter { background: #fff; padding: 16px 24px; border-radius: 8px; margin-bottom: 16px; }
.tl-filter-left { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.tl-table { background: #fff; padding: 24px; padding-top: 16px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }

/* 操作按钮组 */
.action-group { display: inline-flex; align-items: center; gap: 0; }
.action-group .ant-btn-link { padding: 0 4px; height: auto; }
.action-group .action-divider { width: 1px; height: 14px; background: #e8e8e8; margin: 0 4px; }

/* 文档面板 */
.doc-toggle { position: fixed; top: 50%; right: 0; transform: translateY(-50%); z-index: 1001; background: #3e8dff; color: #fff; border: none; padding: 12px 4px; border-radius: 4px 0 0 4px; cursor: pointer; writing-mode: vertical-rl; font-size: 13px; letter-spacing: 2px; transition: right 0.3s; }
.doc-panel { position: fixed; top: 0; right: -400px; width: 400px; height: 100vh; background: #fafafa; border-left: 1px solid #e8e8e8; padding: 24px; overflow-y: auto; z-index: 1000; transition: right 0.3s; }
.doc-panel.open { right: 0; }
.doc-panel .doc-section { background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.doc-panel .doc-title { font-size: 15px; font-weight: 600; color: rgba(0,0,0,0.85); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0; }
```

## 4. 整体布局结构

```html
<body>
<div class="ant-layout" style="min-height: 100vh;">
  <!-- 侧边栏 -->
  <aside style="background: #1e202a; width: 220px; flex-shrink: 0; position: fixed; left: 0; top: 0; bottom: 0; z-index: 100;">
    <div style="height: 56px; display: flex; align-items: center; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.08);">
      <span style="color: #fff; font-size: 16px; font-weight: 600;">KT Agent</span>
    </div>
    <ul style="list-style: none; padding: 8px 0; margin: 0;">
      <li style="padding: 10px 20px; color: rgba(255,255,255,0.65); cursor: pointer; font-size: 14px; display: flex; align-items: center;">
        <span class="anticon anticon-home" style="margin-right: 10px; font-size: 14px;"></span>首页
      </li>
      <li style="padding: 10px 16px; background: #3e8dff; color: #fff; cursor: pointer; font-size: 14px; border-radius: 4px; margin: 0 8px; display: flex; align-items: center;">
        <span class="anticon anticon-file-text" style="margin-right: 10px; font-size: 14px;"></span>当前页面
      </li>
    </ul>
  </aside>

  <!-- 右侧 -->
  <div style="margin-left: 220px; flex: 1; display: flex; flex-direction: column;">
    <header style="height: 56px; background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); position: sticky; top: 0; z-index: 99;">
      <span style="font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85);">页面标题</span>
      <div style="display: flex; align-items: center; gap: 16px;">
        <span style="color: rgba(0,0,0,0.65); font-size: 14px;">管理员</span>
      </div>
    </header>
    <main style="flex: 1; padding: 16px; background: #f0f2f5; overflow: auto;">
      <!-- 页面内容 -->
    </main>
  </div>
</div>
</body>
```

## 5. 组件规范

### 图标使用规范（禁止 Emoji）

**推荐方式：**
```html
<script src="https://at.alicdn.com/t/c/font_3649831_vn4l2gpuij.js"></script>
<svg class="anticon" style="width: 14px; height: 14px; margin-right: 10px;">
  <use xlink:href="#anticon-home"></use>
</svg>
```

**Fallback（文字色块）：**
```html
<span style="display: inline-flex; width: 18px; height: 18px; border-radius: 3px; background: #3e8dff; color: #fff; font-size: 11px; align-items: center; justify-content: center; margin-right: 10px;">首</span>
```

### yc-status 状态标签

**优先方案 — ant-tag：**
```html
<span class="ant-tag ant-tag-success">启用</span>
<span class="ant-tag ant-tag-error">禁用</span>
<span class="ant-tag ant-tag-warning">待审核</span>
```

**增强方案 — .kt-status（带圆点背景色）：**
```html
<span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span>
<span class="kt-status kt-status-danger"><span class="kt-status-dot"></span>禁用</span>
<span class="kt-status kt-status-warning"><span class="kt-status-dot"></span>待审核</span>
<span class="kt-status kt-status-primary"><span class="kt-status-dot"></span>运行中</span>
<span class="kt-status kt-status-default"><span class="kt-status-dot"></span>未知</span>
```

### 表格（bordered + small）

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
                <td class="ant-table-cell"><span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span></td>
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
  <div style="padding: 16px 0 0; display: flex; justify-content: flex-end;">
    <ul class="ant-pagination">
      <li class="ant-pagination-total-text">共 50 条</li>
      <li class="ant-pagination-prev ant-pagination-disabled"><button class="ant-pagination-item-link" disabled>&lt;</button></li>
      <li class="ant-pagination-item ant-pagination-item-active"><a>1</a></li>
      <li class="ant-pagination-next"><button class="ant-pagination-item-link">&gt;</button></li>
    </ul>
  </div>
</div>
```

### 抽屉

```html
<div id="drawer" style="display: none;">
  <div class="ant-drawer" style="position: fixed; top: 0; right: 0; bottom: 0; z-index: 1000;">
    <div class="ant-drawer-mask" onclick="closeDrawer()" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0;"></div>
    <div class="ant-drawer-content-wrapper" style="width: 980px; position: fixed; top: 0; right: 0; bottom: 0;">
      <div class="ant-drawer-content">
        <div class="ant-drawer-wrapper-body" style="display: flex; flex-direction: column; height: 100%;">
          <div class="ant-drawer-header" style="padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between;">
            <div class="ant-drawer-title" id="drawerTitle" style="font-size: 16px; font-weight: 500;">标题</div>
            <button onclick="closeDrawer()" style="border: none; background: none; font-size: 16px; cursor: pointer; color: rgba(0,0,0,0.45);">✕</button>
          </div>
          <div class="ant-drawer-body" style="flex: 1; overflow: auto; padding: 24px;">
            <!-- 表单内容 -->
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
```

### 确认弹窗

```html
<div id="confirmModal" style="display: none;">
  <div class="ant-modal-mask" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0; z-index: 1001;"></div>
  <div class="ant-modal-wrap" style="position: fixed; inset: 0; z-index: 1002; display: flex; align-items: center; justify-content: center;">
    <div class="ant-modal" style="width: 420px;">
      <div class="ant-modal-content">
        <div class="ant-modal-header"><div class="ant-modal-title">确认删除</div></div>
        <div class="ant-modal-body" style="padding: 24px;"><p>确定要删除此记录吗？此操作不可撤销。</p></div>
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

```html
<form class="ant-form ant-form-vertical">
  <div class="ant-form-item">
    <div class="ant-form-item-label"><label><span style="color: #ff4d4f; margin-right: 4px;">*</span>名称</label></div>
    <div class="ant-form-item-control"><div class="ant-form-item-control-input">
      <input class="ant-input" placeholder="请输入名称" style="max-width: 400px;">
    </div></div>
  </div>
  <div class="ant-form-item">
    <div class="ant-form-item-label"><label>描述</label></div>
    <div class="ant-form-item-control"><div class="ant-form-item-control-input">
      <textarea class="ant-input" placeholder="请输入描述" rows="3" style="max-width: 400px; resize: vertical;"></textarea>
    </div></div>
  </div>
</form>
```

---

## 6. 交互脚本模板

每个HTML文件底部必须包含：

```javascript
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
function mockAction(action, data) { console.log('[Mock]', action, data); }
</script>
```

---

## 7. 文档面板（交互说明）

文档面板记录页面整体说明、字段含义等，默认隐藏，点击右侧「交互说明」按钮展开。

**注意**：文档面板 ≠ 需求说明。需求改动必须用引导层（第8节）标注，文档面板只记录页面通用说明。

```html
<button class="doc-toggle" onclick="toggleDoc()">交互说明</button>
<div class="doc-panel" id="docPanel">
  <div class="doc-section">
    <div class="doc-title">页面说明</div>
    <p style="color: rgba(0,0,0,0.65); font-size: 14px;">一句话描述页面用途。</p>
  </div>
  <div class="doc-section">
    <div class="doc-title">交互逻辑</div>
    <div style="font-size: 14px; color: rgba(0,0,0,0.65); line-height: 2;">
      <div><b>查询：</b>输入筛选条件后点击查询按钮</div>
      <div><b>新增：</b>点击新增按钮打开右侧抽屉</div>
      <div><b>删除：</b>弹出确认弹窗，确认后删除</div>
    </div>
  </div>
</div>
```

---

## 8. 需求引导层（⚠️ 有需求改动时必须包含）

### 什么是引导层

类似新手引导的视觉效果，在原型页面上叠加一个半透明蒙版，对每一处需求改动显示**彩色高亮框 + 气泡说明卡片**，让查看者直观理解"这里改了什么"。

**效果示意：**
```
┌────────────────────────────────────────┐
│  ┌──────────────────────────────────┐  │
│  │  筛选区（已还原）                 │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │  ← 蒙版盖住页面
│  │  表格（已还原）                   │  │
│  │                          ┌──────┐│  │
│  │  [导出按钮] ←蓝色高亮框  │ 1    ││  │  ← 高亮框 + 序号徽标
│  │                          └──────┘│  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌─────────────────┐                   │
│  │ ① 新增：导出按钮 │ ← 气泡说明卡片   │
│  │ 支持将当前筛选   │                   │
│  │ 结果导出 Excel  │                   │
│  └─────────────────┘                   │
└────────────────────────────────────────┘
```

### 颜色规范

| 改动类型 | 高亮框颜色 | 气泡标签 | 蒙版色 |
|---------|-----------|---------|-------|
| `new`（新增）| `#3e8dff` 蓝色，3px 实线 | 蓝底白字「新增」 | 无（高亮框足够）|
| `modified`（修改）| `#ffb71d` 橙色，3px 实线 | 橙底白字「修改」 | 无 |
| `removed`（移除）| `#ff8b78` 红色，3px 虚线 | 红底白字「移除」 | 无 |

高亮框使用 `box-shadow: 0 0 0 3px <color>` 实现，不影响布局。

### 完整实现代码

在 HTML 文件的 `</body>` 前插入以下代码块：

```html
<!-- ==================== 需求引导层 ==================== -->

<!-- 引导开关按钮（固定在右上角） -->
<div id="guide-toggle-bar" style="position: fixed; top: 14px; right: 16px; z-index: 9999; display: flex; align-items: center; gap: 8px;">
  <div style="background: rgba(0,0,0,0.6); color: #fff; font-size: 12px; padding: 4px 10px; border-radius: 12px; letter-spacing: 0.5px;">
    需求改动预览
  </div>
  <button id="guide-toggle-btn" onclick="toggleGuide()" style="background: #3e8dff; color: #fff; border: none; padding: 5px 14px; border-radius: 4px; font-size: 13px; cursor: pointer; box-shadow: 0 2px 6px rgba(62,141,255,0.4);">
    关闭引导
  </button>
</div>

<!-- 引导说明卡片容器（绝对定位，由 JS 动态插入） -->
<div id="guide-cards" style="position: fixed; bottom: 24px; left: 240px; z-index: 9998; display: flex; flex-direction: column; gap: 8px; max-width: 360px;"></div>

<style>
/* 高亮框样式 */
.guide-highlight-new {
  box-shadow: 0 0 0 3px #3e8dff !important;
  border-radius: 4px;
  position: relative;
  z-index: 100;
}
.guide-highlight-modified {
  box-shadow: 0 0 0 3px #ffb71d !important;
  border-radius: 4px;
  position: relative;
  z-index: 100;
}
.guide-highlight-removed {
  box-shadow: 0 0 0 3px #ff8b78 !important;
  border-radius: 4px;
  border: 2px dashed #ff8b78 !important;
  position: relative;
  z-index: 100;
}
/* 序号徽标 */
.guide-badge {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 101;
  pointer-events: none;
}
/* 说明卡片 */
.guide-card {
  background: #fff;
  border-radius: 8px;
  padding: 10px 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.14);
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  line-height: 1.6;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.guide-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.18); }
.guide-card-label {
  padding: 1px 7px;
  border-radius: 3px;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  margin-top: 2px;
}
.guide-card-content { flex: 1; }
.guide-card-title { font-weight: 600; color: rgba(0,0,0,0.85); }
.guide-card-desc { color: rgba(0,0,0,0.55); margin-top: 2px; }
</style>

<script>
// ===== 需求改动数据（按实际需求填写）=====
const guideSteps = [
  {
    id: 1,
    selector: '#btn-export',        // 目标元素的 CSS 选择器（建议加 id）
    type: 'new',                    // new | modified | removed
    title: '新增：导出按钮',
    desc: '支持将当前筛选结果导出为 Excel，权限：运营及以上角色可见',
  },
  {
    id: 2,
    selector: '[data-col="status"]',
    type: 'modified',
    title: '修改：状态列',
    desc: '原「启用/禁用」两态改为「启用/禁用/待审核」三态，新增黄色待审核样式',
  },
  {
    id: 3,
    selector: '.guide-removed-1',   // 被移除位置用占位元素标记（见下方说明）
    type: 'removed',
    title: '移除：批量操作栏',
    desc: '当前版本不需要批量操作，已移除；后续迭代版本再加',
  },
];

// ===== 颜色映射 =====
const guideColors = {
  new:      { border: '#3e8dff', label: '#3e8dff', text: '新增' },
  modified: { border: '#ffb71d', label: '#ffb71d', text: '修改' },
  removed:  { border: '#ff8b78', label: '#ff8b78', text: '移除' },
};

let guideActive = true;
// 记录已包裹的元素，用于还原
const highlightedEls = [];

function renderGuide() {
  // 1. 清除旧状态
  highlightedEls.forEach(({ el, wrapper }) => {
    if (wrapper && wrapper.parentNode) {
      wrapper.parentNode.insertBefore(el, wrapper); // 把原元素还原到 wrapper 位置
      wrapper.remove();
    }
    el.classList.remove('guide-highlight-new', 'guide-highlight-modified', 'guide-highlight-removed');
  });
  highlightedEls.length = 0;
  document.getElementById('guide-cards').innerHTML = '';

  if (!guideActive) return;

  guideSteps.forEach(step => {
    const el = document.querySelector(step.selector);
    if (!el) return;

    const color = guideColors[step.type];

    // 2. 高亮目标元素
    el.classList.add(`guide-highlight-${step.type}`);

    // 3. 用 wrapper 包裹，以便绝对定位序号徽标
    const wrapper = document.createElement('span');
    wrapper.style.cssText = 'position:relative; display:inline-block;';
    el.parentNode.insertBefore(wrapper, el);
    wrapper.appendChild(el);

    const badge = document.createElement('span');
    badge.style.cssText = `position:absolute;top:-10px;right:-10px;width:20px;height:20px;border-radius:50%;background:${color.border};color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;z-index:101;pointer-events:none;`;
    badge.textContent = step.id;
    wrapper.appendChild(badge);

    highlightedEls.push({ el, wrapper });

    // 4. 生成说明卡片
    const card = document.createElement('div');
    card.className = 'guide-card';
    card.innerHTML = `
      <span class="guide-card-label" style="background:${color.label};">${color.text}</span>
      <div class="guide-card-content">
        <div class="guide-card-title">${step.id}. ${step.title}</div>
        <div class="guide-card-desc">${step.desc}</div>
      </div>
    `;
    card.onclick = () => el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    document.getElementById('guide-cards').appendChild(card);
  });
}

function toggleGuide() {
  guideActive = !guideActive;
  const btn = document.getElementById('guide-toggle-btn');
  btn.textContent = guideActive ? '关闭引导' : '开启引导';
  btn.style.background = guideActive ? '#3e8dff' : '#8c8c8c';
  renderGuide();
}

// 页面加载后自动渲染
window.addEventListener('DOMContentLoaded', renderGuide);
</script>
<!-- ==================== /需求引导层 ==================== -->
```

### 如何标记被移除的元素

被移除的元素在页面上不再存在，需要插入一个占位符让引导层有东西可以高亮：

```html
<!-- 原来批量操作栏的位置，已移除，保留占位供引导层高亮 -->
<div class="guide-removed-1" style="height: 0; overflow: hidden;" aria-hidden="true"></div>
```

### 使用要点

1. **selector 精确性**：建议给需要标注的新增/修改元素加 `id` 属性，如 `id="btn-export"`
2. **卡片位置**：默认显示在页面左下角，可根据页面内容调整 `#guide-cards` 的 `bottom`/`left` 值
3. **卡片数量**：建议不超过 8 个，过多时可合并相关改动
4. **desc 写法**：一句话说清楚「改了什么 + 为什么改 / 权限 / 注意事项」

---

## 9. 重要规则汇总

1. **必须使用项目配色**：#3e8dff 主色，非 Ant Design 默认 #1890ff
2. **禁止使用 Emoji**：所有图标使用 Ant Design 图标类名（`anticon anticon-xxx`）或 CSS 实现
3. **复刻模式两阶段**：先1:1还原所有元素，确认后再叠加改动
4. **需求改动必须用引导层**：有任何对源页面的改动，必须通过引导层标注，不能只写在文档面板
5. **状态标签优先用 ant-tag**：需要带圆点背景色时才用 `.kt-status`
6. **TL 布局模式**：`.tl-filter` + `.tl-table` + 抽屉
7. **Tailwind 仅用于布局**：flex、grid、间距
8. **不使用 @apply**：CDN 模式不生效
9. **遵循 Ant Design 组件结构**：即使配色被覆盖，组件 HTML 结构和类名必须遵循 Ant Design 4.x 规范
