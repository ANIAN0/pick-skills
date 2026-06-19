---
name: filebrowser-skill
description: 使用 filebrowser-cli 安装、更新、配置和操作 FileBrowser。用户要求上传、下载、浏览、搜索、移动、复制、删除、预览或分享远程文件，管理 FileBrowser 登录与配置，安装或升级 filebrowser-cli，或排查该 CLI 在 PowerShell、Git Bash、MSYS2、Linux、macOS 中的调用问题时使用。
---

# FileBrowser CLI

通过 `filebrowser-cli` 完成 FileBrowser 操作。以当前二进制的 `--help` 为最终依据；不要猜测参数，不要把本地路径和 FileBrowser 远程路径混用。

## 执行流程

1. 判断当前 shell 和操作系统。
2. 定位命令并检查是否有多个副本。
3. 命令不存在时按“安装”处理；用户要求升级时按“更新”处理。
4. 运行 `config path`、`config validate`，必要时初始化配置。
5. 对读取操作优先使用 `--json`；解析 stdout，并检查退出码。
6. 写入、覆盖、移动、删除或创建公开分享前，确认目标路径和用户意图；操作后读取验证。

## 定位和诊断

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

如果存在多个副本，先确定实际执行路径。更新后仍显示旧版本时，通常是 PATH 中较早的旧副本：PowerShell 用 `Get-Command ... -All`，Bash 用 `type -a` 排查。不要在未确认目标的情况下删除副本。

## 安装

优先使用已有的 Go 工具链安装；没有 Go 时下载 Release 二进制。Go 版本要求为 1.21 或更高。

### 使用 Go 安装

两个 shell 都可执行：

```text
go install github.com/ANIAN0/filebrowser-cli@latest
```

PowerShell 将 Go bin 加入当前会话：

```powershell
$goBin = go env GOBIN
if (-not $goBin) { $goBin = Join-Path (go env GOPATH) 'bin' }
$env:Path = "$goBin;$env:Path"
filebrowser-cli --version
```

Git Bash / Bash：

```bash
go_bin="$(go env GOBIN)"
[ -n "$go_bin" ] || go_bin="$(go env GOPATH)/bin"
export PATH="$go_bin:$PATH"
filebrowser-cli --version
```

只在用户要求持久化时修改 PowerShell 用户 PATH 或 `~/.bashrc`。当前会话可用并不代表新终端已持久生效。

### 下载 GitHub Release

Release 资产命名为 `filebrowser-cli-<os>-<arch>`，Windows 带 `.exe`。常见值：`windows-amd64.exe`、`windows-arm64.exe`、`linux-amd64`、`linux-arm64`、`darwin-amd64`、`darwin-arm64`。

PowerShell（示例为 Windows amd64）：

```powershell
$asset = 'filebrowser-cli-windows-amd64.exe'
$base = 'https://github.com/ANIAN0/filebrowser-cli/releases/latest/download'
Invoke-WebRequest "$base/$asset" -OutFile ".\$asset"
Invoke-WebRequest "$base/checksums.txt" -OutFile '.\checksums.txt'
$expected = ((Select-String -Path '.\checksums.txt' -Pattern ([regex]::Escape($asset))).Line -split '\s+')[0]
$actual = (Get-FileHash ".\$asset" -Algorithm SHA256).Hash
if (-not $expected -or $actual.ToLowerInvariant() -ne $expected.ToLowerInvariant()) { throw 'checksum mismatch' }
& ".\$asset" install
```

Git Bash / Bash（Windows Git Bash 示例）：

```bash
asset='filebrowser-cli-windows-amd64.exe'
base='https://github.com/ANIAN0/filebrowser-cli/releases/latest/download'
curl -fL "$base/$asset" -o "$asset"
curl -fL "$base/checksums.txt" -o checksums.txt
sha256sum -c checksums.txt --ignore-missing
"./$asset" install
```

`install` 把当前二进制复制到默认用户目录：Windows 为 `%LOCALAPPDATA%\Programs\filebrowser-cli`，Linux/macOS 为 `~/.local/bin`。也可使用 `install --dir <目录>`。根据命令输出把该目录加入 PATH，然后重新定位并验证版本。

### 从本地源码安装

仅在用户明确要使用源码版本时进入源码目录。先运行 `git status --short`，保留用户改动，再执行测试和构建。

PowerShell：

```powershell
go test ./...
New-Item -ItemType Directory -Force .\bin | Out-Null
go build -o .\bin\filebrowser-cli.exe .
& .\bin\filebrowser-cli.exe install
```

Git Bash / Bash：

```bash
go test ./...
mkdir -p ./bin
go build -o ./bin/filebrowser-cli.exe .   # Windows Git Bash
./bin/filebrowser-cli.exe install
```

在 Linux/macOS 将输出名改为 `./bin/filebrowser-cli`。

## 更新与卸载

Release/自安装版本优先使用：

```text
filebrowser-cli update
filebrowser-cli update --force
filebrowser-cli uninstall
filebrowser-cli uninstall --purge
```

`update` 从最新 GitHub Release 下载匹配当前 OS/架构的资产，并在提供 `checksums.txt` 时校验。Windows 会安排在当前进程退出后替换文件；关闭或重启 shell，再运行 `Get-Command -All`/`type -a` 和 `--version` 验证。`--purge` 会删除用户配置，仅在用户明确要求时使用。

如果通过 `go install` 管理源码版本，也可再次执行：

```text
go install github.com/ANIAN0/filebrowser-cli@latest
```

更新必须作用于 PATH 实际解析到的副本；不要假设刚更新的文件就是当前命令。

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
