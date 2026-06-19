# 确认协议

## 字段

确认前 `confirmation: null`。确认快照：

```yaml
confirmation:
  content_hash: sha256:<64 位小写十六进制>
  confirmed_at: <带时区偏移的 ISO 8601 时间>
  confirmed_by: <人工或已批准执行者身份>
```

content_hash、confirmed_at 必填；可取得执行者身份时 confirmed_by 必填，且不得编造。

## 语义哈希

1. 只读解析 Frontmatter 和正文。
2. 移除完整 confirmation、status，以及 backlinks、children、computed_impact、last_indexed_at 等纯派生键。
3. 剩余 Frontmatter 按键排序、紧凑分隔、保留 Unicode，序列化为 UTF-8 JSON。
4. 正文换行统一 LF，移除各行尾空格，保留有意义空行并确保末尾一个 LF。
5. 对 `frontmatter_json + "\n---body---\n" + normalized_body` 计算 SHA-256，加 `sha256:` 前缀。

路径、派生索引、status、确认时间和执行者不参与哈希；parent、relations、revision、标题、节点类型、语义扩展字段和正文参与。仅生命周期变化不使决策失效。

## 有效性与失效

存储哈希必须与当前语义哈希完全一致。语义字段或正文变化使确认失效；纯路径移动不失效，parent 变化会失效。失配产生有效 stale，并阻止下游推进，直到责任方评审影响并重新确认。只读脚本仅报告，不覆盖旧确认历史。

## 消费行为

哈希匹配且已覆盖当前决策时直接消费，不重复提问。失配时先识别变更节点和相关影响，再聚焦重新确认；不重新确认无关祖先、后代或弱引用。只有真实确认后才记录新时间和执行者。
