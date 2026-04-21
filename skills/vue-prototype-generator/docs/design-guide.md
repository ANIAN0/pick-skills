# Ant Design Vue 原型设计规范

本规范专门用于指导 Vue 原型生成，确保所有原型页面风格统一。**基于 Ant Design Vue 官方样式**。

## 核心原则

**使用 Vue 3 + Ant Design Vue CDN 引入**：

```html
<!-- Vue 3 -->
<script src="https://cdn.jsdmirror.com/npm/vue@3/dist/vue.global.js"></script>

<!-- Ant Design Vue 样式 -->
<link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/reset.css" />
<link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.css" />

<!-- Ant Design Vue 组件 -->
<script src="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.js"></script>
```

## 配色方案（Ant Design Vue）

| 名称 | 色值 | CSS 变量 | 用途 |
|-----|------|---------|-----|
| Primary | `#1677ff` | `--ant-primary-color` | 主按钮、链接、选中态 |
| Success | `#52c41a` | `--ant-success-color` | 成功状态、启用标签 |
| Warning | `#faad14` | `--ant-warning-color` | 警告状态 |
| Error | `#ff4d4f` | `--ant-error-color` | 错误状态、危险操作 |
| Info | `#1677ff` | `--ant-info-color` | 信息提示 |

### 中性色
| 名称 | 色值 | 用途 |
|-----|------|-----|
| Text Primary | `rgba(0, 0, 0, 0.85` | success

## HTML 头部模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {页面名称}</title>
  <!-- Vue 3 -->
  <script src="https://cdn.jsdmirror.com/npm/vue@3/dist/vue.global.js"></script>

  <!-- Ant Design Vue CSS -->
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/reset.css" />
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.css" />
  <!-- Ant Design Vue JS -->
  <script src="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.js"></script>
  <!-- Ant Design Icons -->
  <script src="https://cdn.jsdmirror.com/npm/@ant-design/icons-vue@6.1.0/dist/index.umd.min.js"></script>

  ## 组件使用规范

  ### 按钮

  ```html
  <style>
    <script>
      /* 成功n


```html
<!-- 主按钮 -->
<a-button type="primary">主要按钮</a-button>

<!-- 默认按钮 -->
<a-button>默认按钮</a-button>

<!-- 危险按钮 -->
<a-button danger>删除</a-button>

<!-- 链接按钮 -->
<a-button type="link">编辑</a-button>

<!-- 带图标的按钮 -->
<a-button type="primary">
  <plus-outlined />新增
</a-button>
```

### 输入框

```html
<!-- 基础输入框 -->
<a-input v-model:value="input" placeholder="请输入" />

<!-- 带前缀的输入框 -->
<a-input v-model:value="input" placeholder="搜索">
  <template #prefix>
    <search-outlined />
  </template>
</a-input>

<!-- 清空按钮 -->
<a-input v-model:value="input" placeholder="请输入" allow-clear />

<!-- 密码输入框 -->
<a-input-password v-model:value="password" placeholder="请输入密码" />

<!-- 文本域 -->
<a-textarea v-model:value="textarea" :rows="3" placeholder="请输入" />
```

### 下拉选择

```html
<a-select v-model:value="value" placeholder="请选择" allow-clear style="width: 200px;">
  <a-select-option value="">全部状态</a-select-option>
  <a-select-option value="enabled">启用</a-select-option>
  <a-select-option value="disabled">禁用</a-select-option>
</a-select>
```

### 表格

```html
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
```

### 标签

```html
<!-- 状态标签 - 启用 -->
<a-tag color="success">启用</a-tag>

<!-- 状态标签 - 禁用 -->
<a-tag color="error">禁用</a-tag>

<!-- 状态标签 - 待审核 -->
<a-tag color="warning">待审核</a-tag>

<!-- 状态标签 - 默认 -->
<a-tag>默认</a-tag>

<!-- 边框标签 -->
<a-tag color="success" bordered>启用</a-tag>
```

### 卡片

```html
<a-card>
  <template #title>
    <span>卡片标题</span>
  </template>
  卡片内容
</a-card>
```

### 抽屉

```html
<a-drawer
  v-model:open="drawerVisible"
  title="抽屉标题"
  width="500px"
>
  <a-form :model="formData" layout="vertical">
    <a-form-item label="名称" :required="true">
      <a-input v-model:value="formData.name" placeholder="请输入名称" />
    </a-form-item>
  </a-form>
  <template #footer>
    <a-button @click="drawerVisible = false">取消</a-button>
    <a-button type="primary" @click="handleSave" style="margin-left: 8px;">确定</a-button>
  </template>
</a-drawer>
```

### 对话框

```html
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

### 分页

```html
<a-pagination
  v-model:current="currentPage"
  v-model:page-size="pageSize"
  :total="total"
  :page-size-options="['10', '20', '50']"
  show-size-changer
  show-quick-jumper
  show-total
  style="margin-top: 20px; text-align: right;"
/>
```

### 表单

```html
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
      <a-select-option value="enabled">启用</a-select-option>
      <a-select-option value="disabled">禁用</a-select-option>
    </a-select>
  </a-form-item>

  <a-form-item>
    <a-button type="primary" @click="handleSubmit">提交</a-button>
    <a-button @click="handleCancel" style="margin-left: 8px;">取消</a-button>
  </a-form-item>
</a-form>
```

### 描述列表

```html
<a-descriptions :column="2" bordered>
  <a-descriptions-item label="用户名">admin</a-descriptions-item>
  <a-descriptions-item label="邮箱">admin@example.com</a-descriptions-item>
  <a-descriptions-item label="状态">
    <a-tag color="success">启用</a-tag>
  </a-descriptions-item>
</a-descriptions>
```

## 布局模式

### 标准后台布局

```html
<a-layout style="min-height: 100vh;">
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
    <a-layout-sider width="200px" style="background: #001529;">
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
          <span>用户管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <!-- 主内容 -->
    <a-layout-content style="background: #f0f2f5; padding: 24px;">
      <!-- 面包屑 -->
      <a-breadcrumb style="margin-bottom: 16px;">
        <a-breadcrumb-item>首页</a-breadcrumb-item>
        <a-breadcrumb-item>用户管理</a-breadcrumb-item>
      </a-breadcrumb>

      <!-- 页面内容 -->
    </a-layout-content>
  </a-layout>
</a-layout>
```

## 消息提示

```javascript
// 成功提示
message.success('操作成功');

// 错误提示
message.error('操作失败');

// 警告提示
message.warning('请确认信息');

// 普通提示
message.info('提示信息');

// 确认对话框
Modal.confirm({
  title: '确定要删除吗？',
  content: '此操作不可撤销。',
  okText: '确定',
  cancelText: '取消',
  onOk: () => {
    message.success('删除成功');
  }
});
```

## 图标使用

```html
<!-- 使用 Ant Design 图标 -->
<home-outlined />
<unordered-list-outlined />
<file-text-outlined />
<search-outlined />
<plus-outlined />
<edit-outlined />
<delete-outlined />
<exclamation-circle-outlined />
<user-outlined />
```

在 script 中导入：

```javascript
const { HomeOutlined, UnorderedListOutlined, FileTextOutlined, SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined, ExclamationCircleOutlined, UserOutlined } = icons;

// 注册组件
app.component('HomeOutlined', HomeOutlined);
app.component('UnorderedListOutlined', UnorderedListOutlined);
```

## 完整页面示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>原型 - 用户列表</title>
  <script src="https://cdn.jsdmirror.com/npm/vue@3/dist/vue.global.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/reset.css" />
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.css" />
  <script src="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.js"></script>
  <script src="https://cdn.jsdmirror.com/npm/@ant-design/icons-vue@6.1.0/dist/index.umd.min.js"></script>
  <style>
    .prototype-container { display: flex; height: 100vh; overflow: hidden; }
    .prototype-left { width: 1200px; background: white; overflow: auto; flex-shrink: 0; }
    .prototype-right { flex: 1; background: #f5f5f5; padding: 24px; overflow: auto; }
  </style>
</head>
<body>
  <div class="prototype-container">
    <!-- 左侧原型 -->
    <div class="prototype-left" id="app">
      <a-layout style="min-height: 100vh;">
        <a-layout-header style="background: #fff; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08);">
          <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 32px; height: 32px; background: #1677ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">S</div>
            <span style="font-size: 18px; font-weight: 500;">系统后台</span>
          </div>
          <div style="display: flex; align-items: center; gap: 16px;">
            <span style="color: rgba(0,0,0,0.65);">管理员</span>
            <a-avatar :size="32" icon="user" />
          </div>
        </a-layout-header>

        <a-layout>
          <a-layout-sider width="200px" style="background: #001529;">
            <a-menu mode="inline" theme="dark" :selected-keys="['2']" style="border-right: none;">
              <a-menu-item key="1">
                <home-outlined />
                <span>首页</span>
              </a-menu-item>
              <a-menu-item key="2">
                <unordered-list-outlined />
                <span>用户管理</span>
              </a-menu-item>
            </a-menu>
          </a-layout-sider>

          <a-layout-content style="background: #f0f2f5; padding: 24px;">
            <a-breadcrumb style="margin-bottom: 16px;">
              <a-breadcrumb-item>首页</a-breadcrumb-item>
              <a-breadcrumb-item>用户管理</a-breadcrumb-item>
            </a-breadcrumb>

            <!-- 搜索卡片 -->
            <a-card style="margin-bottom: 24px;">
              <a-form :model="searchForm" layout="inline">
                <a-form-item label="用户名" name="username">
                  <a-input v-model:value="searchForm.username" placeholder="请输入用户名" allow-clear />
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
            <div style="margin-bottom: 16px;">
              <a-button type="primary" @click="openDrawer('add')">
                <plus-outlined />新增用户
              </a-button>
            </div>

            <!-- 表格 -->
            <a-card>
              <a-table :columns="columns" :data-source="tableData" :pagination="false" bordered>
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'action'">
                    <a-button type="link" @click="openDrawer('edit', record)">编辑</a-button>
                    <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
                  </template>
                  <template v-else-if="column.key === 'status'">
                    <a-tag :color="record.status === '启用' ? 'success' : 'error'">{{ record.status }}</a-tag>
                  </template>
                </template>
              </a-table>

              <a-pagination
                v-model:current="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                :page-size-options="['10', '20', '50']"
                show-size-changer
                show-quick-jumper
                show-total
                style="margin-top: 20px; text-align: right;"
              />
            </a-card>
          </a-layout-content>
        </a-layout>
      </a-layout>

      <!-- 抽屉 -->
      <a-drawer v-model:open="drawerVisible" :title="drawerTitle" width="500px">
        <a-form :model="formData" layout="vertical">
          <a-form-item label="用户名" name="username" :required="true">
            <a-input v-model:value="formData.username" placeholder="请输入用户名" />
          </a-form-item>
          <a-form-item label="邮箱" name="email" :required="true">
            <a-input v-model:value="formData.email" placeholder="请输入邮箱" />
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
    </div>

    <!-- 右侧说明 -->
    <div class="prototype-right">
      <!-- 说明内容 -->
    </div>
  </div>

  <script>
    const { createApp, ref, reactive } = Vue;
    const { message, Modal } = antd;
    const { HomeOutlined, UnorderedListOutlined, UserOutlined, SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined, ExclamationCircleOutlined } = icons;

    const app = createApp({
      setup() {
        const searchForm = reactive({ username: '', status: '' });
        const tableData = ref([
          { key: 1, username: 'admin', email: 'admin@example.com', status: '启用' },
          { key: 2, username: 'user1', email: 'user1@example.com', status: '禁用' },
        ]);
        const currentPage = ref(1);
        const pageSize = ref(10);
        const total = ref(100);
        const drawerVisible = ref(false);
        const drawerTitle = ref('新增用户');
        const formData = reactive({ username: '', email: '', status: 'enabled' });

        const columns = [
          { title: '用户名', dataIndex: 'username', key: 'username' },
          { title: '邮箱', dataIndex: 'email', key: 'email' },
          { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
          { title: '操作', key: 'action', width: 150 },
        ];

        const handleSearch = () => message.success('搜索成功（模拟）');
        const handleReset = () => {
          searchForm.username = '';
          searchForm.status = '';
          message.success('重置成功');
        };
        const openDrawer = (type, row) => {
          drawerTitle.value = type === 'add' ? '新增用户' : '编辑用户';
          drawerVisible.value = true;
        };
        const handleSave = () => {
          message.success('保存成功（模拟）');
          drawerVisible.value = false;
        };
        const handleDelete = (row) => {
          Modal.confirm({
            title: '确认删除',
            content: '确定要删除该用户吗？此操作不可撤销。',
            okText: '确定',
            cancelText: '取消',
            onOk: () => message.success('删除成功（模拟）')
          });
        };

        return {
          searchForm, tableData, currentPage, pageSize, total,
          drawerVisible, drawerTitle, formData, columns,
          handleSearch, handleReset, openDrawer, handleSave, handleDelete
        };
      }
    });

    app.use(antd);
    app.component('HomeOutlined', HomeOutlined);
    app.component('UnorderedListOutlined', UnorderedListOutlined);
    app.component('UserOutlined', UserOutlined);
    app.component('SearchOutlined', SearchOutlined);
    app.component('PlusOutlined', PlusOutlined);
    app.component('EditOutlined', EditOutlined);
    app.component('DeleteOutlined', DeleteOutlined);
    app.component('ExclamationCircleOutlined', ExclamationCircleOutlined;

    app.mount('#app');
  </script>
</body>
</html>
```

## 重要提醒

1. **使用 Ant Design Vue CDN 引入**：`antd.min.js` 包含完整组件
2. **使用 Ant Design Vue 组件标签**：`a-button`、`a-input`、`a-table` 等
3. **使用 Vue 3 Composition API**：`setup()` 函数返回响应式数据和方法
4. **使用 ref/reactive 定义响应式数据**
5. **使用 message/Modal 进行交互反馈**
6. **使用 Ant Design 标准色**：`#1677ff` 为主色
7. **抽屉/弹窗使用 v-model:open 控制显示**：绑定 `visible` 变量
8. **表格操作列通过 bodyCell 插槽自定义**：`#bodyCell="{ column, record
9. **分页使用 a-pagination 组件**：绑定 `current` 和 `pageSize`
10. **图标需从 icons 对象导入并注册**：使用 `app.component()`
