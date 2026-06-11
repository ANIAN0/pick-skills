# FileBrowser Skill

管理和操作 FileBrowser 文件管理系统。

## 功能

- 文件上传、下载、删除、移动、复制
- 目录管理和浏览
- 文件分享和链接管理
- 文件搜索
- 图片预览

## 安装

### 方式一：从 GitHub Release 下载预编译二进制（推荐）

访问 [GitHub Releases](https://github.com/ANIAN0/filebrowser-cli/releases) 下载对应平台的二进制文件：

- Windows: `filebrowser-cli-windows-amd64.exe`
- Linux: `filebrowser-cli-linux-amd64`
- macOS: `filebrowser-cli-darwin-amd64`

下载后重命名为 `filebrowser-cli`（Windows 为 `filebrowser-cli.exe`）并添加到 PATH。

### 方式二：使用 go install

```bash
go install github.com/ANIAN0/filebrowser-cli@latest
```

### 方式三：从源码编译

```bash
git clone https://github.com/ANIAN0/filebrowser-cli.git
cd filebrowser-cli
make build
# 二进制文件在 bin/filebrowser-cli
```

## 配置

创建配置文件 `~/.config/filebrowser-cli/config.yaml`：

```yaml
version: 1
instance_url: "http://your-server:8080"
username: "admin"
password: "${FB_PASSWORD}"
```

设置环境变量：

```bash
export FB_PASSWORD="your-password"
```

## 使用示例

```bash
# 登录
filebrowser-cli login

# 列出文件
filebrowser-cli ls /

# 上传文件
filebrowser-cli upload ./report.pdf /documents/report.pdf

# 创建分享链接
filebrowser-cli share create /documents/report.pdf

# 搜索文件
filebrowser-cli search / "report"
```

## 文档

- [SKILL.md](SKILL.md) - 完整的 skill 文档
- [references/](references/) - API 接口文档
