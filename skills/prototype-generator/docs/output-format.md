# 原型HTML输出格式规范

## 文件输出位置

**默认输出目录：** `.dev/prototype/`

## 文件结构

**必须使用真正的 Ant Design CSS，Tailwind 仅用于页面级布局。**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {页面名称}</title>
  <!-- Ant Design 4.x 样式（必须） -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <!-- Tailwind CSS（仅用于页面级布局） -->
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div class="prototype-container">
    <!-- 左侧原型（1200px） -->
    <div class="prototype-left">
      <!-- Ant Design 布局 -->
    </div>

    <!-- 右侧说明 -->
    <div class="prototype-right">
      <!-- 交互说明 -->
    </div>
  </div>
</body>
</html>
```

## Ant Design 布局规范

### 标准后台布局结构

```html
<div class="ant-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <header class="ant-layout-header" style="background: #fff; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08);">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">S</div>
      <span style="font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85);">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <div style="width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%;"></div>
    </div>
  </header>

  <div class="ant-layout" style="display: flex;">
    <!-- 侧边栏 -->
    <aside class="ant-layout-sider" style="background: #001529; width: 200px; flex-shrink: 0;">
      <ul class="ant-menu ant-menu-dark ant-menu-root" style="background: #001529; padding: 16px 0;">
        <li class="ant-menu-item" style="padding-left: 24px; color: rgba(255,255,255,0.65);">
          <span>🏠</span>
          <span style="margin-left: 10px;">首页</span>
        </li>
        <li class="ant-menu-item ant-menu-item-selected" style="background: #1890ff; padding-left: 24px;">
          <span>📋</span>
          <span style="margin-left: 10px;">当前页面</span>
        </li>
      </ul>
    </aside>

    <!-- 主内容 -->
    <main class="ant-layout-content" style="flex: 1; padding: 24px; background: #f0f2f5; overflow: auto;">
      <!-- 面包屑 -->
      <div class="ant-breadcrumb" style="margin-bottom: 16px;">
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.45);">首页</span>
        <span class="ant-breadcrumb-separator">/</span>
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.85);">当前页面</span>
      </div>

      <!-- 页面内容 -->
    </main>
  </div>
</div>
```

## 列表页结构

```html
<!-- 搜索卡片 -->
<div class="ant-card" style="margin-bottom: 24px;">
  <div class="ant-card-body" style="padding: 24px;">
    <form class="ant-form">
      <div class="ant-row" style="margin-left: -8px; margin-right: -8px;">
        <div class="ant-col" style="padding-left: 8px; padding-right: 8px;">
          <input class="ant-input" placeholder="请输入关键词" style="width: 200px;">
        </div>
        <div class="ant-col" style="padding-left: 8px; padding-right: 8px;">
          <button type="button" class="ant-btn ant-btn-primary">搜索</button>
          <button type="button" class="ant-btn" style="margin-left: 8px;">重置</button>
        </div>
      </div>
    </form>
  </div>
</div>

<!-- 操作栏 -->
<div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
  <div style="display: flex; gap: 8px;">
    <button type="button" class="ant-btn ant-btn-primary" onclick="openDrawer('新增')">新增</button>
    <button type="button" class="ant-btn">导出</button>
  </div>
</div>

<!-- 表格卡片 -->
<div class="ant-card">
  <div class="ant-table-wrapper">
    <div class="ant-spin-nested-loading">
      <div class="ant-spin-container">
        <div class="ant-table">
          <div class="ant-table-container">
            <div class="ant-table-content">
              <table style="table-layout: auto; width: 100%;">
                <thead class="ant-table-thead">
                  <tr>
                    <th class="ant-table-cell">名称</th>
                    <th class="ant-table-cell">状态</th>
                    <th class="ant-table-cell">创建时间</th>
                    <th class="ant-table-cell">操作</th>
                  </tr>
                </thead>
                <tbody class="ant-table-tbody">
                  <tr class="ant-table-row">
                    <td class="ant-table-cell">示例数据</td>
                    <td class="ant-table-cell">
                      <span class="ant-tag ant-tag-green">启用</span>
                    </td>
                    <td class="ant-table-cell" style="color: rgba(0,0,0,0.45);">2024-03-25</td>
                    <td class="ant-table-cell">
                      <a style="color: #1890ff; cursor: pointer;" onclick="openDrawer('编辑')">编辑</a>
                      <span style="margin: 0 8px; color: #d9d9d9;">|</span>
                      <a style="color: #ff4d4f; cursor: pointer;" onclick="openModal('删除确认')">删除</a>
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

  <!-- 分页 -->
  <div style="padding: 16px; display: flex; justify-content: flex-end;">
    <ul class="ant-pagination">
      <li class="ant-pagination-total-text" style="margin-right: 8px;">共 100 条</li>
      <li class="ant-pagination-prev ant-pagination-disabled">
        <button class="ant-pagination-item-link" disabled>&lt;</button>
      </li>
      <li class="ant-pagination-item ant-pagination-item-1 ant-pagination-item-active">
        <a>1</a>
      </li>
      <li class="ant-pagination-item">
        <a>2</a>
      </li>
      <li class="ant-pagination-next">
        <button class="ant-pagination-item-link">&gt;</button>
      </li>
    </ul>
  </div>
</div>
```

## 表单页结构

```html
<div class="ant-card" style="max-width: 800px;">
  <div class="ant-card-head">
    <div class="ant-card-head-title">表单标题</div>
  </div>
  <div class="ant-card-body" style="padding: 24px;">
    <form class="ant-form">
      <div class="ant-row ant-form-item">
        <div class="ant-col ant-form-item-label" style="width: 120px;">
          <label><span style="color: #ff4d4f; margin-right: 4px;">*</span>字段名称</label>
        </div>
        <div class="ant-col ant-form-item-control">
          <div class="ant-form-item-control-input">
            <input class="ant-input" placeholder="请输入" style="width: 100%;">
          </div>
        </div>
      </div>

      <div class="ant-row ant-form-item" style="margin-top: 24px;">
        <div class="ant-col ant-form-item-control" style="margin-left: 120px;">
          <button type="button" class="ant-btn ant-btn-primary" style="margin-right: 8px;">提交</button>
          <button type="button" class="ant-btn">取消</button>
        </div>
      </div>
    </form>
  </div>
</div>
```

## 详情页结构

```html
<!-- 操作栏 -->
<div style="margin-bottom: 24px;">
  <button type="button" class="ant-btn ant-btn-primary" style="margin-right: 8px;">编辑</button>
  <button type="button" class="ant-btn">返回</button>
</div>

<!-- 详情卡片 -->
<div class="ant-card" style="margin-bottom: 24px;">
  <div class="ant-card-head">
    <div class="ant-card-head-title">基本信息</div>
  </div>
  <div class="ant-card-body">
    <div class="ant-descriptions">
      <div class="ant-descriptions-item" style="padding-bottom: 16px;">
        <span class="ant-descriptions-item-label" style="color: rgba(0,0,0,0.85); font-weight: 500; display: inline-block; width: 120px;">字段名:</span>
        <span class="ant-descriptions-item-content" style="color: rgba(0,0,0,0.65);">字段值</span>
      </div>
    </div>
  </div>
</div>
```

## 抽屉组件（合并到主页面）

```html
<div id="drawer" class="ant-drawer-wrapper" style="display: none;">
  <div class="ant-drawer">
    <div class="ant-drawer-mask" onclick="closeDrawer()"></div>
    <div class="ant-drawer-content-wrapper">
      <div class="ant-drawer-content">
        <div class="ant-drawer-header">
          <div class="ant-drawer-title">抽屉标题</div>
          <button type="button" class="ant-drawer-close" onclick="closeDrawer()">✕</button>
        </div>
        <div class="ant-drawer-body">
          <!-- 表单或详情内容 -->
        </div>
        <div class="ant-drawer-footer">
          <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
          <button type="button" class="ant-btn ant-btn-primary">确定</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 弹窗组件（合并到主页面）

```html
<div id="modal" class="ant-modal-root" style="display: none;">
  <div class="ant-modal-mask" onclick="closeModal()"></div>
  <div class="ant-modal-wrap">
    <div class="ant-modal" style="width: 420px;">
      <div class="ant-modal-content">
        <button type="button" class="ant-modal-close" onclick="closeModal()">✕</button>
        <div class="ant-modal-header">
          <div class="ant-modal-title">弹窗标题</div>
        </div>
        <div class="ant-modal-body">
          <!-- 弹窗内容 -->
        </div>
        <div class="ant-modal-footer">
          <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeModal()">取消</button>
          <button type="button" class="ant-btn ant-btn-primary">确定</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

## Mock 交互脚本

```javascript
<script>
// 抽屉控制
function openDrawer(title) {
  const drawer = document.getElementById('drawer');
  if (drawer) {
    drawer.style.display = 'block';
    const titleEl = drawer.querySelector('.ant-drawer-title');
    if (titleEl) titleEl.textContent = title || '标题';
  }
}

function closeDrawer() {
  const drawer = document.getElementById('drawer');
  if (drawer) drawer.style.display = 'none';
}

// 弹窗控制
function openModal(title) {
  const modal = document.getElementById('modal');
  if (modal) {
    modal.style.display = 'block';
    const titleEl = modal.querySelector('.ant-modal-title');
    if (titleEl) titleEl.textContent = title || '标题';
  }
}

function closeModal() {
  const modal = document.getElementById('modal');
  if (modal) modal.style.display = 'none';
}

// 通用操作
function mockAction(action, data) {
  console.log('[Mock]', action, data);
  alert(action + ' 成功（模拟）');
}
</script>
```

## 重要规则

1. **必须使用 `antd.min.css`**：这是风格一致的基础
2. **使用原生 antd 类名**：
   - 布局：`ant-layout`, `ant-layout-header`, `ant-layout-sider`, `ant-layout-content`
   - 组件：`ant-card`, `ant-table`, `ant-form`, `ant-btn`, `ant-input`
   - 导航：`ant-breadcrumb`, `ant-menu`
   - 反馈：`ant-tag`, `ant-pagination`, `ant-modal`, `ant-drawer`
3. **Tailwind 仅用于页面级布局**：如 flex、grid、间距
4. **不要使用 `@apply`**：在 CDN 模式下不生效
5. **使用 Ant Design 4.x 配色**：`#1890ff` 为主色
6. **抽屉/弹窗合并到主页面**：不再单独生成独立 HTML 文件
7. **输出目录**：`.dev/prototype/`
8. **继承现有风格**：生成时自动读取现有页面提取配色
