# 本地工具

只在初始化、inventory、queue transaction、严格校验、查询或可视化时读取。`<skill-dir>` 是包含 `SKILL.md` 和 `scripts/` 的 skill 根。

## 初始化

```text
python <skill-dir>/scripts/kb_cli.py init-project --project-root <项目根>
```

只创建 `index.md/purpose.md/INSTRUCTIONS.md/log.md/_meta/schema.md/_meta/state.json/_meta/capture-registry.json`，不生成业务正文。先填写 state.json 的 design 字段；未满足门槛时 queue `sync` 会拒绝进入 growing。

## Inventory 与队列

对话中发现问题、决定或经验时，先创建独立来源：

```text
python <skill-dir>/scripts/ingest_queue.py capture \
  --project-root <项目根> --okf-root <OKF 根> \
  --kind user-decision|problem-report|observation|experience|resolution \
  --summary <原始陈述摘要> --scope <权威或适用范围> \
  [--details <上下文>] [--conversation-ref <任务标识>] \
  [--related-path <项目路径>] [--evidence-ref <调查线索>] \
  [--requested-action <后续动作>] [--resolves <原 EVD-ID>]
```

`resolution` 必须带已存在的 `--resolves EVD-*`。默认来源根是 `knowledge-sources/captures/`；命令同时更新 `_meta/capture-registry.json`，拒绝输出根和 inventory 排除路径。知识库已处于 `growing` 且队列存在时自动 inventory + sync，未真正入队会返回错误；其他阶段返回 `awaiting_inventory`。Capture 成功只表示原始陈述已保存，不表示正式知识或技术事实已确认。

```text
python <skill-dir>/scripts/audit_wiki.py inventory \
  --project-root <项目根> --okf-root <OKF 根> \
  --profile personal|project|product \
  --authoritative-root <权威来源根>

python <skill-dir>/scripts/ingest_queue.py sync \
  --project-root <项目根> --okf-root <OKF 根>

python <skill-dir>/scripts/ingest_queue.py status \
  --project-root <项目根> --okf-root <OKF 根>

python <skill-dir>/scripts/ingest_queue.py next \
  --project-root <项目根> --okf-root <OKF 根>
```

先 inventory，后 sync。每次继续前运行 `next`，不凭目录顺序自行挑文件。

## 单来源事务

```text
python <skill-dir>/scripts/ingest_queue.py claim \
  --project-root <项目根> --okf-root <OKF 根> --source <来源路径>

python <skill-dir>/scripts/ingest_queue.py record-analysis \
  --project-root <项目根> --okf-root <OKF 根> --source <来源路径> \
  --artifact <analysis.json>

python <skill-dir>/scripts/ingest_queue.py record-write \
  --project-root <项目根> --okf-root <OKF 根> --source <来源路径> \
  --target <OKF 相对目标页> --shared-target <共享写入页>

python <skill-dir>/scripts/ingest_queue.py finish \
  --project-root <项目根> --okf-root <OKF 根> --source <来源路径>
```

多个 target/shared target 分别重复传参；参数集合必须与固定 artifact 完全一致。无目标时不传。`finish` 内部逐 claim/target 运行来源级 validator；失败时不提交指纹。

失败与 review：

```text
python <skill-dir>/scripts/ingest_queue.py fail \
  --project-root <项目根> --okf-root <OKF 根> --source <来源路径> \
  --error <错误说明> [--rollback]

python <skill-dir>/scripts/ingest_queue.py resolve-review \
  --project-root <项目根> --okf-root <OKF 根> --review-id <REV-ID> \
  --resolution <裁决> --evidence <证据>
```

`--rollback` 由工具恢复 record-analysis 时固定的 coverage 与目标页快照；没有有效快照就保持 blocked。不要人工声称已回滚。

完成一个来源后，下一次用户明确要求继续时开启新 cycle：

```text
python <skill-dir>/scripts/ingest_queue.py continue \
  --project-root <项目根> --okf-root <OKF 根>
```

## 验证

```text
python <skill-dir>/scripts/audit_wiki.py validate \
  --project-root <项目根> --okf-root <OKF 根> \
  --profile <profile> --source <当前来源>

python <skill-dir>/scripts/audit_wiki.py validate \
  --project-root <项目根> --okf-root <OKF 根> --profile <profile>

python <skill-dir>/scripts/kb_cli.py validate-project \
  --project-root <项目根> --profile write
```

第一条是来源级；第二条只用于全库完成/发布；第三条检查 OKF 写入格式。外部 bundle 的宽容读取才使用 `--profile okf`。

范围里程碑在 `_meta/milestones/<id>.json` 写明问题、来源指纹、全部通过的 retrieval tests 和独立 review 后运行：

```text
python <skill-dir>/scripts/ingest_queue.py validate-milestone \
  --project-root <项目根> --okf-root <OKF 根> \
  --milestone <_meta/milestones/id.json>
```

工具只接受当前仍为 done 的绑定指纹，并逐来源重跑 validator。后续 `sync` 发现任一绑定来源不再是该指纹的 done 状态时，自动把 milestone 标为 stale。

## 查询与视图

```text
python <skill-dir>/scripts/kb_cli.py search-kb --project-root <项目根> --query <正则>
python <skill-dir>/scripts/kb_cli.py read-kb --project-root <项目根> --path <相对文件>
python <skill-dir>/scripts/kb_cli.py viz --project-root <项目根> --output <可选路径>
```

CLI 的 `error/errors` 非空即失败；依赖缺失为 `not_verified`。`viz.html` 是可重建视图，不是知识源。
