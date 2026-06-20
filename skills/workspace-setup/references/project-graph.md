# 项目图目录

`workspace-setup` 在当前实际版本目录下创建：

```text
workplace/{current_version}/graph/
├── stories/
└── .derived/
```

- `stories/` 保存项目研发 v3 的层级 Markdown 事实文档。初始化时为空；流程仅按真实拆分创建 `US-*`、可选 `modules/M-*` 和可选 `features/F-*`。
- `.derived/` 只保存可删除重建的索引和静态视图。
- 初始化不创建示例 User Story、空 `modules/`、空 `features/` 或其他业务文档。
- 已有目录和文件保持原内容；初始化只补齐缺失目录。
- 旧项目已有 `graph/nodes/` 时保持原样并由读取器兼容；初始化器不删除、不移动、不自动迁移。

实际路径由 `workspace.workplace_dir` 与 `workspace.current_version` 组合，不能把说明中的 `{current_version}` 当成持久化目录名。

## 全局研究知识库

可在 `skillconfig.json` 中配置：

```json
{
  "knowledge": {
    "global_dir": "~/personal-kb"
  }
}
```

路径支持 `~` 和环境变量展开。相对路径相对于项目根目录。未配置时只建议并解析 `~/personal-kb`，不会由初始化器在 HOME 中自动创建。显式配置的目录必须已经存在且可读写；不可用时返回明确错误，且不会把全局报告复制到项目目录。
