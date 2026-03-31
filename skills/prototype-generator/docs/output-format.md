# 原型HTML输出格式规范

## 文件结构

**必须使用真正的 Ant Design CSS，而不是 Tailwind 模拟。**

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
  <style>
    /* 仅用于页面级布局，不覆盖 antd 组件样式 */
    .prototype-container {
      width: 1200px;
      min-height: 100vh;
      background: #f0f2f5;
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
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
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
<body>
  <div style="display: flex; height: 100vh;">
    <!-- 左侧原型（1200px） -->
    <div class="prototype-container" style="overflow-y: auto;">
      <!-- 使用 antd 原生类名构建页面 -->
    </div>

    <!-- 右侧说明 -->
    <div class="doc-panel">
      <!-- 交互说明 -->
    </div>
  </div>
</body>
</html>
```

## 左侧原型页面结构

### 1. 标准后台布局

```html
<div class="ant-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <header class="ant-layout-header" style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); height: 64px;">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">L</div>
      <span style="font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85);">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <div style="width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%;"></div>
    </div>
  </header>

  <div style="display: flex;">
    <!-- 侧边栏 -->
    <aside style="background: #001529; width: 200px; flex-shrink: 0; min-height: calc(100vh - 64px);">
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
    <main style="flex: 1; padding: 24px; background: #f0f2f5;">
      <!-- 面包屑 -->
      <div class="ant-breadcrumb" style="margin-bottom: 16px;">
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.45);">首页</span>
        <span class="ant-breadcrumb-separator">/</span>
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.85);">当前页面</span>
      </div>

      <!-- 页面标题 -->
      <h1 style="font-size: 20px; font-weight: 500; color: rgba(0,0,0,0.85); margin-bottom: 24px;">页面标题</h1>

      <!-- 内容区 -->
      <div class="ant-card">
        <div class="ant-card-body">
          <!-- 页面内容 -->
        </div>
      </div>
    </main>
  </div>
</div>
```

### 2. 列表页内容结构

```html
<!-- 筛选卡 -->
<div class="ant-card" style="margin-bottom: 24px;">
  <div class="ant-card-body">
    <div style="display: flex; gap: 16px; flex-wrap: wrap; align-items: center;">
      <input class="ant-input" placeholder="请输入关键词" style="width: 200px;">
      <div class="ant-select" style="width: 150px;">
        <div class="ant-select-selector">
          <span class="ant-select-selection-item">全部状态</span>
        </div>
      </div>
      <button class="ant-btn ant-btn-primary">
        <span>🔍</span>
        <span style="margin-left: 4px;">搜索</span>
      </button>
      <button class="ant-btn">
        <span>🔄</span>
        <span style="margin-left: 4px;">重置</span>
      </button>
    </div>
  </div>
</div>

<!-- 操作栏 -->
<div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
  <div style="display: flex; gap: 8px;">
    <button class="ant-btn ant-btn-primary">
      <span>➕</span>
      <span style="margin-left: 4px;">新增</span>
    </button>
    <button class="ant-btn">
      <span>📥</span>
      <span style="margin-left: 4px;">导出</span>
    </button>
  </div>
</div>

<!-- 表格 -->
<div class="ant-card">
  <div class="ant-table-wrapper">
    <div class="ant-spin-nested-loading">
      <div class="ant-spin-container">
        <div class="ant-table">
          <div class="ant-table-container">
            <div class="ant-table-content">
              <table style="table-layout: auto;">
                <thead class="ant-table-thead">
                  <tr>
                    <th class="ant-table-cell" style="padding: 12px 16px;">名称</th>
                    <th class="ant-table-cell" style="padding: 12px 16px;">状态</th>
                    <th class="ant-table-cell" style="padding: 12px 16px;">创建时间</th>
                    <th class="ant-table-cell" style="padding: 12px 16px;">操作</th>
                  </tr>
                </thead>
                <tbody class="ant-table-tbody">
                  <tr class="ant-table-row">
                    <td class="ant-table-cell" style="padding: 12px 16px;">示例数据1</td>
                    <td class="ant-table-cell" style="padding: 12px 16px;">
                      <span class="ant-tag ant-tag-success">启用</span>
                    </td>
                    <td class="ant-table-cell" style="padding: 12px 16px; color: rgba(0,0,0,0.45);">2024-03-25</td>
                    <td class="ant-table-cell" style="padding: 12px 16px;">
                      <a style="color: #1890ff; cursor: pointer;">编辑</a>
                      <span style="margin: 0 8px; color: #d9d9d9;">|</span>
                      <a style="color: #1890ff; cursor: pointer;">详情</a>
                      <span style="margin: 0 8px; color: #d9d9d9;">|</span>
                      <a style="color: #ff4d4f; cursor: pointer;">删除</a>
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
        <button class="ant-pagination-item-link" disabled>
          <span>&lt;</span>
        </button>
      </li>
      <li class="ant-pagination-item ant-pagination-item-1 ant-pagination-item-active">
        <a>1</a>
      </li>
      <li class="ant-pagination-item">
        <a>2</a>
      </li>
      <li class="ant-pagination-next">
        <button class="ant-pagination-item-link">
          <span>&gt;</span>
        </button>
      </li>
    </ul>
  </div>
</div>
```

### 3. 表单页内容结构

```html
<div class="ant-card">
  <div class="ant-card-body" style="padding: 24px;">
    <form>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <div>
          <div style="margin-bottom: 8px;">
            <label style="color: rgba(0,0,0,0.85); font-weight: 500;">
              字段名称 <span style="color: #ff4d4f;">*</span>
            </label>
          </div>
          <input class="ant-input" placeholder="请输入" style="width: 100%;">
          <div style="margin-top: 4px; font-size: 12px; color: rgba(0,0,0,0.45);">字段说明提示</div>
        </div>

        <div>
          <div style="margin-bottom: 8px;">
            <label style="color: rgba(0,0,0,0.85); font-weight: 500;">选择项</label>
          </div>
          <div class="ant-select" style="width: 100%;">
            <div class="ant-select-selector">
              <span class="ant-select-selection-item">选项一</span>
            </div>
          </div>
        </div>
      </div>

      <div style="margin-top: 24px;">
        <div style="margin-bottom: 8px;">
          <label style="color: rgba(0,0,0,0.85); font-weight: 500;">文本域</label>
        </div>
        <textarea class="ant-input" placeholder="请输入" style="width: 100%; min-height: 100px; resize: vertical;"></textarea>
      </div>

      <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #f0f0f0; text-align: center;">
        <button type="button" class="ant-btn" style="margin-right: 8px;">取消</button>
        <button type="button" class="ant-btn ant-btn-primary">提交</button>
      </div>
    </form>
  </div>
</div>
```

### 4. 抽屉组件

```html
<!-- 遮罩 -->
<div style="position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000;" onclick="closeDrawer()"></div>

<!-- 抽屉 -->
<div style="position: fixed; top: 0; right: 0; width: 520px; height: 100vh; background: #fff; z-index: 1001; box-shadow: -2px 0 8px rgba(0,0,0,0.15);">
  <div style="display: flex; flex-direction: column; height: 100%;">
    <!-- 头部 -->
    <div style="padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;">
      <div style="font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85);">抽屉标题</div>
      <button class="ant-btn ant-btn-link" style="padding: 0;">
        <span style="font-size: 18px;">✕</span>
      </button>
    </div>

    <!-- 内容 -->
    <div style="flex: 1; padding: 24px; overflow-y: auto;">
      <!-- 表单或详情内容 -->
    </div>

    <!-- 底部 -->
    <div style="padding: 16px 24px; border-top: 1px solid #f0f0f0; text-align: right;">
      <button class="ant-btn" style="margin-right: 8px;">取消</button>
      <button class="ant-btn ant-btn-primary">确定</button>
    </div>
  </div>
</div>
```

## 右侧原型说明文档结构

```html
<div style="max-width: 600px;">
  <div class="doc-section">
    <div class="doc-title">页面交互说明</div>
    <p style="color: rgba(0,0,0,0.45); font-size: 14px; margin-bottom: 16px;">版本: v1.0 | 更新日期: 2024-03-25</p>
  </div>

  <div class="doc-section">
    <div class="doc-title">1. 页面概述</div>
    <p style="color: rgba(0,0,0,0.65); line-height: 1.6;">本页面用于{功能描述}。用户可以通过{操作方式}完成{目标}。</p>
  </div>

  <div class="doc-section">
    <div class="doc-title">2. 搜索区域</div>
    <div class="doc-item">
      <span class="doc-label">搜索按钮</span>
      <span class="doc-content">点击后根据输入条件筛选表格数据</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">重置按钮</span>
      <span class="doc-content">清空所有搜索条件，恢复初始列表状态</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">筛选字段</span>
      <span class="doc-content">支持按关键词、状态、时间范围筛选</span>
    </div>
  </div>

  <div class="doc-section">
    <div class="doc-title">3. 数据表格</div>
    <div class="doc-item">
      <span class="doc-label">列定义</span>
      <span class="doc-content">共X列，包括{列名列表}</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">排序</span>
      <span class="doc-content">支持按{字段}升序/降序排列</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">分页</span>
      <span class="doc-content">默认每页10条，支持10/20/50条切换</span>
    </div>
  </div>

  <div class="doc-section">
    <div class="doc-title">4. 操作按钮</div>
    <div class="doc-item">
      <span class="doc-label">新增</span>
      <span class="doc-content">点击打开抽屉表单，填写后提交创建新记录</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">编辑</span>
      <span class="doc-content">点击打开编辑表单，数据自动回显</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">删除</span>
      <span class="doc-content">点击弹出二次确认框，确认后删除记录</span>
    </div>
  </div>

  <div class="doc-section">
    <div class="doc-title">5. 边界场景</div>
    <div class="doc-item">
      <span class="doc-label">空数据</span>
      <span class="doc-content">表格无数据时展示空状态插画和提示文字</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">加载中</span>
      <span class="doc-content">数据加载时显示骨架屏</span>
    </div>
    <div class="doc-item">
      <span class="doc-label">错误提示</span>
      <span class="doc-content">操作失败时顶部显示错误提示消息</span>
    </div>
  </div>
</div>
```

## Mock 交互脚本

```javascript
<script>
// 搜索
function mockSearch() {
  console.log('[Mock] 执行搜索');
  alert('搜索成功（模拟）');
}

// 重置
function mockReset() {
  console.log('[Mock] 重置搜索条件');
}

// 新增
function mockAdd() {
  console.log('[Mock] 打开新增抽屉');
  openDrawer('新增');
}

// 编辑
function mockEdit(id) {
  console.log('[Mock] 编辑记录', id);
  openDrawer('编辑');
}

// 删除
function mockDelete(id) {
  if (confirm('确定要删除该记录吗？')) {
    console.log('[Mock] 删除记录', id);
    alert('删除成功（模拟）');
  }
}

// 提交表单
function mockSubmit() {
  console.log('[Mock] 提交表单');
  alert('提交成功（模拟）');
  closeDrawer();
}

// 打开抽屉
function openDrawer(title) {
  document.getElementById('drawer').style.display = 'block';
  document.getElementById('drawerMask').style.display = 'block';
}

// 关闭抽屉
function closeDrawer() {
  document.getElementById('drawer').style.display = 'none';
  document.getElementById('drawerMask').style.display = 'none';
}
</script>
```

## 重要规则

1. **必须使用 `antd.min.css`**：这是风格一致的基础
2. **使用原生 antd 类名**：如 `ant-btn`、`ant-input`、`ant-table`
3. **Tailwind 仅用于页面级布局**：如 flex、grid、间距
4. **不要使用 `@apply`**：在 CDN 模式下不生效
5. **使用 Ant Design 4.x 配色**：`#1890ff` 为主色
