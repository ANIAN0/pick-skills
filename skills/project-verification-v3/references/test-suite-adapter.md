# 测试套件适配器

## 输入

`test-suite-maintainer` 适配器只有在验收/E2E 路径已真实通过后才运行。输入至少包含 `verification_ids`、`target_environment`、`real_data`、command/observation、screenshot paths、cleanup result、完整步骤、负向场景、原始证据和目标测试目录。

## 调用顺序

1. 先运行真实流程，再生成或修改自动化；检查项目既有测试框架、约定和相邻测试。
2. 选择最小适配层，不另建平行测试体系。
3. 将真实步骤映射为 setup/action/assertion/cleanup。
4. 保留正向及必要负向观察和来源 ID。
5. 创建/更新脚本及 `test-manifest.yaml`，再运行生成或更新后的测试。
6. 保存命令、退出码和产物；失败则回写责任节点。

## 输出映射

自动化资产记录脚本路径、框架、运行命令、覆盖的 Acceptance/Verification、环境要求、最近证据和维护责任。写入前确认路径真实存在且脚本确实运行。项目节点引用路径和证据，不嵌入整份脚本。

## 失败回写

脚本无法稳定复现真实流程、依赖不可用或执行失败时，不得标记回归已建立。按 `test-asset`、`environment-data`、`product-code` 三类归因，保持 fail 并保存失败证据，再创建相应 Root Cause/Finding/blocked 状态。
