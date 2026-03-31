# Prototype Generator（原型生成器）

根据需求文档生成 Ant Design 风格的前端原型HTML页面。

## 功能

- 读取需求文档（REQ文档或产品说明）
- 评估页面清单并与用户确认
- 查看项目现有页面现状（判断新增/修改）
- 通过提问澄清需求细节（每轮≤3问）
- 使用Subagent并行生成原型（避免上下文爆炸）
- **使用真正的 Ant Design CSS（`antd.min.css`）生成高保真原型**
- 输出左侧原型（固定1200px）+ 右侧交互说明的双栏布局
- **支持旧原型改造**（生成新文件，保留旧文件）

## 触发方式

### 场景A：根据需求生成新原型
```
/prototype
/生成原型
根据需求生成原型页面
```

### 场景B：旧原型改造
```
/改造原型
/优化原型
旧原型需要修改
```

## 工作流程

### 场景A：新原型
```
1. 读取需求文档 → 2. 评估页面清单 → 3. 查看现有页面现状
  → 4. 需求澄清（每轮≤3问）→ 5. 使用Subagent生成原型 → 6. 输出到docs/prototype
```

### 场景B：旧原型改造
```
1. 读取旧原型HTML → 2. 理解旧页面逻辑 → 3. 确认改造需求（每轮≤3问）
  → 4. 使用Subagent生成新原型 → 5. 输出（新文件名，保留旧文件）
```

## 输出格式

### 场景A：新原型
```
docs/prototype/
├── prototype-20240325-user-list.html
├── prototype-20240325-user-detail.html
└── prototype-20240325-user-form.html
```

### 场景B：旧原型改造
```
docs/prototype/
├── prototype-20240320-user-list.html      # 旧文件（保留）
├── prototype-20240325-user-list-v2.html   # 新文件（改造后）
└── ...
```

## 页面结构

每个HTML原型文件包含：
- **左侧（固定1200px）**：Ant Design 风格的原型页面，使用 mock 数据
- **右侧（自适应）**：交互说明文档，详细描述每个操作点的行为

## 技能目录结构

```
prototype-generator/
├── SKILL.md                   # 主技能文档
├── README.md                  # 使用说明
├── docs/
│   ├── design-guide.md        # Ant Design设计规范（独立可获取）
│   └── output-format.md       # HTML输出格式规范
├── evals/
│   └── evals.json             # 测试用例
└── scripts/
    └── generator.py           # 辅助脚本

prototype-page-generator/      # Subagent技能
└── SKILL.md                   # 单页面生成器
```

## 参考资源

- `docs/design-guide.md` - Ant Design 4.x 设计规范（使用真正的 `antd.min.css`）
- `docs/output-format.md` - HTML输出格式详细规范
- `../prototype-page-generator/SKILL.md` - Subagent页面生成器
