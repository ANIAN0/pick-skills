# 测试套件适配

输入包含 Test Plan document ID、scope_ref、V-*、目标命令和预期资产。输出必须是实际命令、exit code、stdout/stderr、timestamp、executor、artifact paths 和 result，并回写 Task List/Verification Report。测试 Skill 调用失败必须保留，不得改写为 passed。
