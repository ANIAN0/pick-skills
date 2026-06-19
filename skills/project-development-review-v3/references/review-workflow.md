# 评审工作流

## 范围

评审当前节点、直接上下文、关联证据及确定性影响输出。除非共享协议本身失效，不加载或阻断全图。

## 责任定位

从观察到问题的节点向上追踪定义与依赖，选择最早包含错误、歧义或无证据断言的节点作为 responsible_node。observed_node 保留发现位置。修复属于该节点责任 Skill，不由评审 Skill 越权完成。

## 歧义调研

问题依赖可外部验证事实时，从责任节点创建 Research Task，并以 `researches` 指向责任节点；Finding 保持打开。产品偏好或风险接受不是调研问题，必须由有权限的人决策。

## 局部恢复

调用公共影响工具得到 reason、via、depth。完整 impact_set 用于审计；剔除 report-only 弱引用后得到 actionable impact。BLOCKER/HIGH 只将责任节点和 actionable 项标记 stale/blocked，并设置最早未完成责任节点为 resume_node。

## 恢复

责任节点修复后：重新校验；重算语义哈希和确认；重算影响；验证关闭条件及证据；复核 actionable 子图；关闭 Finding；从 resume_node 继续。未受影响且哈希有效的决策或已完成任务不重放、不重复确认或执行。
