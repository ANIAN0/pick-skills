---
name: project-development-review-v3
description: 将项目研发 v3 的评审发现聚合为范围化 Review Report，REV-* 作为内部条目定位责任文档和 R/A/F/D/C/T/V，并按真实影响集局部重审。
---

# 局部评审报告 v3

1. 使用公共影响工具计算责任文档的完整 impact set。
2. 调用 `scripts/review_report.py` 在责任范围 supporting/ 下创建一个 Review Report；每个 REV-* 是内部条目，不建 Finding 文件。
3. Finding 保存 responsible_document/item、owner skill、severity、impact set、review scope、close conditions/evidence。
4. report-only 弱引用只审计，不进入阻断范围；BLOCKER/HIGH 未关闭时阻断受影响范围。
5. 关闭前必须证明责任文档语义已变化，证据是可解析的 passed 记录且绑定 finding ID，并覆盖重算后的全部 review_scope；任一条件缺失不得关闭。
