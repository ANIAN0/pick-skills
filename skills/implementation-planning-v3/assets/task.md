---
type: project-development/node
id: TASK-001
node_type: task
title: 替换为一个可独立验证的任务
status: blocked
parent: CHANGE-001
revision: 1
relations:
  - type: implements
    target: CHANGE-001
    scope: project
  - type: depends-on
    target: VER-001
    scope: project
confirmation: null
criticality: core
infrastructure: false
risk: high
executor_requirement: senior
executor_profile: null
approval: null
blocking_reason: 等待 senior 执行者或明确审批
input_confirmation_hashes:
  CHANGE-001: sha256:replace-with-confirmed-hash
verification_ids:
  - VER-001
target_files: []
target_symbols: []
execution_assertions:
  must_disappear: []
  must_appear: []
  must_propagate: []
  must_persist: []
test_scenarios: []
evidence_paths: []
completion_boundary: []
---

## 步骤

列出受该变更契约约束的实施步骤。

## 相邻接口

记录执行者必须保留的调用方、消费方、Schema 或节点。

## 禁止事项

列出局部范围排除项和禁止使用的完成捷径。
