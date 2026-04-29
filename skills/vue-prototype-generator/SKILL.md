---
name: vue-prototype-generator
description: |
  **确保使用此技能** 当用户需要「生成Vue原型」「创建Vue原型页面」「Vue需求转原型」「/vue-prototype」「Vue原型」「根据需求生成前端原型」「复刻现有页面为原型」「更新原型页面」「修改原型细节」或任何涉及Vue前端页面原型生成的请求时。

  本技能支持3种工作模式：
  1. **复刻模式**：已有页面1:1复刻，生成与现有页面**完全一致的原型**（包括布局、样式、交互，数据使用mock数据）
  2. **需求模式**：根据需求文档生成全新的原型页面
  3. **对话模式**：通过对话逐步调整原型细节，用于迭代优化

  **核心特点**：
  - 输出使用与项目前端完全一致的技术栈（Vue 3.3.4 + Ant Design Vue 3.2.20 + Rsbuild + TypeScript + @kt/unity组件库）
  - **复刻模式必须保持与原页面 1:1 风格一致**（配色、间距、字体、组件样式）
  - **复用现有项目时新页面必须与现有项目风格一致**
  - 需要在原型目录下运行 `pnpm dev` 在3005端口启动服务后预览

  **触发关键词**: Vue原型、生成原型、复刻页面、原型页面、Ant Design Vue原型、需求转原型、更新原型、调整原型
---

# Vue Prototype Generator（Vue原型生成器）

## 目标

将需求文档或现有页面转换为**高保真 Vue 原型页面**，输出使用与项目前端**完全一致的技术栈**：

- **Vue 3.3.4** + TypeScript
- **Ant Design Vue 3.2.20**
- **Rsbuild** 构建工具
- **@kt/unity-*** 组件库（公司内部组件）
- **tl-*** 布局组件系统
- **Mock 数据** 替代真实API调用

原型需要在指定目录下运行 `pnpm dev` 启动开发服务器（默认3005端口）后才能预览，确保原型与实际页面的一致性。

## 三种工作模式

## 三种工作模式

### 模式1：复刻模式（已有页面1:1复刻）

当用户需要「复刻现有页面」「复制现有页面为原型」「将页面转为原型」时触发。

**⚠️ 关键决策：复用 or 新建？**

在复刻页面之前，**必须先判断**是复用现有原型项目，还是创建新项目：

```
检查 .dev/prototype/ 目录
├── 已有相同业务领域的原型？→ 【复用现有项目】只需添加新页面
└── 没有相关原型？→ 【创建新项目】初始化完整项目结构
```

**【复用现有项目】（推荐）**
- 同一业务领域的页面应放入**同一个原型项目**
- 只需将新页面文件放入 `src/pages/{page-name}/`，更新路由即可
- **无需重新安装依赖**，直接运行 `pnpm dev` 启动
- **⚠️ 风格一致性要求**：新页面必须参考现有项目的风格（样式、布局、组件使用方式），确保视觉上与现有页面保持一致

**【创建新项目】**
- 仅用于全新业务领域，与现有原型无关
- 需要完整初始化项目结构并安装依赖

**工作流程**：
```
检查现有原型项目 → 决策（复用/新建）→ 读取现有页面代码 → 分析页面结构
→ 提取组件和交互 → 生成原型文件（添加到现有项目或新建）→ 替换API为mock数据
```

**关键步骤**：
1. **检查现有原型项目**：先查看 `.dev/prototype/` 下是否已有可复用的原型项目
   - 如有：将新页面添加到现有项目 `src/pages/{page-name}/`
   - 如无：创建新的原型项目
2. 读取现有页面的 `.vue` 文件、`data.ts` 文件、`components/` 下的组件
3. 分析页面使用的组件、hooks、布局结构
4. 生成原型文件，保留原有结构和样式
5. 将真实API调用替换为mock数据
6. 保持与原始页面1:1的视觉效果和交互体验

### 模式2：需求模式（根据需求文档生成）

当用户需要「根据需求生成原型」「从需求文档创建页面」时触发。

**工作流程**：
```
读取需求文档 → 评估页面清单 → 需求澄清 → 生成原型 → 启动服务验证
```

**关键步骤**：
1. 读取需求文档，提取用户故事、功能列表、业务流程
2. 评估需要的前端页面清单
3. 针对每个页面澄清布局、数据、交互、边界场景
4. 生成完整的Vue原型文件
5. 初始化原型项目并启动服务

### 模式3：对话模式（通过对话调整细节）

当用户需要「调整原型」「修改原型细节」「优化原型」时触发。

**工作流程**：
```
读取现有原型 → 理解调整需求 → 修改对应文件 → 验证更新效果
```

**关键步骤**：
1. 读取现有原型文件
2. 与用户对话明确调整范围（样式、布局、交互、字段等）
3. 修改对应的 `.vue` 或 `data.ts` 文件
4. 保持其他部分不变

## 原型项目结构

生成的原型项目位于 `.dev/prototype/{原型名称}/` 目录下，结构如下：

```
.dev/prototype/{prototype-name}/
├── package.json              # 依赖配置（与项目前端一致）
├── rsbuild.config.ts         # Rsbuild配置
├── tsconfig.json             # TypeScript配置
├── index.html                # 入口HTML
├── src/
│   ├── main.ts               # 入口文件
│   ├── App.vue               # 根组件
│   ├── env.d.ts              # 类型声明
│   ├── api/                  # Mock API层
│   │   └── mock-api.ts
│   ├── hooks/                # Hooks（简化版）
│   │   ├── useDrawer.ts
│   │   └── useForm.ts
│   ├── pages/                # 页面目录
│   │   └── {page-name}/
│   │       ├── index.vue     # 页面主组件
│   │       ├── data.ts       # 列配置、搜索配置
│   │       └── components/   # 页面组件
│   │           ├── EditForm.vue
│   │           └── DetailForm.vue
│   ├── styles/               # 全局样式
│   │   └── index.less
│   └── utils/                # 工具函数
│       └── index.ts
└── pnpm-lock.yaml
```

## 技术栈一致性要求

### Rsbuild 配置规范

**rsbuild.config.ts 模板**（必须与项目前端一致）：

```typescript
import { defineConfig } from '@rsbuild/core';
import { pluginVue } from '@rsbuild/plugin-vue';
import { pluginLess } from '@rsbuild/plugin-less';

export default defineConfig({
  plugins: [pluginVue(), pluginLess()],  // 必须包含 Less 插件
  resolve: {
    alias: {
      '@': './src',  // 使用 resolve.alias（source.alias 已弃用）
    },
  },
  source: {
    entry: {
      index: './src/main.ts',  // 显式配置入口文件
    },
  },
  server: {
    port: 3005,
  },
  html: {
    template: './index.html',
  },
});
```

**重要注意事项**：
1. 使用 `resolve.alias` 代替已弃用的 `source.alias`
2. 必须显式配置 `source.entry`，否则 Rsbuild 找不到入口文件
3. 必须安装并使用 `@rsbuild/plugin-less` 插件，因为项目使用 Less 样式
4. 样式文件使用 `.less` 后缀

### package.json 依赖规范

**package.json 模板**（必须与项目前端一致）：

```json
{
  "name": "prototype-{name}",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "rsbuild dev",
    "build": "rsbuild build"
  },
  "dependencies": {
    "vue": "3.3.4",
    "ant-design-vue": "3.2.20",
    "pinia": "3.0.4",
    "vue-router": "5.0.1",
    "@vueuse/core": "14.2.0",
    "dayjs": "^1.11.19",
    "lodash-es": "^4.17.23"
  },
  "devDependencies": {
    "@rsbuild/core": "^1.6.15",
    "@rsbuild/plugin-vue": "^1.2.2",
    "@rsbuild/plugin-less": "^1.5.0",
    "typescript": "~5.9.3"
  }
}
```

**关键依赖说明**：
- 必须包含 `@rsbuild/plugin-less`，因为项目使用 Less 样式
- 版本号必须与项目前端保持一致

### main.ts 入口文件规范

**src/main.ts 模板**：

```typescript
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';

const app = createApp(App);
app.use(router);
app.use(Antd);
app.mount('#app');
```

**重要**：必须导入 `ant-design-vue/dist/antd.css`，否则组件样式无法加载

**使用 @kt/unity-* 组件库**：

```vue
<template>
  <tl v-model:drawer="drawer.visible">
    <tl-main>
      <tl-filter>
        <yc-form v-bind="searchVBind" />
        <a-button type="primary" @click="search">查询</a-button>
      </tl-filter>
      <tl-table>
        <a-table v-on="VOn" v-bind="VBind" />
      </tl-table>
    </tl-main>
    <tl-drawer :title="drawer.title">
      <!-- 抽屉内容 -->
    </tl-drawer>
  </tl>
</template>
```

**常用组件**：
- `<tl>` - 布局根组件
- `<tl-main>` - 主内容区
- `<tl-filter>` - 搜索筛选区
- `<tl-table>` - 表格区
- `<tl-drawer>` - 抽屉组件
- `<yc-form>` - 表单组件
- `<yc-status>` - 状态标签
- `<action-group>` - 操作按钮组

### Hooks 使用规范

**useDrawer**（简化版）：

```typescript
import useDrawer from '@/hooks/useDrawer';

const { drawer, spinning } = useDrawer(PAGE_NAME);

// 打开抽屉
drawer.open('add', '新增');
drawer.open('edit', '编辑', record);
drawer.open('detail', '详情', record);

// 关闭抽屉
drawer.close();

// 加载状态
drawer.showSpinning();
drawer.hideSpinning();
// 或使用 spinning 对象
spinning.show();
spinning.hide();
```

**注意**：Hook 返回两个对象 `drawer` 和 `spinning`。`drawer` 对象已绑定 `open`、`close`、`showSpinning`、`hideSpinning` 方法，可直接调用。

**useForm**（简化版）：

```typescript
import { ref, reactive } from 'vue';  // 原型项目需要显式导入
import { useForm } from '@/hooks/useForm';

const { VBind, resetFields } = useForm({
  schemas: searchSchema,
  modelRef: inParams,
  isForm: false,
  onEnter: () => search(),
});
```

**重要**：原型项目没有 `unplugin-auto-import` 自动导入，**必须在每个组件顶部显式导入 Vue API**：

```typescript
import { ref, reactive, computed, watch, nextTick } from 'vue';
```

**useTable**（使用 @kt/unity-hooks）：

```typescript
import { useTable } from '@kt/unity-hooks';

const tableOptions = reactive<UseTableOptions>({
  currentKey: 'pageNo',
  pageSizeKey: 'pageSize',
  dataSourceKey: 'records',
  totalKey: 'total',
  immediate: false,
  columns,
  inParams,
});

const { VBind, VOn, search, loading, dataSource } = useTable(
  getTableData,
  tableOptions,
);
```

## 复刻模式技术细节检查清单

在复刻现有页面时，必须检查以下技术细节，确保生成的原型能够正常运行：

### 0. 原型复用决策检查（⚠️ 最重要）

- [ ] **已检查 `.dev/prototype/` 下是否已有可复用的原型项目**
- [ ] **已做出明确决策**：复用现有项目（推荐）或创建新项目
- [ ] **如复用现有项目**：
  - [ ] 目标 hooks 已存在于 `src/hooks/`（useDrawer.ts、useForm.ts、useTable.ts）
  - [ ] 新页面将添加到 `src/pages/{page-name}/`
  - [ ] 无需重新安装依赖，直接 `pnpm dev` 启动
  - [ ] **⚠️ 已读取 `src/styles/index.less` 了解现有项目风格**
  - [ ] **⚠️ 新页面风格与现有项目一致**（配色、间距、组件样式）
- [ ] **如创建新项目**：
  - [ ] 需要从原项目复制所有必要的 hooks 文件
  - [ ] 需要运行 `pnpm install` 安装依赖

### 1. Rsbuild 配置检查

- [ ] 使用 `resolve.alias` 而非 `source.alias`
- [ ] 显式配置 `source.entry: { index: './src/main.ts' }`
- [ ] 安装并配置 `@rsbuild/plugin-less` 插件
- [ ] 配置端口为 3005

### 2. 依赖检查

- [ ] `package.json` 包含 `@rsbuild/plugin-less` 依赖
- [ ] 版本号与项目前端一致

### 3. 入口文件检查

- [ ] `main.ts` 导入 `ant-design-vue/dist/antd.css`
- [ ] 正确注册 Vue Router 和 Ant Design Vue

### 4. Vue API 导入检查

- [ ] 每个组件顶部显式导入 Vue API：`import { ref, reactive, computed, watch } from 'vue'`
- [ ] 从原项目复制的代码需要补充缺失的导入语句

### 5. useDrawer Hook 检查

- [ ] 使用 `const { drawer, spinning } = useDrawer(PAGE_NAME)` 解构
- [ ] 不要假设只返回 `{ drawer }`
- [ ] `drawer.open()`、`drawer.close()`、`drawer.showSpinning()`、`drawer.hideSpinning()` 方法已绑定到 drawer 对象
- [ ] **检查原型项目的 `src/hooks/useDrawer.ts` 是否存在**，如不存在需复制

### 6. useForm / useTable 检查（⚠️ 新增）

- [ ] **检查原型项目的 `src/hooks/useForm.ts` 是否存在**
- [ ] **检查原型项目的 `src/hooks/useTable.ts` 是否存在**（或使用 `@kt/unity-hooks`）
- [ ] 确认 useForm 返回 `VBind` 对象（不是 ref）
- [ ] 确认使用方式：`const { VBind, resetFields } = useForm({...})`

### 7. 样式文件检查

- [ ] 样式文件使用 `.less` 后缀
- [ ] 全局样式在 `main.ts` 中导入
- [ ] **复刻模式**：样式与原页面 1:1 一致
- [ ] **复用现有项目**：已读取 `src/styles/index.less` 了解现有项目风格

### 8. Mock 数据检查（⚠️ 新增）

- [ ] Mock 数据返回格式正确：`{ records: [...], total: number }`
- [ ] useTable 配置与实际数据结构匹配
- [ ] 搜索筛选功能正常

### 9. 文件路径检查（⚠️ 新增，Windows 环境特别注意）

- [ ] 复制文件后验证目录结构正确
- [ ] `index.vue` 位于 `src/pages/{page-name}/` 目录下
- [ ] router 中的 import 路径正确
- [ ] **Windows 环境**：使用正斜杠 `/` 或双反斜杠 `\\` 处理路径

### 7. 常见错误修复

如果在启动原型时遇到以下错误，按以下方式修复：

**错误：`source.alias` is deprecated**
```typescript
// 错误
source: {
  alias: { '@': './src' }
}

// 正确
resolve: {
  alias: { '@': './src' }
}
```

**错误：Could not find any entry module**
```typescript
// 添加 source.entry 配置
source: {
  entry: {
    index: './src/main.ts',
  },
}
```

**错误：Less 样式编译失败**
```bash
# 安装 Less 插件
pnpm add -D @rsbuild/plugin-less
```

**错误：`drawer.open is not a function`**
```typescript
// 确保使用正确的解构方式
const { drawer, spinning } = useDrawer(PAGE_NAME);
// drawer 对象已绑定 open/close 方法
```

**错误：`reactive is not defined`**
```typescript
// 在组件顶部添加导入
import { ref, reactive, computed, watch } from 'vue';
```

**错误：Ant Design Vue 组件无样式**
```typescript
// 在 main.ts 中添加
import 'ant-design-vue/dist/antd.css';
```

**错误：`Cannot find module '@/hooks/useDrawer'`（⚠️ 新增）**
```bash
# 从原项目或其他原型项目复制 hooks
cp admin_frontend/src/hooks/useDrawer.ts .dev/prototype/{prototype-name}/src/hooks/
cp admin_frontend/src/hooks/useForm.ts .dev/prototype/{prototype-name}/src/hooks/
cp admin_frontend/src/hooks/useTable.ts .dev/prototype/{prototype-name}/src/hooks/
```

**错误：`Property 'VBind' was accessed on 'ref'`（⚠️ 新增）**
```typescript
// 错误：useForm 返回 ref
const VBind = useForm({...});  // VBind 是 ref

// 正确：解构获取 VBind
const { VBind, resetFields } = useForm({...});  // VBind 是 computed 对象
```

**错误：Mock 数据不显示（⚠️ 新增）**
```typescript
// 确保返回格式正确
const getTableData = async (params: any) => {
  return {
    records: [...],  // 必须包含 records
    total: number,   // 必须包含 total
    pageNum: number,
    pageSize: number,
  };
};
```

**错误：页面风格不一致（⚠️ 新增）**
```bash
# 问题1：复用现有项目时，新页面风格与现有页面不一致
# 原因：没有读取并参考现有项目的 src/styles/index.less 样式文件

# 解决方案：
# 1. 复用现有项目前，先读取 src/styles/index.less 了解现有项目风格
# 2. 新页面使用与现有页面相同的配色、间距、组件样式
# 3. 参考现有页面的写法（如 tl-* 组件使用方式）

# 问题2：复刻模式时，生成页面与原页面风格不一致
# 原因：没有 1:1 复刻原页面的样式（颜色、间距、字体等）

# 解决方案：
# 1. 复刻时必须保持与原页面完全一致的风格
# 2. 检查配色方案（主色调、按钮颜色、标签颜色）
# 3. 检查字体样式（大小、字重）
# 4. 检查间距规范（padding、margin）
# 5. 检查组件样式（表格、表单、按钮）
```

**问题：创建了重复的原型项目（⚠️ 新增）**
```bash
# 问题：每次复刻页面都创建新文件夹，导致依赖重复安装
# 原因：没有检查现有原型项目

# 正确做法：
# 1. 先检查 .dev/prototype/ 下是否有可复用的原型项目
# 2. 如有：将新页面放入现有项目的 src/pages/ 目录
# 3. 更新 router 后直接运行 pnpm dev（无需重新安装依赖）
# 4. 只有全新业务领域才创建新项目
```

**问题：Windows 路径错误（⚠️ 新增）**
```bash
# 复制后验证文件位置
dir .dev\prototype\{prototype-name}\src\pages\{page-name}\

# 确保 index.vue 在正确的位置
# 正确：src/pages/user-list/index.vue
# 错误：src/pages/user-list.vue（目录结构错误）
```

## 详细工作流程

### Phase 1: 确定工作模式

根据用户输入判断工作模式：

| 用户意图 | 关键词 | 工作模式 |
|---------|-------|---------|
| 复刻现有页面 | "复刻"、"复制"、"参考现有页面"、"仿照" | 模式1：复刻模式 |
| 根据需求生成 | "根据需求"、"从PRD"、"新建原型" | 模式2：需求模式 |
| 调整原型 | "调整"、"修改"、"优化"、"更新细节" | 模式3：对话模式 |

### Phase 2: 模式1 - 复刻模式详细步骤

**Step 2.0: 检查现有原型项目并决策（⚠️ 关键步骤）**

在创建任何文件之前，**必须先检查** `.dev/prototype/` 目录下是否已有可复用的原型项目：

```bash
# 查看现有原型项目
ls .dev/prototype/
```

**决策标准**：

| 场景 | 操作 | 说明 |
|-----|------|-----|
| 已有相同业务领域的原型项目 | **复用现有项目** | 将新页面添加到 `src/pages/`，无需重新安装依赖 |
| 全新业务领域，无相关原型 | **创建新项目** | 初始化完整项目结构并安装依赖 |

**复用现有项目的操作步骤**：
1. 将新页面代码放入现有项目的 `src/pages/{page-name}/` 目录：
   - `src/pages/{page-name}/index.vue`
   - `src/pages/{page-name}/data.ts`
   - `src/pages/{page-name}/components/*.vue`（如有）
2. 确认必要的 hooks 已存在于 `src/hooks/`（useDrawer.ts、useForm.ts 等）
3. 更新 `src/router/index.ts` 添加新路由
4. **直接运行 `pnpm dev` 启动**（无需 `pnpm install`，依赖已存在）

**创建新项目的操作步骤**：
1. 创建原型项目目录 `.dev/prototype/{prototype-name}/`
2. 初始化完整的项目结构（package.json、rsbuild.config.ts 等）
3. 安装依赖：`pnpm install`
4. 生成页面文件并启动服务

**Step 2.1: 读取现有页面**

读取目标页面的所有相关文件：
- `src/pages/{page-name}/index.vue` - 页面主组件
- `src/pages/{page-name}/data.ts` - 配置数据
- `src/pages/{page-name}/components/*.vue` - 子组件
- `src/api/{module}/` - API接口（用于了解数据结构）

**Step 2.2: 分析页面结构和风格（⚠️ 新增风格分析）**

提取以下信息：
- 页面布局结构（tl-* 组件使用方式）
- 表格列配置（columns）
- 搜索表单配置（searchSchema）
- 使用的hooks及其调用方式
- 抽屉/弹窗的使用方式
- 状态枚举和选项

**⚠️ 风格一致性分析（复刻模式关键）**：
- **配色方案**：主色调、按钮颜色、标签颜色
- **字体样式**：字体大小、字重、行高
- **间距规范**：padding、margin、间距大小
- **组件样式**：表格样式、表单样式、按钮样式
- **布局模式**：页面整体布局结构
- **交互细节**：hover效果、过渡动画

**如复用现有项目**：同时读取现有项目的 `src/styles/index.less` 或其他样式文件，确保新页面与现有页面风格一致。

**Step 2.3: Hooks 依赖检查（⚠️ 关键步骤）**

复刻页面时，**必须检查**以下 hooks 是否存在于目标原型项目中：

**必需 Hooks 清单**：
| Hook | 路径 | 用途 |
|-----|------|------|
| useDrawer | `src/hooks/useDrawer.ts` | 抽屉状态管理 |
| useForm | `src/hooks/useForm.ts` | 表单处理 |
| useTable | `src/hooks/useTable.ts` 或使用 `@kt/unity-hooks` | 表格数据管理 |

**检查步骤**：
1. 读取原页面的 hooks 导入语句，确认使用了哪些 hooks
2. 检查目标原型项目的 `src/hooks/` 目录是否已存在这些 hooks
3. 如不存在，从原项目或其他原型项目复制对应的 hook 文件

**useDrawer.ts 简化版要求**：
```typescript
// 必须将方法绑定到 drawer 对象返回
const drawer = reactive<DrawerState>({
  visible: false,
  title: '',
  mode: '',
  record: null,
  spinning: false,
  open: () => {},
  close: () => {},
  showSpinning: () => {},
  hideSpinning: () => {},
});

// 方法绑定
drawer.open = (mode, title, record) => { /* ... */ };
drawer.close = () => { /* ... */ };
drawer.showSpinning = () => { /* ... */ };
drawer.hideSpinning = () => { /* ... */ };

return { drawer };  // 只返回 drawer，方法已绑定
```

**useForm.ts 返回值要求**：
```typescript
return {
  VBind,           // 必须返回 VBind
  resetFields,
  setFields,
  validate,
};
```

**Step 2.4: 生成原型项目（⚠️ 强调风格复刻）**

1. 创建原型项目目录结构（如新建项目）
2. 复制基础配置文件（package.json、rsbuild.config.ts等）
3. **生成页面文件，保持原有代码结构和样式（复刻模式必须 1:1 复刻原页面风格）**
4. **如复用现有项目**：确保新页面风格与现有项目保持一致（读取并参考 `src/styles/index.less`）
5. 替换真实API为mock数据

**⚠️ 风格复刻检查清单**：
- [ ] 使用了与原页面相同的 tl-* 布局组件
- [ ] 表格/表单的样式与原页面一致
- [ ] 按钮、标签的颜色和大小与原页面一致
- [ ] 间距、padding、margin 与原页面一致
- [ ] 字体大小、字重与原页面一致

**Step 2.5: Mock数据替换**

将真实API调用替换为mock：

```typescript
// 原始代码
const getTableData = async (params: DemoGetTableType.Req) => {
  const { data } = await DemoApi.demoGetTable(params);
  return data;
};

// 原型代码 - 使用mock数据
const getTableData = async (params: any) => {
  // Mock数据
  return {
    records: [
      { id: '1', userName: '示例用户1', status: 0, createTime: '2024-01-01' },
      { id: '2', userName: '示例用户2', status: 1, createTime: '2024-01-02' },
    ],
    total: 2,
  };
};
```

### Phase 3: 模式2 - 需求模式详细步骤

**Step 3.1: 读取需求文档**

读取用户指定的需求文档，提取：
- 功能模块划分
- 页面清单
- 用户故事和业务流程
- 数据结构定义

**Step 3.2: 评估页面清单**

基于需求分析需要的前端页面，输出表格：

| 序号 | 页面名称 | 页面类型 | 功能描述 | 优先级 |
|-----|---------|---------|---------|-------|
| 1 | xxx列表 | list | 展示xxx数据 | P0 |
| 2 | xxx详情 | detail | 展示详细信息 | P0 |
| 3 | 新建xxx | form | 表单填写 | P0 |

**等待用户确认页面清单后再继续**

**Step 3.3: 需求澄清**

针对每个页面分轮次澄清（每轮最多3问）：

1. **布局与结构**：整体布局、模块划分、面包屑
2. **数据与展示**：表格列/表单字段/详情分组
3. **交互逻辑**：操作按钮、编辑方式（抽屉/弹窗/页面）、状态流转
4. **边界场景**：空数据、加载中、错误、权限控制

**停止条件**：用户确认达到90%理解度或明确表示「可以开始生成」

**Step 3.4: 生成原型项目**

**⚠️ 关键决策：复用 or 新建？**

在生成原型之前，**必须先检查** `.dev/prototype/` 下是否已有可复用的原型项目：

```bash
# 查看现有原型项目
ls .dev/prototype/
```

**决策标准**：
- 如已有相同业务领域的原型 → **复用现有项目**，只需添加新页面
- 如全新业务领域 → **创建新项目**

**【复用现有项目】操作步骤**：
1. 将新页面文件直接放入现有项目 `src/pages/{page-name}/`
2. 更新 `src/router/index.ts` 添加新路由
3. **直接运行 `pnpm dev` 启动**（无需重新安装依赖）

**【创建新项目】操作步骤**：

调用 `scripts/init_prototype.py` 初始化项目：

```bash
python scripts/init_prototype.py --name {prototype-name} --output .dev/prototype/
```

然后调用 `scripts/generate_page.py` 生成每个页面：

```bash
python scripts/generate_page.py --input '{
  "page_name": "用户列表",
  "page_type": "list",
  "prototype_name": "user-prototype",
  "clarification": {...}
}'
```

**Step 3.5: 安装依赖并启动服务**

**如复用现有项目**（推荐）：
```bash
cd .dev/prototype/{existing-prototype}
# 无需安装依赖，直接启动
pnpm dev
```

**如创建新项目**：
```bash
cd .dev/prototype/{prototype-name}
pnpm install
pnpm dev
```

服务启动后，原型可在 http://localhost:3005 访问

### Phase 4: 模式3 - 对话模式详细步骤

**Step 4.1: 读取现有原型**

确定用户要调整的原型项目和具体页面，读取相关文件。

**Step 4.2: 理解调整需求**

与用户对话明确：
- 调整范围（样式、布局、交互、字段等）
- 调整的具体内容
- 是否影响其他页面

**Step 4.3: 执行修改**

根据需求修改对应文件，保持其他部分不变：

```bash
python scripts/update_page.py --prototype {prototype-name} --page {page-name} --changes '{...}'
```

**Step 4.4: 验证更新**

如果服务未运行，启动服务；如果已运行，热更新会自动生效。

## 文件输出规范

### 输出目录

原型项目输出到 `.dev/prototype/{原型名称}/` 目录下。

### 命名规范

- **原型目录**：kebab-case，如 `user-management-prototype`
- **页面目录**：kebab-case，如 `user-list`
- **页面组件**：PascalCase，如 `UserListPage`
- **子组件**：PascalCase，如 `EditForm.vue`

### 页面类型

| 类型 | 说明 | 典型组件 |
|-----|------|---------|
| list | 列表页 | 搜索表单、表格、分页、操作按钮 |
| form | 表单页 | 表单字段、验证、提交/取消按钮 |
| detail | 详情页 | 描述列表、卡片、操作栏 |

## 脚本工具

### init_prototype.py - 初始化原型项目

```bash
python scripts/init_prototype.py \
  --name {原型名称} \
  --output {输出目录} \
  [--template {模板类型}]
```

### generate_page.py - 生成页面

```bash
python scripts/generate_page.py \
  --input '{JSON配置}' \
  [--prototype {原型名称}]
```

### update_page.py - 更新页面

```bash
python scripts/update_page.py \
  --prototype {原型名称} \
  --page {页面名称} \
  --changes '{变更配置}'
```

### batch_generate.py - 批量生成

```bash
python scripts/batch_generate.py \
  --config {配置文件路径}
```

## 自检清单

### 原型复用决策检查（⚠️ 最重要）
- [ ] **已检查 `.dev/prototype/` 下是否有可复用的原型项目**
- [ ] **已做出明确决策**：复用现有项目 OR 创建新项目
- [ ] **如复用现有项目**：
  - [ ] 新页面已添加到 `src/pages/{page-name}/` 目录
  - [ ] 确认 hooks 文件已存在（`src/hooks/useDrawer.ts`、`src/hooks/useForm.ts` 等）
  - [ ] 路由已更新
  - [ ] **跳过了 `pnpm install`**，直接运行 `pnpm dev`
  - [ ] **⚠️ 新页面风格与现有项目一致**（读取并参考 `src/styles/index.less`）
- [ ] **如创建新项目**：
  - [ ] 已完成 `pnpm install` 安装依赖
  - [ ] 所有 hooks 文件已复制到 `src/hooks/`
  - [ ] 项目能正常启动

### 基础配置检查
- [ ] `package.json` 包含 `@rsbuild/plugin-less` 依赖
- [ ] `rsbuild.config.ts` 使用 `resolve.alias`（非 `source.alias`）
- [ ] `rsbuild.config.ts` 显式配置 `source.entry: { index: './src/main.ts' }`
- [ ] `rsbuild.config.ts` 包含 `@rsbuild/plugin-less` 插件
- [ ] `main.ts` 导入 `ant-design-vue/dist/antd.css`

### 代码规范检查
- [ ] 所有组件顶部显式导入 Vue API：`import { ref, reactive, computed, watch } from 'vue'`
- [ ] useDrawer 使用正确解构：`const { drawer, spinning } = useDrawer(PAGE_NAME)`
- [ ] drawer 方法通过 drawer 对象调用：`drawer.open()`, `drawer.close()`
- [ ] useForm 正确使用：`const { VBind, resetFields } = useForm({...})`
- [ ] 样式文件使用 `.less` 后缀

### Hooks 完整性检查（⚠️ 新增）
- [ ] `src/hooks/useDrawer.ts` 存在且方法已绑定到 drawer 对象
- [ ] `src/hooks/useForm.ts` 存在且返回 `VBind`、`resetFields` 等
- [ ] `src/hooks/useTable.ts` 存在（或使用 `@kt/unity-hooks`）

### Mock 数据检查（⚠️ 新增）
- [ ] Mock 数据返回格式包含 `records` 和 `total`
- [ ] useTable 配置与实际数据结构匹配
- [ ] 搜索筛选功能正常

### 文件路径检查（⚠️ 新增，Windows 环境）
- [ ] 页面文件位于 `src/pages/{page-name}/index.vue`
- [ ] router 中的 import 路径正确
- [ ] 复制后验证目录结构

### 功能检查
- [ ] 原型项目使用与项目前端完全一致的技术栈版本
- [ ] 使用 @kt/unity-* 组件库和 tl-* 布局组件
- [ ] Mock数据正确显示，API调用已被替换
- [ ] 页面布局与目标一致
- [ ] 抽屉、弹窗等交互组件正常工作
- [ ] `pnpm dev` 能在3005端口正常启动，无编译错误
- [ ] 原型页面可在浏览器正常访问，样式正确加载
- [ ] **复刻模式：与原页面1:1对比一致（包括布局、样式、交互）**

### 风格一致性检查（⚠️ 新增）
- [ ] **复刻模式**：生成页面与原页面 1:1 风格一致
  - [ ] 配色方案一致（主色调、按钮颜色、标签颜色）
  - [ ] 字体样式一致（大小、字重）
  - [ ] 间距规范一致（padding、margin）
  - [ ] 组件样式一致（表格、表单、按钮）
- [ ] **复用现有项目**：新页面与现有项目风格一致
  - [ ] 已读取并参考 `src/styles/index.less`
  - [ ] 使用了与现有页面相同的布局模式
  - [ ] 按钮、表格、表单的样式与现有页面一致

## 参考资源

- **项目前端CLAUDE.md**: `admin_frontend/CLAUDE.md` — 项目前端详细规范
- **设计规范**: `docs/design-guide.md` — Ant Design Vue 设计规范
- **示例页面**: `admin_frontend/src/pages/table-demo/` — 参考实现
- **常见问题**: `.dev/testdoc/docs/报错信息/Vue原型常见问题.md` — 原型常见问题及解决方案
