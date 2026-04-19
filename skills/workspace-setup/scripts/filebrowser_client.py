#!/usr/bin/env python3
"""
FileBrowser API 客户端
提供登录认证、文件上传下载、目录操作等基础功能
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List


class FileBrowserClient:
    """FileBrowser API 客户端"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.session = requests.Session()

    def login(self) -> bool:
        """登录获取 JWT Token"""
        url = f"{self.base_url}/api/login"
        data = {
            "username": self.username,
            "password": self.password
        }
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                self.token = response.text.strip()
                self.session.headers.update({"X-Auth": self.token})
                print(f"✅ 登录成功: {self.username}")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False

    def check_connection(self) -> bool:
        """检查连接状态"""
        if not self.token:
            return self.login()
        return True

    def file_exists(self, remote_path: str) -> bool:
        """检查远程文件是否存在"""
        url = f"{self.base_url}/api/resources{remote_path}"
        try:
            response = self.session.get(url)
            return response.status_code == 200
        except Exception:
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """从云端下载文件"""
        url = f"{self.base_url}/api/raw{remote_path}"
        try:
            response = self.session.get(url, stream=True)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ 下载成功: {remote_path} -> {local_path}")
                return True
            elif response.status_code == 404:
                print(f"⚠️ 远程文件不存在: {remote_path}")
                return False
            else:
                print(f"❌ 下载失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 下载异常: {e}")
            return False

    def upload_file(self, local_path: str, remote_path: str, override: bool = True) -> bool:
        """上传文件到云端"""
        url = f"{self.base_url}/api/resources{remote_path}"
        params = {"override": str(override).lower()}
        try:
            with open(local_path, 'rb') as f:
                response = self.session.post(url, data=f, params=params)
                if response.status_code == 200:
                    print(f"✅ 上传成功: {local_path} -> {remote_path}")
                    return True
                else:
                    print(f"❌ 上传失败: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"❌ 上传异常: {e}")
            return False

    def list_remote(self, remote_path: str = "/") -> Dict:
        """获取远程目录内容"""
        url = f"{self.base_url}/api/resources{remote_path}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def create_directory(self, remote_path: str) -> bool:
        """创建远程目录"""
        url = f"{self.base_url}/api/resources{remote_path.rstrip('/')}/"
        try:
            response = self.session.post(url)
            if response.status_code in [200, 201]:
                print(f"✅ 创建目录: {remote_path}")
                return True
            return False
        except Exception:
            return False


def load_config(config_path: str = "skillconfig.json") -> Dict:
    """加载配置文件"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_client(config: Dict) -> FileBrowserClient:
    """从配置创建客户端"""
    fb_config = config.get("filebrowser", {})
    client = FileBrowserClient(
        base_url=fb_config.get("instance_url", ""),
        username=fb_config.get("username", ""),
        password=fb_config.get("password", "")
    )
    return client


def get_remote_path(config: Dict, filename: str) -> str:
    """获取远程路径"""
    fb_config = config.get("filebrowser", {})
    ws_config = config.get("workspace", {})
    base_path = fb_config.get("remote_base_path", "/skills")
    skill_name = ws_config.get("skill_name", "default")
    return f"{base_path.rstrip('/')}/{skill_name}/{filename}"