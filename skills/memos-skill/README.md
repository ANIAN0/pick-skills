# Memos Skill

管理和操作 Memos 备忘录系统。

## 功能

- 创建、读取、更新、删除备忘录
- 搜索和过滤备忘录
- 管理评论
- 上传和管理附件
- 标签管理

## 安装

### 方式一：从 GitHub Release 下载预编译二进制（推荐）

访问 [GitHub Releases](https://github.com/ANIAN0/memos-cli/releases) 下载对应平台的二进制文件：

- Windows: `memos-cli-windows-amd64.exe`
- Linux: `memos-cli-linux-amd64`
- macOS: `memos-cli-darwin-amd64`

下载后重命名为 `memos-cli`（Windows 为 `memos-cli.exe`）并添加到 PATH。

### 方式二：使用 go install

```bash
go install github.com/ANIAN0/memos-cli@latest
```

### 方式三：从源码编译

```bash
git clone https://github.com/ANIAN0/memos-cli.git
cd memos-cli
make build
# 二进制文件在 bin/memos-cli
```

## 配置

创建配置文件 `~/.config/memos-cli/config.yaml`：

```yaml
version: 1
instance_url: "https://your-memos-instance.com"
access_token: "${MEMOS_TOKEN}"
```

设置环境变量：

```bash
export MEMOS_TOKEN="your-token"
```

## 使用示例

```bash
# 创建备忘录
memos-cli memo create --content "Hello World" --visibility PRIVATE

# 列出备忘录
memos-cli memo list

# 搜索备忘录
memos-cli memo search "Hello"

# 上传附件
memos-cli attachment upload ./image.png
```

## 文档

- [SKILL.md](SKILL.md) - 完整的 skill 文档
- [references/](references/) - API 接口文档
