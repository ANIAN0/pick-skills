# Vue 原型设计规范

本规范用于指导 Vue 原型生成，确保所有原型页面使用与项目前端完全一致的技术栈和设计风格。

## 核心原则

### 技术栈一致性

原型项目使用与主项目**完全一致的依赖版本**：

| 技术 | 版本 | 用途 |
|-----|------|-----|
| Vue | 3.3.4 | 前端框架 |
| TypeScript | ~5.9.3 | 类型系统 |
| Ant Design Vue | 3.2.20 | UI 组件库 |
| Rsbuild | ^1.6.15 | 构建工具 |
| Vue Router | 5.0.1 | 路由管理 |
| Pinia | 3.0.4 | 状态管理 |
| Dayjs | ^1.11.19 | 日期处理 |
| Lodash-es | ^4.17.23 | 工具函数 |

**重要提醒**：必须使用 Ant Design Vue **3.x** 版本，而非 4.x。API 有显著差异。

### 启动方式

原型项目需要在指定目录下使用 `pnpm dev` 启动开发服务器：

```bash
cd docs/prototype/{prototype-name}
pnpm install
pnpm dev
```

服务默认在 **3005 端口**启动，访问 http://localhost:3005 查看原型。

## 项目结构

```
docs/prototype/{prototype-name}/
├── package.json              # 依赖配置
├── rsbuild.config.ts         # Rsbuild配置
├── tsconfig.json             # TypeScript配置
├── index.html                # 入口HTML
├── src/
│   ├── main.ts               # 入口文件
│   ├── App.vue               # 根组件
│   ├── env.d.ts              # 类型声明
│   ├── api/
│   │   └── mock-api.ts       # Mock API层
│   ├── hooks/                # Hooks（简化版）
│   │   ├── useDrawer.ts
│   │   └── useForm.ts
│   ├── pages/                # 页面目录
│   │   └── {page-name}/
│   │       ├── index.vue
│   │       ├── data.ts
│   │       └── components/
│   │           └── EditForm.vue
│   ├── router/               # 路由配置
│   │   └── index.ts
│   ├── styles/               # 全局样式
│   ├── utils/                # 工具函数
│   └── types/                # 类型定义
```

## 组件使用规范

### Ant Design Vue 3.x 组件

#### 按钮 Button

```vue
<template>
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
</template>
```

**Ant Design Vue 3.x 注意事项**（与 4.x 的区别）：
- 使用 `v-model:visible` 控制弹窗/抽屉显示（而非 `v-model:open`）
- 图标需要单独导入和注册

#### 输入框 Input

```vue
<template>
  <!-- 基础输入框 -->
  <a-input v-model:value="input" placeholder="请输入" />

  <!-- 带清空按钮 -->
  <a-input v-model:value="input" placeholder="请输入" allow-clear />

  <!-- 密码输入框 -->
  <a-input-password v-model:value="password" placeholder="请输入密码" />

  <!-- 文本域 -->
  <a-textarea v-model:value="textarea" :rows="3" placeholder="请输入" />
</template>
```

#### 下拉选择 Select

```vue
<template>
  <a-select v-model:value="value" placeholder="请选择" allow-clear style="width: 200px;">
    <a-select-option value="">全部状态</a-select-option>
    <a-select-option value="enabled">启用</a-select-option>
    <a-select-option value="disabled">禁用</a-select-option>
  </a-select>
</template>
```

#### 表格 Table

```vue
<template>
  <a-table
    :columns="columns"
    :data-source="tableData"
    :loading="loading"
    :pagination="false"
    row-key="id"
  >
    <template #bodyCell="{ column, record }">
      <template v-if="column.dataIndex === 'action'">
        <a-button type="link" @click="handleEdit(record)">编辑</a-button>
        <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
      </template>
      <template v-else-if="column.dataIndex === 'status'">
        <a-tag :color="record.status === 1 ? 'success' : 'error'">
          {{ record.status === 1 ? '启用' : '禁用' }}
        </a-tag>
      </template>
    </template>
  </a-table>
</template>
```

#### 标签 Tag

```vue
<template>
  <!-- 状态标签 - 启用 -->
  <a-tag color="success">启用</a-tag>

  <!-- 状态标签 - 禁用 -->
  <a-tag color="error">禁用</a-tag>

  <!-- 状态标签 - 待审核 -->
  <a-tag color="warning">待审核</a-tag>
</template>
```

#### 卡片 Card

```vue
<template>
  <a-card title="卡片标题" :bordered="false">
    卡片内容
  </a-card>
</template>
```

#### 抽屉 Drawer（3.x 版本）

**重要**：Ant Design Vue 3.x 使用 `v-model:visible` 而非 `v-model:open`：

```vue
<template>
  <a-drawer
    v-model:visible="drawerVisible"
    title="抽屉标题"
    width="500px"
    :destroy-on-close="true"
  >
    <a-form :model="formData" layout="vertical">
      <a-form-item label="名称" name="name" :required="true">
        <a-input v-model:value="formData.name" placeholder="请输入名称" />
      </a-form-item>
    </a-form>
    <template #footer>
      <a-button @click="drawerVisible = false">取消</a-button>
      <a-button type="primary" @click="handleSave" style="margin-left: 8px;">确定</a-button>
    </template>
  </a-drawer>
</template>
```

#### 对话框 Modal

```vue
<template>
  <a-modal
    v-model:visible="modalVisible"
    title="删除确认"
    width="420px"
    @ok="confirmDelete"
  >
    <div style="display: flex; align-items: center;">
      <exclamation-circle-outlined style="font-size: 22px; color: #faad14; margin-right: 12px;" />
      <span>确定要删除该记录吗？此操作不可撤销。</span>
    </div>
  </a-modal>
</template>
```

#### 分页 Pagination

```vue
<template>
  <a-pagination
    v-model:current="pagination.current"
    v-model:page-size="pagination.pageSize"
    :total="pagination.total"
    :page-size-options="['10', '20', '50']"
    show-size-changer
    show-quick-jumper
    show-total
    style="margin-top: 20px; text-align: right;"
  />
</template>
```

#### 表单 Form

```vue
<template>
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
</template>
```

#### 描述列表 Descriptions

```vue
<template>
  <a-descriptions :column="2" bordered>
    <a-descriptions-item label="用户名">admin</a-descriptions-item>
    <a-descriptions-item label="邮箱">admin@example.com</a-descriptions-item>
    <a-descriptions-item label="状态">
      <a-tag color="success">启用</a-tag>
    </a-descriptions-item>
  </a-descriptions>
</template>
```

## Hooks 使用规范

### useDrawer（简化版）

```typescript
import useDrawer from '@/hooks/useDrawer';

const { drawer, open, close } = useDrawer('PageName');

// 打开抽屉（新增模式）
open('add', '新增');

// 打开抽屉（编辑模式）
open('edit', '编辑', record);

// 打开抽屉（详情模式）
open('detail', '详情', record);

// 关闭抽屉
close();
```

### useForm（简化版）

```typescript
import { useForm } from '@/hooks/useForm';

const { VBind, resetFields, setFields } = useForm({
  schemas: searchSchema,
  modelRef: inParams,
  isForm: false,
  onEnter: () => search(),
});
```

## 页面开发规范

### 列表页标准结构

```vue
<script setup lang="ts">
import { columns, PAGE_NAME, searchSchema, statusOptions } from './data';
import EditForm from './components/EditForm.vue';
import { mockGetTableData, mockDelete } from '@/api/mock-api';
import { getLabelByValue } from '@/utils';
import useDrawer from '@/hooks/useDrawer';
import { useForm } from '@/hooks/useForm';

defineOptions({ name: PAGE_NAME });

// 搜索表单
const inParams = reactive({
  name: '',
  status: '',
});

const { VBind: searchVBind, resetFields: reset } = useForm({
  schemas: searchSchema,
  modelRef: inParams,
  isForm: false,
  onEnter: () => search(),
});

// 表格数据
const tableData = ref<any[]>([]);
const loading = ref(false);
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
});

const getTableData = async () => {
  loading.value = true;
  try {
    const res = await mockGetTableData({
      pageNo: pagination.current,
      pageSize: pagination.pageSize,
      ...inParams,
    });
    if (res.code === 200) {
      tableData.value = res.data.records;
      pagination.total = res.data.total;
    }
  } finally {
    loading.value = false;
  }
};

const search = () => {
  pagination.current = 1;
  getTableData();
};

// 删除操作
const handleDelete = (row: any) => {
  Modal.confirm({
    title: '确定删除？',
    onOk: async () => {
      const res = await mockDelete(row.id);
      if (res.code === 200) {
        message.success('删除成功');
        await getTableData();
      }
    },
    cancelText: '取消',
  });
};

// 抽屉
const { drawer } = useDrawer(PAGE_NAME);
const editForm = ref();
const handleSave = async () => {
  try {
    await editForm.value?.save();
    drawer.close();
    getTableData();
  } catch (e) {
    console.error(e);
  }
};

// 初始化
const init = async () => {
  await getTableData();
};
init();
</script>

<template>
  <div class="prototype-page">
    <a-card title="页面标题" :bordered="false">
      <!-- 搜索区域 -->
      <div class="search-area">
        <a-form layout="inline" :model="inParams">
          <!-- 搜索字段 -->
          <a-form-item>
            <a-button type="primary" @click="search">查询</a-button>
            <a-button style="margin-left: 8px" @click="reset">重置</a-button>
            <a-button type="primary" style="margin-left: 8px" @click="drawer.open('add', '新增')">
              新增
            </a-button>
          </a-form-item>
        </a-form>
      </div>

      <!-- 表格区域 -->
      <a-table
        :columns="columns"
        :data-source="tableData"
        :loading="loading"
        :pagination="false"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <!-- 自定义列 -->
        </template>
      </a-table>

      <!-- 分页 -->
      <a-pagination
        v-model:current="pagination.current"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        show-size-changer
        show-quick-jumper
        show-total
        style="margin-top: 20px; text-align: right"
      />
    </a-card>

    <!-- 抽屉 -->
    <a-drawer
      v-model:visible="drawer.visible"
      :title="drawer.title"
      width="600px"
      :destroy-on-close="true"
    >
      <edit-form v-if="['add', 'edit'].includes(drawer.mode)" ref="editForm" />
      <template #footer>
        <a-button @click="drawer.close">取消</a-button>
        <a-button type="primary" style="margin-left: 8px" @click="handleSave">保存</a-button>
      </template>
    </a-drawer>
  </div>
</template>

<style scoped lang="less">
.prototype-page {
  padding: 24px;
}

.search-area {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}
</style>
```

## 配色方案

使用 Ant Design Vue 3.x 的标准配色：

| 名称 | 色值 | 用途 |
|-----|------|-----|
| Primary | `#1890ff` | 主按钮、链接、选中态 |
| Success | `#52c41a` | 成功状态、启用标签 |
| Warning | `#faad14` | 警告状态 |
| Error | `#ff4d4f` | 错误状态、危险操作 |

## 消息提示

```typescript
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

```vue
<template>
  <home-outlined />
  <search-outlined />
  <plus-outlined />
  <edit-outlined />
  <delete-outlined />
</template>

<script setup lang="ts">
import {
  HomeOutlined,
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons-vue';
</script>
```

## Mock 数据规范

所有 API 调用都使用 mock 数据：

```typescript
// src/api/mock-api.ts
export async function mockGetTableData(params: any): Promise<MockResponse<any>> {
  const pageSize = params.pageSize || 10;
  const pageNo = params.pageNo || 1;

  const records = Array.from({ length: pageSize }, (_, i) => ({
    id: String((pageNo - 1) * pageSize + i + 1),
    name: `示例数据${(pageNo - 1) * pageSize + i + 1}`,
    status: Math.random() > 0.5 ? 1 : 0,
    createTime: '2024-01-01',
  }));

  return createMockResponse({
    records,
    total: 100,
  });
}
```

## 重要提醒

1. **必须使用 Ant Design Vue 3.x**：API 与 4.x 有差异，特别注意 `v-model:visible` vs `v-model:open`
2. **使用 pnpm**：项目使用 pnpm 作为包管理器
3. **3005端口**：原型服务默认在 3005 端口启动
4. **Mock数据**：所有 API 调用都使用 mock 数据，不依赖后端服务
5. **保持技术栈一致**：依赖版本必须与主项目完全一致
