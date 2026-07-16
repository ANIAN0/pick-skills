# 本地工具

只在生成来源账本、执行严格 Wiki 自检，或处理现有 OKF bundle、`project-kb/`、本地检索和单文件可视化时读取。工具不替代 profile 的语义审计和独立审查。

命令中的 `<skill-dir>` 是同时包含 `SKILL.md` 和 `scripts/` 的 skill 根目录。

## 任意 Wiki 的覆盖与链接审计

```text
python <skill-dir>/scripts/audit_wiki.py inventory \
  --project-root <项目根> \
  --wiki-root <Wiki 相对项目根路径> \
  --authoritative-root docs

python <skill-dir>/scripts/audit_wiki.py validate \
  --project-root <项目根> \
  --wiki-root <Wiki 相对项目根路径>
```

`inventory` 在 `<wiki-root>/_meta/coverage.json` 创建或同步全量文件账本，新文件默认 `pending`；扫描不读取 `.gitignore`，只应用生成目录与显式排除规则。Agent 逐文件更新处置后运行 `validate`；后者重新扫描项目，并把漏项、失效条目、`pending`、不存在目标页、断链和无效来源路径作为错误。

## 现有 project-kb

```text
python <skill-dir>/scripts/kb_cli.py init-project --project-root <项目根>
python <skill-dir>/scripts/kb_cli.py list-kb --project-root <项目根> --path <可选子目录>
python <skill-dir>/scripts/kb_cli.py read-kb --project-root <项目根> --path <相对文件>
python <skill-dir>/scripts/kb_cli.py search-kb --project-root <项目根> --query <正则> --path <可选子目录>
```

`init-project` 只初始化兼容的内部项目知识库骨架。个人知识库、公开项目 Wiki 和产品 Wiki 按各自 profile 设计，不用该命令套用项目结构。

## 写入与验证

```text
python <skill-dir>/scripts/kb_cli.py write-concept \
  --project-root <项目根> \
  --path <子目录>/<slug>.md \
  --frontmatter '<JSON 或 YAML>' \
  --content '<Markdown 正文>' \
  --mode create|update

python <skill-dir>/scripts/kb_cli.py validate-project --project-root <项目根> --profile project
python <skill-dir>/scripts/kb_cli.py validate-project --project-root <项目根> --profile okf
```

`project` 检查现有 `project-kb` 的加强契约；`okf` 只检查外部 bundle 的宽容兼容性。两者都不验证个人或产品 profile 的内容关系，仍需执行质量与检索验收。

## 可视化

```text
python <skill-dir>/scripts/kb_cli.py viz --project-root <项目根> --output <可选路径>
```

默认生成 `<project-kb>/viz.html`。该文件是可重建视图，不是知识源；不手工维护其中的正文。

## 直接文件操作

简单读取、迁移和 profile 维护优先使用文件工具与 `rg`。写入后至少检查 frontmatter、相对链接、稳定身份、索引和 Git diff。CLI 返回 `error` 非空或 `errors` 非空时报告诊断；依赖缺失时结果为 `not_verified`，不使用正则近似 YAML 后宣称验证通过。
