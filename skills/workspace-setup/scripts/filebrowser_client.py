#!/usr/bin/env python3
"""通过 filebrowser-cli 提供工作区同步所需的最小 FileBrowser 适配层。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


class FileBrowserCLIClient:
    """调用 filebrowser-cli，不直接访问 FileBrowser HTTP API。"""

    def __init__(self, config: Dict[str, Any]):
        self.filebrowser_config = config.get("filebrowser", {})
        self.executable = shutil.which("filebrowser-cli")
        self.last_error = ""
        self._temporary_config: Optional[tempfile.TemporaryDirectory[str]] = None
        self.cli_config = self._resolve_cli_config()

    def _resolve_cli_config(self) -> Optional[Path]:
        configured = self.filebrowser_config.get("cli_config")
        if configured:
            return Path(os.path.expandvars(os.path.expanduser(configured))).resolve()

        # 兼容旧 skillconfig.json；新配置应交由 filebrowser-cli config 管理。
        legacy_fields = ("instance_url", "username", "password")
        if all(self.filebrowser_config.get(field) for field in legacy_fields):
            self._temporary_config = tempfile.TemporaryDirectory(prefix="workspace-filebrowser-cli-")
            path = Path(self._temporary_config.name) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "instance_url": self.filebrowser_config["instance_url"],
                        "username": self.filebrowser_config["username"],
                        "password": "${WORKSPACE_FILEBROWSER_PASSWORD}",
                        "default_expires": 24,
                        "default_unit": "hours",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            return path
        return None

    def _environment(self) -> Dict[str, str]:
        environment = os.environ.copy()
        legacy_password = self.filebrowser_config.get("password")
        if legacy_password:
            environment["WORKSPACE_FILEBROWSER_PASSWORD"] = str(legacy_password)
        return environment

    def _run(self, *arguments: str, expect_json: bool = True) -> tuple[bool, Any]:
        if not self.executable:
            self.last_error = "未找到 filebrowser-cli；请先安装并加入 PATH"
            return False, None

        command = [self.executable]
        if self.cli_config:
            command.extend(["--config", str(self.cli_config)])
        if expect_json:
            command.append("--json")
        command.extend(arguments)
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=self._environment(),
            check=False,
        )
        if completed.returncode != 0:
            self.last_error = completed.stderr.strip() or completed.stdout.strip() or f"退出码 {completed.returncode}"
            return False, None
        self.last_error = ""
        if not expect_json:
            return True, completed.stdout.strip()
        try:
            return True, json.loads(completed.stdout) if completed.stdout.strip() else {}
        except json.JSONDecodeError:
            self.last_error = "filebrowser-cli 返回了无效 JSON"
            return False, None

    def login(self) -> bool:
        ok, _ = self._run("login")
        print("[OK] filebrowser-cli 登录成功" if ok else f"[FAIL] filebrowser-cli 登录失败: {self.last_error}")
        return ok

    def check_connection(self) -> bool:
        ok, _ = self._run("whoami")
        return ok

    def file_exists(self, remote_path: str) -> bool:
        ok, _ = self._run("info", remote_path)
        return ok

    def download_file(self, remote_path: str, local_path: str) -> bool:
        destination = Path(local_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        ok, _ = self._run("download", remote_path, str(destination), expect_json=False)
        print(f"[OK] 下载成功: {remote_path} -> {local_path}" if ok else f"[FAIL] 下载失败: {self.last_error}")
        return ok

    def upload_file(self, local_path: str, remote_path: str, override: bool = True) -> bool:
        del override  # filebrowser-cli upload 当前固定覆盖；保留参数兼容现有调用方。
        if not Path(local_path).is_file():
            self.last_error = f"本地文件不存在: {local_path}"
            return False
        ok, _ = self._run("upload", str(Path(local_path)), remote_path, expect_json=False)
        print(f"[OK] 上传成功: {local_path} -> {remote_path}" if ok else f"[FAIL] 上传失败: {self.last_error}")
        return ok

    def list_remote(self, remote_path: str = "/") -> Dict[str, Any]:
        ok, info = self._run("info", remote_path)
        if not ok or not isinstance(info, dict):
            return {}
        if info.get("isDir"):
            listed, listing = self._run("ls", remote_path)
            if listed and isinstance(listing, dict):
                info["items"] = listing.get("items", [])
        return info

    def create_directory(self, remote_path: str) -> bool:
        if self.file_exists(remote_path):
            return True
        ok, _ = self._run("mkdir", remote_path, expect_json=False)
        print(f"[OK] 创建目录: {remote_path}" if ok else f"[FAIL] 创建目录失败: {self.last_error}")
        return ok


def load_config(config_path: str = "skillconfig.json") -> Dict[str, Any]:
    """加载工作区配置。"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    return json.loads(config_file.read_text(encoding="utf-8"))


def get_client(config: Dict[str, Any]) -> FileBrowserCLIClient:
    """从工作区配置创建 filebrowser-cli 适配器。"""
    return FileBrowserCLIClient(config)


def get_remote_root(config: Dict[str, Any]) -> str:
    """通用入口固定同步到 FileBrowser 云端根目录。"""
    del config
    return "/"


def get_remote_path(config: Dict[str, Any], filename: str) -> str:
    """获取云端全局配置文件路径。"""
    return "/" + filename.lstrip("/")
