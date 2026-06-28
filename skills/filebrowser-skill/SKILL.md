---
name: filebrowser-skill
description: 操作 FileBrowser 远程文件（上传、下载、浏览、搜索、移动、复制、删除、预览、分享）；管理登录与配置；安装或升级 filebrowser-cli；或跨 PowerShell、Git Bash、MSYS2、Linux、macOS 排查调用问题。
---

# FileBrowser CLI

通过 `filebrowser-cli` 完成 FileBrowser 操作。以当前二进制的 `--help` 为最终依据；不要猜测参数，不要把本地路径和 FileBrowser 远程路径混用。

## 执行流程

1. 直接运行 `filebrowser-cli <subcommand>`；参数不确定时用 `filebrowser-cli <subcommand> --help` 或查阅本文档对应章节。
2. 命令未找到（PowerShell: `not recognized`；Bash: `command not found`）→ 按“安装”处理。
3. 命令存在但行为异常、更新后版本未变、或 PATH 中疑有多个副本 → 按“排错”处理。
4. 对读取操作优先使用 `--json`；解析 stdout，并检查退出码。
5. 写入、覆盖、移动、删除或创建公开分享前，确认目标路径和用户意图；操作后读取验证。

## 排错

只在命令未按预期工作或更新未生效时进入；正常流程不需要这一步。

PowerShell：

```powershell
Get-Command filebrowser-cli -All -ErrorAction SilentlyContinue
filebrowser-cli --version
filebrowser-cli --help
$LASTEXITCODE
```

Git Bash / Bash：

```bash
type -a filebrowser-cli 2>/dev/null || true
filebrowser-cli --version
filebrowser-cli --help
printf '%s\n' "$?"
```

更新后仍显示旧版本时，多半是 PATH 中较早的旧副本在拦截调用：PowerShell 用 `Get-Command ... -All`，Bash 用 `type -a` 列出所有副本，确认实际执行路径。处理方法是清理旧副本（一般是 PATH 上更靠前的那个），而不是给当前二进制换位置。Windows 上刚替换的副本若已被本进程加载，需关闭当前 shell 后新开会话再验证。

只在确认了实际执行路径后再决定下一步；不要在未确认的情况下删除副本。

## 安装

命令未找到时进入 [`references/install.md`](references/install.md)。该文件覆盖 Go 安装、GitHub Release 下载、本地源码构建三种方式；Go 版本要求为 1.21 或更高。

## 更新与卸载

Release/自安装版本优先使用：

```text
filebrowser-cli update
filebrowser-cli update --force
filebrowser-cli uninstall
filebrowser-cli uninstall --purge
```

`update` 从最新 GitHub Release 下载匹配当前 OS/架构的资产，并在提供 `checksums.txt` 时校验。Windows 会安排在当前进程退出后替换文件；关闭或重启 shell 后再调用命令即可。`--purge` 会删除用户配置，仅在用户明确要求时使用。

如果通过 `go install` 管理源码版本，也可再次执行：

```text
go install github.com/ANIAN0/filebrowser-cli@latest
```

## 配置

不要手工猜测配置文件位置。CLI 的优先级是 `--config`、`FILEBROWSER_CLI_CONFIG`、随后是 `config path` 输出的候选路径。

```text
filebrowser-cli config path
filebrowser-cli config init
filebrowser-cli config validate
filebrowser-cli config show
```

`config init` 默认创建用户配置；已有文件时拒绝覆盖。只有用户明确允许时才用 `--force`。示例配置：

```yaml
version: 1
instance_url: "https://files.example.com"
username: "admin"
password: "${FB_PASSWORD}"
default_expires: 24
default_unit: "hours"
```

在当前会话设置密码：

```powershell
$env:FB_PASSWORD = 'secret'       # PowerShell
```

```bash
export FB_PASSWORD='secret'       # Git Bash / Bash
```

优先保留 `${FB_PASSWORD}`，不要把密码写进命令、日志或回复。`config show` 默认脱敏；不要使用 `--redact=false` 暴露密码。认证流程：

```text
filebrowser-cli login
filebrowser-cli whoami
filebrowser-cli renew
filebrowser-cli logout
```

配置含用户名和密码时，过期 token 可自动重新登录。

## Shell 和路径规则

- FileBrowser 远程路径始终使用以 `/` 开头的 POSIX 路径，例如 `/docs/report.pdf`。
- 本地路径按当前 OS 书写，并始终引用包含空格的路径。
- Windows Git Bash/MSYS2 会转换 `/docs`。CLI 会尝试自动还原；若环境无法识别且远程路径被改写，可临时设置 `MSYS2_ARG_CONV_EXCL='*'`，同时把本地文件参数转换为 Windows 路径。
- 在禁用参数转换时，Git Bash 本地路径使用 `cygpath -w`：`local_win="$(cygpath -w './report.pdf')"`。
- PowerShell 调用下载的 `.exe` 使用调用运算符：`& '.\filebrowser-cli.exe' ...`。
- 全局参数统一放在子命令前，例如 `filebrowser-cli --json --timeout 120 ls /`。

Git Bash 的混合本地/远程上传示例：

```bash
local_win="$(cygpath -w './report.pdf')"
MSYS2_ARG_CONV_EXCL='*' filebrowser-cli upload "$local_win" '/docs/report.pdf'
```

正常情况下先直接执行，不要无条件禁用路径转换。

## 文件与目录命令

```text
filebrowser-cli ls [remote-path]
filebrowser-cli tree [remote-path]
filebrowser-cli info [remote-path]
filebrowser-cli mkdir <remote-path>
filebrowser-cli upload <local-path> [remote-path]
filebrowser-cli download <remote-path> [local-path]
filebrowser-cli cp <remote-src> <remote-dst>
filebrowser-cli mv <remote-src> <remote-dst>
filebrowser-cli rm <remote-path>
filebrowser-cli search <remote-path> <query> [--limit N]
```

关键约束：

- `upload` 没有 `--override` 参数；当前实现始终以覆盖模式上传。覆盖前先用 `info` 检查目标。
- 自动化下载时显式提供本地输出路径，避免依赖当前目录和默认文件名。
- `rm`、`mv`、`cp` 前验证源和目标，完成后用 `info` 或 `ls` 验证。
- 搜索参数顺序固定为路径在前、查询词在后。

## 预览与分享

```text
filebrowser-cli preview <remote-path> --size thumb --output <local-file>
filebrowser-cli preview <remote-path> --size big --output <local-file>
filebrowser-cli share create <remote-path> [--expires N --unit seconds|minutes|hours|days] [--password VALUE]
filebrowser-cli share list
filebrowser-cli share info <remote-path>
filebrowser-cli share delete <hash>
```

预览内容是二进制；agent 必须使用 `--output`，不要把它写到终端。分享密码属于敏感信息，不要回显。文本模式只输出相对下载 URL `/api/public/dl/<hash>`；需要完整链接时，将其与配置中的 `instance_url` 拼接，不要臆造域名。

## 机器可读输出

列表类 JSON 固定为 `{"count":N,"items":[...]}`，单对象直接输出对象，错误写入 stderr 为 `{"code":N,"error":"..."}`。

PowerShell：

```powershell
$result = filebrowser-cli --json ls '/docs' | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "filebrowser-cli failed: $LASTEXITCODE" }
$result.items
```

Git Bash / Bash：

```bash
json="$(filebrowser-cli --json ls '/docs')" || exit $?
jq '.items' <<<"$json"
```

退出码：`0` 成功，`1` 客户端/HTTP 4xx，`2` 服务端/HTTP 5xx，`3` 网络或超时，`4` 配置错误。使用 `--verbose` 排障，但避免把含凭据的日志回传。

## 补全

PowerShell 当前会话：

```powershell
filebrowser-cli completion powershell | Out-String | Invoke-Expression
```

Git Bash 当前会话：

```bash
source <(filebrowser-cli completion bash)
```

只在用户要求时将补全脚本持久写入 shell 配置。
