# Vue Prototype Generator

Vue 原型生成器 - 基于项目前端技术栈的高保真原型生成工具。

## 功能特性

- **三种工作模式**：
  1. **复刻模式**：已有页面 1:1 复刻（数据使用 mock 数据）
  2. **需求模式**：根据需求文档生成全新原型页面
  3. **对话模式**：通过对话逐步调整原型细节

- **技术栈一致性**：
  - Vue 3.3.4 + TypeScript
  - Ant Design Vue 3.2.20
  - Rsbuild 构建工具
  - Mock 数据替代真实 API

- **独立项目结构**：每个原型都是完整的 Vue 项目，需要在指定目录下运行 `pnpm dev` 在 3005 端口启动服务后预览

## 目录结构

```
.claude/skills/vue-prototype-generator/
├── SKILL.md                    # 技能主文档（使用说明）
├── README.md                   # 本文件
├── docs/
│   └── design-guide.md         # 设计规范文档
└── scripts/
    ├── init_prototype.py       # 初始化原型项目
    ├── generate_page.py        # 生成单个页面
    ├── batch_generate.py       # 批量生成页面
    └── update_page.py          # 更新页面（对话模式）
```

## 使用方法

### 1. 初始化原型项目

```bash
python scripts/init_prototype.py --name my-prototype --output docs/prototype/
```

### 2. 生成页面

```bash
python scripts/generate_page.py \
  --input '{
    "page_name": "用户列表",
    "page_type": "list",
    "clarification": {...}
  }' \
  --prototype my-prototype
```

### 3. 批量生成

```bash
python scripts/batch_generate.py --config pages.json
```

配置示例 (pages.json)：

```json
{
  "prototype_name": "user-prototype",
  "output_path": "docs/prototype",
  "pages": [
    {
      "page_name": "用户列表",
      "page_type": "list",
      "clarification": {
        "data": {
          "columns": [...],
          "search_fields": [...]
        }
      }
    }
  ]
}
```

### 4. 启动服务预览

```bash
cd docs/prototype/my-prototype
pnpm install
pnpm dev
```

访问 http://localhost:3005 查看原型。

### 5. 更新页面（对话模式）

```bash
python scripts/update_page.py \
  --prototype my-prototype \
  --page user-list \
  --changes '{
    "type": "field",
    "updates": {
      "add_columns": [...]
    }
  }'
```

## 生成的原型项目结构

```
docs/prototype/{prototype-name}/
├── package.json              # 依赖配置
├── rsbuild.config.ts         # Rsbuild 配置
├── tsconfig.json             # TypeScript 配置
├── index.html                # 入口 HTML
├── src/
│   ├── main.ts               # 入口文件
│   ├── App.vue               # 根组件
│   ├── api/
│   │   └── mock-api.ts       # Mock API 层
│   ├── hooks/                # Hooks（简化版）
│   │   ├── useDrawer.ts
│   │   └── useForm.ts
│   ├── pages/                # 页面目录
│   │   └── {page-name}/
│   │       ├── index.vue
│   │       ├── data.ts
│   │       └── components/
│   │           └── EditForm.vue
│   ├── router/
│   ├── styles/
│   ├── utils/
│   └── types/
```

## 注意事项

1. **必须使用 pnpm**：项目使用 pnpm 作为包管理器
2. **3005 端口**：原型服务默认在 3005 端口启动
3. **Ant Design Vue 3.x**：注意 API 与 4.x 版本的差异（如 `v-model:visible` vs `v-model:open`）
4. **Mock 数据**：所有 API 调用都使用 mock 数据，不依赖后端服务

## 设计规范

详见 `docs/design-guide.md`，包含：

- 技术栈说明
- 组件使用规范
- Hooks 使用规范
- 页面开发规范
- 配色方案
- Mock 数据规范
