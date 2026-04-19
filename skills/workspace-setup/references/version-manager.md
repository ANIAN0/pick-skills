# 版本管理

`version_manager.py` 脚本的详细使用说明。

## 功能

管理项目版本目录：
- `create` - 创建新版本目录（版本号自动递增）
- `archive` - 归档已完成版本到 archive 目录
- `status` - 查看当前版本状态

## 命令

### 创建新版本

```bash
# 自动递增版本号（如 1.0 -> 1.1）
python scripts/version_manager.py create --config skillconfig.json

# 创建指定版本
python scripts/version_manager.py create --config skillconfig.json --version 2.0
```

创建新版本目录并自动更新 skillconfig.json 中的 current_version。

### 归档版本

```bash
# 归档当前版本
python scripts/version_manager.py archive --config skillconfig.json

# 归档指定版本
python scripts/version_manager.py archive --config skillconfig.json --version 1.0
```

将版本目录移动到 workplace/archive/ 下。

### 查看状态

```bash
python scripts/version_manager.py status --config skillconfig.json
```

显示活跃版本和已归档版本的列表。

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--config` | skillconfig.json | 配置文件路径 |
| `--version` | 自动计算 | 指定版本号（可选） |

## 版本号格式

采用 `major.minor` 格式：
- `1.0`, `1.1`, `1.2` - 主版本 1 的迭代版本
- `2.0`, `2.1` - 主版本 2 的迭代版本

自动递增规则：`minor + 1`（如 1.0 → 1.1）

## 版本目录结构

每个版本目录包含以下子目录：

```
{version}/
├── requirements/   # 需求文档
├── references/     # 参考文档
├── prototypes/     # 原型设计
├── tech-design/    # 技术方案
├── plan/           # 实施计划
└── tests/          # 测试文件
```

## 输出示例

### 创建新版本

```
🆕 开始创建新版本...

✅ 创建版本目录: 1.1
  ├── requirements/
  ├── references/
  ├── prototypes/
  ├── tech-design/
  ├── plan/
  ├── tests/

📊 创建完成:
   新版本: 1.1
   目录数: 7
```

### 归档版本

```
📦 开始归档版本...

✅ 归档成功: 1.0 -> archive/1.0

📊 归档完成:
   归档版本: 1.0
```

### 查看状态

```
📋 版本状态:

当前版本: 1.1

活跃版本:
  1.1 *

已归档:
  1.0 (archived)

归档路径: workplace/archive
```

## 工作流程示例

### 日常迭代

```
# 1. 开始新迭代
python scripts/version_manager.py create
# 输出: 创建版本 1.1

# 2. 开发过程中查看状态
python scripts/version_manager.py status
# 输出: 当前版本 1.1

# 3. 完成迭代，归档旧版本
python scripts/version_manager.py archive --version 1.0
# 输出: 归档 1.0 -> archive/1.0
```

### 主版本升级

```
# 1. 创建新的主版本
python scripts/version_manager.py create --version 2.0

# 2. 归档所有 1.x 版本
python scripts/version_manager.py archive --version 1.5
```

## 配置更新

创建新版本时，自动更新 skillconfig.json：

```json
{
  "workspace": {
    "current_version": "1.1"  // 自动更新
  }
}
```

## 错误处理

| 错误 | 处理 |
|------|------|
| 版本号格式无效 | 抛出 ValueError |
| 版本目录已存在 | 返回错误，提示归档或使用其他版本号 |
| 归档目标已存在 | 返回错误 |
| 源版本目录不存在 | 返回错误 |

## 版本目录用途

| 目录 | 典型内容 |
|------|----------|
| requirements/ | 需求说明、用户故事、验收标准 |
| references/ | API文档、设计规范、参考资料 |
| prototypes/ | UI原型、流程图、架构图 |
| tech-design/ | 技术选型、架构设计、数据库设计 |
| plan/ | 任务分解、里程碑、进度跟踪 |
| tests/ | 测试计划、测试用例、测试报告 |