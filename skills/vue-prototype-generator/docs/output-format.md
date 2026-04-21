# Vue 原型HTML输出格式规范

## 文件输出位置

**默认输出目录：** `.dev/prototype/`

## 文件结构

生成的 HTML 文件使用 **Vue 3 + Ant Design Vue**（通过 CDN 引入），可直接在浏览器中打开预览。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {页面名称}</title>
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
    <!-- 左侧原型（1200px固定宽度） -->
    <div class="prototype-left" id="app">
      <!-- Vue 3 应用内容 -->
    </div>

    <!-- 右侧说明 -->
    <div class="prototype-right">
      <!-- 交互说明文档 -->
    </div>
  </div>

  <script>
    // Vue 3 Composition API 代码
    const { createApp, ref, reactive } = Vue;
    const { message, Modal } = antd;
    // ... 应用逻辑
  </script>
</body>
</html>
```

## 页面级布局样式

```html
<style>
  /* 页面级布局 */
  .prototype-container {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }
  .prototype-left {
    width: 1200px;
    background: white;
    overflow: auto;
    flex-shrink: 0;
    position: relative;
  }
  .prototype-right {
    flex: 1;
    background: #f5f5f5;
    padding: 24px;
    overflow: auto;
  }

  /* 右侧说明文档样式 */
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
    color: rgba(0,0,0,0.85);
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
</style>
```

## Ant Design Vue 标准后台布局

```html
<div class="common-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <a-layout-header style="background: #fff; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08);">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1677ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">S</div>
      <span style="font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85);">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <a-avatar :size="32" icon="user" />
    </div>
  </a-layout-header>

  <a-layout>
    <!-- 侧边栏 -->
    <a-layout-sider width="200px" style="background: #001529; min-height: calc(100vh - 64px);">
      <a-menu
        mode="inline"
        theme="dark"
        :selected-keys="['1']"
        style="border-right: none;"
      >
        <a-menu-item key="1">
          <home-outlined />
          <span>首页</span>
        </a-menu-item>
        <a-menu-item key="2">
          <unordered-list-outlined />
          <span>当前页面</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <!-- 主内容 -->
    <a-layout-content style="background: #f0f2f5; padding: 24px;">
      <!-- 面包屑 -->
      <a-breadcrumb style="margin-bottom: 16px;">
        <a-breadcrumb-item>首页</a-breadcrumb-item>
        <a-breadcrumb-item>当前页面</a-breadcrumb-item>
      </a-breadcrumb>

      <!-- 页面内容 -->
    </a-layout-content>
  </a-layout>
</div>
```

## 列表页结构

```html
<!-- 搜索卡片 -->
<a-card style="margin-bottom: 24px;">
  <a-form :model="searchForm" layout="inline">
    <a-form-item label="关键词" name="keyword">
      <a-input v-model:value="searchForm.keyword" placeholder="请输入关键词" allow-clear style="width: 200px;" />
    </a-form-item>
    <a-form-item label="状态" name="status">
      <a-select v-model:value="searchForm.status" placeholder="请选择状态" allow-clear style="width: 200px;">
        <a-select-option value="">全部</a-select-option>
        <a-select-option value="enabled">启用</a-select-option>
        <a-select-option value="disabled">禁用</a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item>
      <a-button type="primary" @click="handleSearch">
        <search-outlined />搜索
      </a-button>
      <a-button @click="handleReset" style="margin-left: 8px;">重置</a-button>
    </a-form-item>
  </a-form>
</a-card>

<!-- 操作栏 -->
<a-card style="margin-bottom: 16px;">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
      <a-button type="primary" @click="openDrawer('add')">新增</a-button>
      <a-button @click="handleExport" style="margin-left: 8px;">导出</a-button>
    </div>
  </div>
</a-card>

<!-- 表格卡片 -->
<a-card>
  <a-table :columns="columns" :data-source="tableData" :pagination="false" bordered>
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'action'">
        <a-button type="link" @click="handleEdit(record)">编辑</a-button>
        <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
      </template>
      <template v-else-if="column.key === 'status'">
        <a-tag :color="record.status === '启用' ? 'success' : 'error'">{{ record.status }}</a-tag>
      </template>
    </template>
  </a-table>

  <!-- 分页 -->
  <a-pagination
    v-model:current="currentPage"
    v-model:page-size="pageSize"
    :total="total"
    :page-size-options="['10', '20', '50']"
    show-size-changer
    show-quick-jumper
    show-total
    :total-text="'共 ' + total + ' 条'"
    style="margin-top: 20px; text-align: right;"
  />
</a-card>
```

## 表单页结构

```html
<a-card style="max-width: 800px;">
  <template #title>
    <span style="font-size: 16px; font-weight: 500;">表单标题</span>
  </template>

  <a-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    layout="vertical"
  >
    <a-form-item label="用户名" name="username" :required="true">
      <a-input v-model:value="formData.username" placeholder="请输入用户名" />
    </a-form-item>

    <a-form-item label="状态" name="status">
      <a-select v-model:value="formData.status" placeholder="请选择状态" style="width: 100%;">
        <a-select-option value="">请选择</a-select-option>
        <a-select-option value="enabled">启用</a-select-option>
        <a-select-option value="disabled">禁用</a-select-option>
      </a-select>
    </a-form-item>

    <a-form-item>
      <a-button type="primary" @click="handleSubmit">提交</a-button>
      <a-button @click="handleCancel" style="margin-left: 8px;">取消</a-button>
    </a-form-item>
  </a-form>
</a-card>
```

## 详情页结构

```html
<!-- 操作栏 -->
<div style="margin-bottom: 24px;">
  <a-button type="primary" @click="handleEdit">编辑</a-button>
  <a-button @click="handleBack" style="margin-left: 8px;">返回</a-button>
</div>

<!-- 详情卡片 -->
<a-card style="margin-bottom: 24px;">
  <template #title>
    <span style="font-size: 16px; font-weight: 500;">基本信息</span>
  </template>
  <a-descriptions :column="2" bordered>
    <a-descriptions-item label="用户名">{{ detailData.username }}</a-descriptions-item>
    <a-descriptions-item label="邮箱">{{ detailData.email }}</a-descriptions-item>
    <a-descriptions-item label="状态">
      <a-tag :color="detailData.status === '启用' ? 'success' : 'error'">{{ detailData.status }}</a-tag>
    </a-descriptions-item>
  </a-descriptions>
</a-card>
```

## 抽屉组件（合并到主页面）

```html
<!-- 抽屉：新增/编辑 -->
<a-drawer
  v-model:open="drawerVisible"
  :title="drawerTitle"
  width="500px"
>
  <a-form :model="formData" layout="vertical">
    <a-form-item label="名称" name="name" :required="true">
      <a-input v-model:value="formData.name" placeholder="请输入名称" />
    </a-form-item>
    <a-form-item label="状态" name="status">
      <a-select v-model:value="formData.status" placeholder="请选择状态" style="width: 100%;">
        <a-select-option value="enabled">启用</a-select-option>
        <a-select-option value="disabled">禁用</a-select-option>
      </a-select>
    </a-form-item>
  </a-form>
  <template #footer>
    <a-button @click="drawerVisible = false">取消</a-button>
    <a-button type="primary" @click="handleSave" style="margin-left: 8px;">确定</a-button>
  </template>
</a-drawer>
```

## 弹窗组件（合并到主页面）

```html
<!-- 弹窗：删除确认 -->
<a-modal
  v-model:open="modalVisible"
  title="删除确认"
  width="420px"
  @ok="confirmDelete"
>
  <div style="display: flex; align-items: center;">
    <exclamation-circle-outlined style="font-size: 22px; color: #faad14; margin-right: 12px;" />
    <span>确定要删除该记录吗？此操作不可撤销。</span>
  </div>
</a-modal>
```

## Vue 3 脚本部分

```javascript
<script>
  const { createApp, ref, reactive } = Vue;
  const { message, Modal } = antd;

  const app = createApp({
    setup() {
      // ========== 响应式数据 ==========
      // 搜索表单
      const searchForm = reactive({
        keyword: '',
        status: ''
      });

      // 表格数据
      const tableData = ref([
        { key: 1, name: '示例数据1', status: '启用', createTime: '2024-03-25' },
        { key: 2, name: '示例数据2', status: '禁用', createTime: '2024-03-24' },
        { key: 3, name: '示例数据3', status: '启用', createTime: '2024-03-23' },
      ]);

      // 分页
      const currentPage = ref(1);
      const pageSize = ref(10);
      const total = ref(100);

      // 抽屉控制
      const drawerVisible = ref(false);
      const drawerTitle = ref('新增');
      const formData = reactive({
        name: '',
        status: ''
      });

      // 弹窗控制
      const modalVisible = ref(false);
      const currentRow = ref(null);

      // ========== 方法 ==========
      const handleSearch = () => {
        message.success('搜索成功（模拟）');
      };

      const handleReset = () => {
        searchForm.keyword = '';
        searchForm.status = '';
        message.success('重置成功');
      };

      const openDrawer = (type, row = null) => {
        drawerTitle.value = type === 'add' ? '新增' : '编辑';
        if (row) {
          Object.assign(formData, row);
        } else {
          formData.name = '';
          formData.status = '';
        }
        drawerVisible.value = true;
      };

      const handleSave = () => {
        message.success('保存成功（模拟）');
        drawerVisible.value = false;
      };

      const handleDelete = (row) => {
        currentRow.value = row;
        modalVisible.value = true;
      };

      const confirmDelete = () => {
        message.success('删除成功（模拟）');
        modalVisible.value = false;
      };

      return {
        searchForm,
        tableData,
        currentPage,
        pageSize,
        total,
        drawerVisible,
        drawerTitle,
        formData,
        modalVisible,
        handleSearch,
        handleReset,
        openDrawer,
        handleSave,
        handleDelete,
        confirmDelete
      };
    }
  });

  app.use(antd);
  app.mount('#app');
</script>
```

## 右侧说明文档结构

```html
<div class="prototype-right">
  <div style="max-width: 600px;">
    <div class="doc-section">
      <div class="doc-title">页面交互说明</div>
      <p style="color: rgba(0,0,0,0.45); font-size: 14px;">版本: v1.0 | 更新日期: 2024-03-25</p>
    </div>

    <div class="doc-section">
      <div class="doc-title">1. 页面概述</div>
      <p style="color: rgba(0,0,0,0.65); line-height: 1.6;">本页面为xxx列表原型...</p>
    </div>

    <div class="doc-section">
      <div class="doc-title">2. 布局结构</div>
      <p>布局类型: 顶栏+侧边栏+内容区</p>
    </div>

    <div class="doc-section">
      <div class="doc-title">3. 交互逻辑</div>
      <ul style="list-style: disc; padding-left: 20px;">
        <li><strong>搜索:</strong> 输入关键词后点击搜索按钮</li>
        <li><strong>新增:</strong> 点击新增按钮打开抽屉</li>
        <li><strong>编辑:</strong> 点击编辑链接打开抽屉</li>
        <li><strong>删除:</strong> 点击删除链接弹出确认框</li>
      </ul>
    </div>

    <div class="doc-section">
      <div class="doc-title">4. 边界场景</div>
      <ul style="list-style: disc; padding-left: 20px;">
        <li>空数据时显示空状态</li>
        <li>加载中显示骨架屏</li>
      </ul>
    </div>
  </div>
</div>
```

## Ant Design Vue 组件清单

### 基础组件
- `a-button` - 按钮
- `a-input` - 输入框
- `a-select` / `a-select-option` - 选择器
- `a-date-picker` - 日期选择器
- `a-tag` - 标签
- `a-card` - 卡片
- `a-avatar` - 头像

### 表单组件
- `a-form` / `a-form-item` - 表单
- `a-input` (type="textarea") - 文本域
- `a-radio` / `a-radio-group` - 单选
- `a-checkbox` / `a-checkbox-group` - 多选
- `a-switch` - 开关

### 数据展示
- `a-table` / `a-table-column` - 表格
- `a-pagination` - 分页
- `a-descriptions` / `a-descriptions-item` - 描述列表
- `a-empty` - 空状态

### 导航
- `a-breadcrumb` / `a-breadcrumb-item` - 面包屑
- `a-menu` / `a-menu-item` - 菜单
- `a-layout` / `a-layout-header` / `a-layout-sider` / `a-layout-content` - 布局

### 反馈
- `message` - 消息提示
- `Modal` - 消息确认框
- `a-modal` - 对话框
- `a-drawer` - 抽屉

### 布局
- `a-layout` - 布局容器
- `a-layout-header` - 顶栏
- `a-layout-sider` - 侧边栏
- `a-layout-content` - 主内容区

### 图标（需导入）
```javascript
const { HomeOutlined, UnorderedListOutlined, FileTextOutlined, SearchOutlined } = icons;
```

## 命名规范

### 文件名
- PascalCase 命名：`VuePrototypeUserList.html`
- 前缀 `VuePrototype` + 页面名称
- 版本号：`VuePrototypeUserListV2.html`

### 变量名
- 响应式数据：`xxxForm`, `xxxData`
- 控制变量：`xxxVisible`（如 `drawerVisible`, `modalVisible`）
- 方法：`handleXxx`（如 `handleSearch`, `handleSubmit`）

## 重要规则

1. **使用 Vue 3 全局构建版**：通过 CDN 引入 `vue.global.js`
2. **使用 Ant Design Vue 完整版**：通过 CDN 引入 `antd.min.js`
3. **HTML 可直接预览**：生成文件双击即可在浏览器打开
4. **左侧原型区域**：固定宽度 1200px
5. **抽屉/弹窗合并到主页面**：使用 `v-model:open` 控制显示
6. **输出目录**：`.dev/prototype/`
7. **继承现有风格**：生成时自动读取现有页面提取配色

## CDN 地址

```html
<!-- Vue 3 -->
<script src="https://cdn.jsdmirror.com/npm/vue@3/dist/vue.global.js"></script>

<!-- Ant Design Vue CSS -->
<link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/reset.css" />
<link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.css" />

<!-- Ant Design Vue JS -->
<script src="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.js"></script>

<!-- Ant Design Icons（可选） -->
<script src="https://cdn.jsdmirror.com/npm/@ant-design/icons-vue@6.1.0/dist/index.umd.min.js"></script>
```
