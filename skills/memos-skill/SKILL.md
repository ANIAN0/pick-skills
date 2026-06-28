---
name: memos-skill
description: 使用 memos-cli 安装、更新、配置和操作 Memos。用户要求创建、读取、搜索、筛选、更新或删除 memo，管理评论与附件，安装或升级 memos-cli，配置 Memos access token，或排查该 CLI 在 PowerShell、Git Bash、MSYS2、Linux、macOS 中的调用问题时使用。
---

# Memos CLI

通过 `memos-cli` 操作 Memos。以当前二进制的 `--help` 为最终依据；不要猜测参数或绕过 CLI 直接拼 API 请求。

## 执行流程

1. 直接运行 `memos-cli <subcommand>`；参数不确定时用 `memos-cli <subcommand> --help` 或查阅本文档对应章节。
2. 命令未找到（PowerShell: `not recognized`；Bash: `command not found`）→ 按“安装”处理。
3. 命令存在但行为异常、更新后版本未变、或 PATH 中疑有多个副本 → 按“排错”处理。
4. 读取和创建操作优先使用 `--json`，解析 stdout 并检查退出码。
5. 更新、删除或创建公开 memo 前确认对象 ID、可见性和用户意图；完成后重新读取验证。

## 排错

只在命令未按预期工作或更新未生效时进入；正常流程不需要这一步。

PowerShell：

```powershell
Get-Command memos-cli -All -ErrorAction SilentlyContinue
memos-cli --version
memos-cli --help
$LASTEXITCODE
```

Git Bash / Bash：

```bash
type -a memos-cli 2>/dev/null || true
memos-cli --version
memos-cli --help
printf '%s\n' "$?"
```

更新后仍显示旧版本时，多半是 PATH 中较早的旧副本在拦截调用：PowerShell 用 `Get-Command ... -All`，Bash 用 `type -a` 列出所有副本，确认实际执行路径。处理方法是清理旧副本（一般是 PATH 上更靠前的那个），而不是给当前二进制换位置。Windows 上刚替换的副本若已被本进程加载，需关闭当前 shell 后新开会话再验证。

只在确认了实际执行路径后再决定下一步；不要在未确认的情况下删除副本。

## 安装

命令未找到时进入 [`references/install.md`](references/install.md)。该文件覆盖 Go 安装、GitHub Release 下载、本地源码构建三种方式；Go 版本要求为 1.21 或更高。

## 更新与卸载

Release/自安装版本优先使用：

```text
memos-cli update
memos-cli update --force
memos-cli uninstall
memos-cli uninstall --purge
```

`update` 下载与当前 OS/架构匹配的最新 Release，并在提供 `checksums.txt` 时校验。Windows 会在当前进程退出后替换文件；关闭或重启 shell 后再调用命令即可。`--purge` 会删除用户配置，只能在用户明确要求时使用。

通过 Go 管理源码版本时也可再次执行：

```text
go install github.com/ANIAN0/memos-cli@latest
```

## 配置

不要猜测配置位置。CLI 的优先级是 `--config`、`MEMOS_CLI_CONFIG`、随后是 `config path` 输出的候选路径。

```text
memos-cli config path
memos-cli config init
memos-cli config validate
memos-cli config show
```

`config init` 默认创建用户配置；已有文件时拒绝覆盖。只有用户明确允许时才使用 `--force`。示例：

```yaml
version: 1
instance_url: "https://memos.example.com"
access_token: "${MEMOS_TOKEN}"
default_page_size: 10
default_visibility: "PRIVATE"
```

在当前会话设置 token：

```powershell
$env:MEMOS_TOKEN = 'secret'        # PowerShell
```

```bash
export MEMOS_TOKEN='secret'        # Git Bash / Bash
```

保留 `${MEMOS_TOKEN}` 插值，不要把 token 写入命令、日志或回复。`config show` 默认脱敏；不要用 `--redact=false` 暴露 token。使用 `memos-cli whoami` 验证实例和凭据。

当前实现中，创建命令不能可靠地继承 `default_visibility`，列表也不应依赖 `default_page_size`。为获得确定行为，创建时显式传 `--visibility`，列表时显式传 `--page-size`。

## Shell 规则

- PowerShell 调用当前目录的 `.exe` 使用 `& '.\memos-cli.exe' ...`。
- Git Bash 调用当前目录二进制使用 `./memos-cli.exe`；本地附件路径包含空格时必须加引号。
- 全局参数统一放在子命令前，例如 `memos-cli --json --timeout 120 memo list`。
- PowerShell 和 Bash 都用单引号保护 Memos filter 表达式；标签列表整体加引号。
- 不要使用 `MSYS_NO_PATHCONV`：memos-cli 参数没有 FileBrowser 式远程绝对路径，禁用转换反而可能破坏本地附件路径。

## Memo 命令

```text
memos-cli memo create --content <text> --visibility PRIVATE|PROTECTED|PUBLIC [--tags "tag1,tag2"]
memos-cli memo get <id>
memos-cli memo list [--page-size N] [--page-token TOKEN] [--filter EXPR] [--sort FIELD]
memos-cli memo update <id> [--content <text>] [--visibility VALUE] [--tags "tag1,tag2"]
memos-cli memo delete <id>
memos-cli memo search <query> [--page-size N]
```

ID 可传数字 `123` 或完整名称 `memos/123`。创建后从 JSON 的 `name` 字段保存真实 ID，不要根据列表位置推断。

示例：

```powershell
$memo = memos-cli --json memo create --content '会议记录' --visibility PRIVATE --tags 'work,meeting' | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "memos-cli failed: $LASTEXITCODE" }
memos-cli --json memo get $memo.name
```

```bash
memo_json="$(memos-cli --json memo create --content '会议记录' --visibility PRIVATE --tags 'work,meeting')" || exit $?
memo_name="$(jq -r '.name' <<<"$memo_json")"
memos-cli --json memo get "$memo_name"
```

多行内容没有 stdin 或 `--file` 参数，先读入变量：

```powershell
$content = Get-Content -Raw '.\memo.md'
memos-cli memo create --content $content --visibility PRIVATE
```

```bash
content="$(<./memo.md)"
memos-cli memo create --content "$content" --visibility PRIVATE
```

注意：

- `memo update` 只更新显式提供且非空的字段。先 `memo get`，再更新，再读取验证。
- 当前实现不能通过 `--tags ''` 可靠清空全部标签；不要声称已清空。
- `memo search` 会构造 `content.contains(...)` 过滤；查询词包含双引号时可能形成无效表达式，改用经服务端支持的 `memo list --filter` 或明确报告限制。
- filter 语法由 Memos 服务端版本决定；先用小 `--page-size` 验证，不要自行改写用户表达式。
- 删除和改为 `PUBLIC` 都是高影响操作，执行前必须核对 memo 内容和 ID。

## 评论命令

```text
memos-cli comment list <memo-id>
memos-cli comment create <memo-id> --content <text>
```

评论创建的 `--content` 是必填项。使用 memo 的数字 ID 或 `memos/<id>`，完成后重新列出评论验证。

## 附件命令

```text
memos-cli attachment upload <local-file>
memos-cli attachment list [--page-size N]
memos-cli attachment get <id> --output <local-file>
memos-cli attachment delete <id>
```

附件 ID 可传数字或 `attachments/<id>`。自动化下载必须显式使用 `--output`：当前实现宣称可使用原文件名，但省略输出路径会创建文件失败。下载后检查文件存在且大小非零。删除前先用列表确认 ID、文件名和大小。

## 机器可读输出

列表类 JSON 固定为 `{"count":N,"items":[...]}`；创建、获取等单对象直接输出对象；错误写入 stderr 为 `{"code":N,"error":"..."}`。

PowerShell：

```powershell
$result = memos-cli --json memo list --page-size 20 | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "memos-cli failed: $LASTEXITCODE" }
$result.items
```

Git Bash / Bash：

```bash
json="$(memos-cli --json memo list --page-size 20)" || exit $?
jq '.items' <<<"$json"
```

退出码：`0` 成功，`1` 客户端/HTTP 4xx，`2` 服务端/HTTP 5xx，`3` 网络或超时，`4` 配置错误。使用 `--verbose` 排障，但不要回传 Authorization header 或 token。

## 补全

PowerShell 当前会话：

```powershell
memos-cli completion powershell | Out-String | Invoke-Expression
```

Git Bash 当前会话：

```bash
source <(memos-cli completion bash)
```

只在用户要求时将补全脚本持久写入 shell 配置。
