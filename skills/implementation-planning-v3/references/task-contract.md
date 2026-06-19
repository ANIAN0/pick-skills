# 任务契约

## 必要上下文

任务记录：所属变更契约 ID 和确认哈希；验证 ID；精确目标文件和符号；相邻接口和依赖；局部实施步骤；正向及必要负向场景；must disappear/appear/propagate/persist 执行断言；预期证据路径和命令；完成边界。只引用上游 ID，不复制完整正文。

## 必填字段

每个任务必须包含：

- `criticality`: `core` 或 `supporting`；
- `infrastructure`: boolean；
- `risk`: `high`、`medium` 或 `low`；
- `executor_requirement`: `senior` 或 `standard`；
- `executor_profile`: 已分配执行者级别或 null；
- `approval`: 明确审批映射或 null；
- `target_files`、`target_symbols`、`verification_ids`、`execution_assertions`、`test_scenarios`、`evidence_paths`、`completion_boundary`。

## 关系与状态

- 任务以 `implements` 指向所属变更契约。
- 以 `depends-on` 指向每个必要验证和前置任务。
- 验证缺失/stale 或执行者门禁失败时保持 blocked。
- ready 表示依赖、上游哈希、验证和执行者门禁均通过。
- done 必须有通过证据；仅创建任务文档不能完成。

## Bug 快捷路径

已确认缺陷只创建复现、根因修复、关联验证和回归覆盖所需任务。修复任务关联根因/变更契约和缺陷验证；除非确有缺失决策，不创建无关用户故事、UI、调研或技术决策节点。
