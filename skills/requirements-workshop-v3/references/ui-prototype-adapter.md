# UI 与原型适配

## 输入契约

只有请求包含页面、视觉状态、交互流程、UI 文档或高保真原型时才创建 UI 分支。每个 UI 输入节点应记录：

- 对应能力和验证 ID；
- 页面/组件责任；
- 正常、空、加载、错误、禁用等必要状态；
- 用户动作、可观察反馈和无障碍要求；
- 目标设备或断点；
- 原型交付物与验收边界。

视觉偏好不明确且会影响交付时询问用户；可从既有设计系统或代码确定时先检查证据。

传给下游生成 Skill 的契约字段必须包含 `capability_id`、`capability_parent`、`verification_ids`、页面/状态/交互要求和验收边界。

## Skill 选择

- UI 需求文档调用 `ui-requirements-doc`；HTML 原型调用 `html-prototype-generator`；Vue 原型调用 `vue-prototype-generator`。
- 需要位图素材时才调用图像生成能力。
- 已有设计系统时优先复用其组件和 Token，不建立平行视觉规范。

## 输出与证据

原型或 UI 文档必须以 `specifies` 关联责任能力，以 `evidences` 关联适用验证/任务，并记录 `artifact_paths`、`generator_skill`、真实文件路径、状态覆盖和观察证据。需求节点只保存摘要及链接，不嵌入完整生成代码。已有页面列表确认仍有效时不得重复询问。

## 失败处理

工具不可用、浏览器未验证、资产缺失或关键状态未覆盖时写入 failed/blocked Evidence，保持 blocked/not_verified 并记录所缺条件；不得用静态字符串检查声称 UI 已完成。
