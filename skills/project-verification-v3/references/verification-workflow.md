# Test Plan 与验证报告工作流

Test Plan 在执行前与 Tech/Task 同目录生成；Verification Report 在执行后形成。二者共享 requirements `scope_ref`。V-* 是 Test Plan 内部条目，真实记录来自 Task List，报告保留命令、exit code、输出、时间、executor 和资产路径。

失败、缺资产、缺负向验证或 not_verified 不得形成通过结论。Bug 路径必须保留 reproduce、fix、regress 三类记录。G-ACCEPT 只确认真实报告，不替代验证。
