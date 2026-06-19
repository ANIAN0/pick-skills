# 评审发现契约

## 必填字段

- `severity`: BLOCKER、HIGH、MEDIUM 或 LOW。
- `responsible_node`: 最早需要修复的稳定节点 ID。
- `impact_set`: 影响分析产出的有序 `{node_id, reason, via, depth}`。
- `close_conditions`: 具体契约、行为或验证条件。
- `close_evidence`: 证明各条件的 Evidence ID 或持久产物路径。
- `status`: 使用公共生命周期；打开时为 blocked/in_progress，关闭门禁通过后才 done。

还应记录观察节点、责任 Skill、问题、影响、所需修复、调研任务 ID、创建/更新时间和责任节点当前哈希。

## 阻断行为

BLOCKER/HIGH 阻断责任节点和可执行影响项。完整 impact_set 保留 `report-only:references` 供知情，但从 stale、阻断和恢复输入中排除。MEDIUM/LOW 不自动阻断无关工作；只有共享 Schema、工具或契约本身无效且有证据时才全局阻断。

## 关闭门禁

只有以下全部满足才将 Finding 设为 done：责任 Skill 已修复责任节点；语义哈希和确认有效；影响已重算并保存；关闭条件全部验证；close_evidence 真实可读；受影响节点已复核且没有阻断级子 Finding。仅写“已修复”不能关闭。
