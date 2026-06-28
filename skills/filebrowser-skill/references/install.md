# FileBrowser CLI 安装

命令未找到时进入这里。优先 Go 安装；没有 Go 时下载 Release 二进制；只有在用户明确要求源码版本时从本地源码构建。Go 版本要求为 1.21 或更高。

## 使用 Go 安装

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

## 下载 GitHub Release

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

## 从本地源码安装

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
