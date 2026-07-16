# 覆盖与里程碑审查

只在 inventory、完整性审计或 operational/publish 里程碑时读取。全量发现不等于全量摄入：coverage 定义分母，queue 记录逐文件生长进度。

## Canonical inventory

`audit_wiki.py inventory` 从真实来源根递归扫描，不读取 `.gitignore`；只应用脚本内确定的版本控制/依赖/缓存目录和显式排除。`build/dist/coverage/target` 不按名称默认排除，权威根覆盖同名排除。project/product 必须声明权威根。

coverage 记录：

- 扫描状态、遍历错误、空目录、实际忽略目录和嵌套/符号链接；
- 每个文件的 SHA-256、大小、读取状态、profile 和权威范围；
- 文件 disposition、精确 evidence/claims、目标页和稳定对象。
- 对话 Capture 的 kind、scope、允许的 assertion type、事实资格与验证要求。

现有 Wiki、旧索引、Git tracked files 和入口文件都不能定义来源全集。新增或指纹变化的文件回到 `pending`；删除/移动进入 `changes.removed`。inventory 后立即运行 queue `sync`：未提交的新指纹产生 pending source task，删除产生 cleanup task。

## 文件 disposition

| 状态 | 含义 | 必需信息 |
|---|---|---|
| `mapped` | 贡献到规范页 | targets、evidence、claims、反向 sources |
| `consolidated` | 与其他来源合并 | 同上及合并理由 |
| `superseded` | 被更新来源替代 | replacement_source、目标、evidence、理由 |
| `duplicate` | 内容完全相同 | 同 SHA-256 canonical_source |
| `ignored` | 与 purpose 无关 | 可复核理由；权威来源不允许 |
| `sensitive` | 不得进入知识/发布层 | sensitivity、理由、review |
| `unsupported` | 当前无法解析 | 类型与限制；权威来源不允许 |
| `conversion_failed` / `read_failed` | 转换/读取失败 | 错误证据 |
| `pending` | 尚未完成当前指纹事务 | queue task |

`evidence` 使用 `<来源>#L行`、`#标题/ID`、`:符号` 或二进制 `#sha256:前缀`。`mapped/consolidated/superseded` 的 `claims` 必须把 evidence、目标和实际进入正文的文本绑定。权威来源不能只映射到 index。

完整性等式始终成立：

```text
discovered = 所有 disposition 数量之和
```

在 `growing` 阶段，`pending` 是公开进度，不是失败。只有声明 operational 范围或全库完成时，该范围的 `pending/read_failed/conversion_failed/blocked/not_verified` 必须为零。

## 产品对象对账

product 文档逐文件填写 `object_disposition: contains|none` 和 `objects`。顶层 `objects` 为每个稳定 ID 登记 `type/id/title/source_paths/target`，并满足：

```text
来源识别对象 = coverage.objects = 非索引 OKF 规范对象
```

扫描发现的 REQ/PRD/RULE/DEC/ITER ID 必须登记；仅为引用时用精确 evidence 记录 override。命中对象提示却标 none 的文件进入 review backlog。一个文件含多个对象时分别登记，ID/标题冲突不能静默合并。

## 三层验证

**来源级**：`validate --source <path>` 只检查当前来源、目标页和对象，允许其他任务 pending，不要求全库 review。每个 source transaction 提交前运行。

**范围里程碑**：在 `_meta/milestones/<id>.json` 固定问题范围、所含 source path + SHA-256、相关对象、检索问题和范围外 pending 摘要。对集合中每个来源运行来源级验证，再做 fresh-context review。范围外 pending 不阻塞，但必须披露。

任何原始 Capture 都不能作为 operational milestone 来源；应由独立项目证据支持被报告的技术结论，由正式决定记录承接需要稳定发布的规范结论。`user-decision` Capture 只证明用户在其 scope 内作出过决定。

Milestone 至少包含 `id/title/builder/questions/sources[{path,sha256}]/object_ids/outside_pending/retrieval_tests/review`。每项 retrieval test 绑定非空 `query/expected/result/evidence` 和 `passed`；evidence 必须指向存在的来源或 OKF 页。`review` 使用不同于 builder 的 reviewer，记录 `status: passed|failed` 与项目内 evidence。工具固定来源 coverage entry、analysis artifact、目标页、review/retrieval evidence 和 milestone artifact 的指纹；任一变化时后续 sync 自动标 stale。

**全库级**：不带 `--source` 的 `validate` 检查完整文件系统差集、所有 disposition、删除清理、全部页面/对象/链接和全库 fresh-context review。只在全库发布或声称所有来源完成时运行。

validator error 保持阻塞，生成者不能改称 warning。

## Review backlog 与 fresh-context review

逐来源 analysis 把矛盾、身份冲突、缺失权威事实和建议写入 queue 的 `review_backlog`。blocker 未解决时来源状态为 `not_verified`；resolution 必须有 evidence，后续摄入可使旧 review 自动失效或被重新判断。

里程碑 review 由未参与摄入的 fresh-context reviewer 执行。只提供项目根、OKF 根、purpose、milestone source set 和原始来源，不提供建设者自评。范围 review 绑定每个来源指纹、相关目标页摘要和 artifact SHA-256；全库 review 另绑定 `coverage_sha256/wiki_sha256`。相关来源、对象、OKF 或 artifact 变化后重新审查。

Reviewer 必须：

- 从文件系统重做一级目录、权威根、空目录、忽略目录和版本/迭代目录对账；
- 核对声明范围内全部来源任务、稳定对象、精确证据和未解决 review items；
- 从外部触发点抽查核心结论的调用/数据链路，识别目录复述、薄页和推断冒充事实；
- 执行真实检索，包含精确事实、跨页关系、历史/冲突和应返回缺口的问题。

reviewer 输出问题路径、严重性与证据。修复产生新的 queue/review 任务；重新验证前里程碑保持 `not_verified`。

## 多来源个人库

不相交来源根分别运行 inventory，manifest 放在 `<okf-root>/_meta/sources/<source-id>/`，并在 `_meta/sources.md` 登记根路径/URI、观察版本和权威范围。每个本地来源独立同步队列；外部 URI 只登记快照与访问日期。
