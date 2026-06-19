# 编排契约

## 阶段责任

| 责任 | Skill/工具 |
|---|---|
| 需求、能力、验证、UI 输入 | `requirements-workshop-v3` |
| 外部调研和全局报告 | `project-research-v3` / `personal-kb` |
| 技术决策和变更契约 | `tech-design-v3` |
| 任务创建、排序和执行者门禁 | `implementation-planning-v3` |
| 代码执行和研发证据 | `plan-execution-v3` |
| 验收、E2E、回归 | `project-verification-v3` |
| Finding 和局部恢复评审 | `project-development-review-v3` |
| 图校验、影响、索引 | 公共确定性脚本 |

总控只选择和编排责任方，不复述或代做阶段专业工作。

## 优先级与阶段推进

full/extension 先规划全部就绪契约，再在依赖允许时优先执行基础设施/核心任务。计划要求分阶段交付时，先验证并验收核心路径，再扩展支撑实现，最后执行 E2E/回归和最终评审。

## 强制暂停门禁

以下情况必须暂停并持久化状态：无效图或未知关系；必需确认 stale；可执行范围内存在 BLOCKER/HIGH Finding；高风险人工决策未解决；核心/基础设施任务缺 senior/审批；环境、凭据、权限、数据创建或真实依赖缺失；验证非零、产物缺失或证据 not_verified；验收、E2E、回归、兼容或最终评审失败。

不得通过修改期望或跳过范围把暂停改成成功。

## 完成

Workflow Run done 要求：范围内必要节点均 done 且关系合法、哈希有效；所有 Verification/Task 依赖有通过 Evidence；验收/E2E/回归有真实产物；无可执行 BLOCKER/HIGH Finding；兼容和安装/发现检查通过；最终评审证据已记录。任何发布关键 blocked/not_verified 都保持非完成。
