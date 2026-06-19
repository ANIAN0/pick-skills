---
name: project-development-v3-common
description: 提供项目研发 v3 Skill 套件共享的节点 Schema、关系、生命周期、确认哈希、证据、局部影响和派生索引协议，以及确定性校验脚本。维护或消费 v3 项目图谱、校验节点、计算影响、构建索引或统一各阶段契约时使用。
---

# 项目研发 v3 公共协议

本 Skill 是 v3 套件的共享契约层，不承担需求、设计、计划或实施阶段的业务决策。

## 按需读取

- 创建或解析节点：读取 [节点 Schema](references/node-schema.md)。
- 创建关系：读取 [关系注册表](references/relation-registry.md)。
- 修改状态：读取 [生命周期](references/lifecycle.md)。
- 复用确认：读取 [确认协议](references/confirmation.md)。
- 写入或消费证据：读取 [证据策略](references/evidence-policy.md)。

## 确定性工具

- `scripts/validate_graph.py`：校验节点、关系、状态和证据完整性。
- `scripts/compute_impact.py`：从变更节点计算局部影响及原因路径。
- `scripts/build_graph_index.py`：从 Markdown 事实源构建可删除重建的派生索引。
- `scripts/build_graph_view.py`：把派生索引构建为无服务、无外部依赖的只读页面。

首次运行脚本前安装其唯一第三方依赖：`python -m pip install -r skills/project-development-v3-common/scripts/requirements.txt`。`requirements.txt` 必须保留，因为 `graph_core.py` 直接使用 `PyYAML` 解析 Frontmatter；Python 标准库不提供 YAML 解析器。

## 硬规则

- Markdown 节点是事实源；索引和视图都是可删除重建的派生产物。
- 只使用关系注册表中的方向和语义，不维护手工反向链接。
- 节点内容变化后重新计算确认哈希，并仅传播到实际受影响子图。
- 未通过真实验证及证据门禁时，不得将任务、验收或工作流标记 done。
- 保留未知字段和用户已有内容；确定性脚本不得擅自改写业务结论。

## 输出

返回校验问题、影响节点及路径、派生索引位置或协议判断；不要生成阶段级长文档。
