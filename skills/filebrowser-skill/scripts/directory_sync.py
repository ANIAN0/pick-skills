#!/usr/bin/env python3
"""
目录同步工具
支持：上传目录到云端、从云端下载目录、双向同步
"""

import os
import hashlib
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple


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

    def list_remote(self, remote_path: str = "/") -> Dict:
        """获取远程目录内容"""
        url = f"{self.base_url}/api/resources{remote_path}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"❌ 获取目录异常: {e}")
            return {}

    def upload_file(self, local_path: str, remote_path: str, override: bool = False) -> bool:
        """上传文件到云端"""
        url = f"{self.base_url}/api/resources{remote_path}"
        params = {"override": str(override).lower()}

        try:
            with open(local_path, 'rb') as f:
                response = self.session.post(url, data=f, params=params)
                if response.status_code == 200:
                    return True
                return False
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
                return True
            return False
        except Exception:
            return False


class DirectorySyncer:
    """目录同步器"""

    def __init__(self, client: FileBrowserClient):
        self.client = client

    def calculate_md5(self, file_path: str) -> str:
        """计算文件 MD5"""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def collect_local_files(self, local_dir: str) -> Dict[str, Dict]:
        """收集本地目录下所有文件"""
        files = {}
        local_dir = Path(local_dir)

        for root, dirs, filenames in os.walk(local_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for filename in filenames:
                if filename.startswith('.'):
                    continue

                full_path = os.path.join(root, filename)
                rel_path = str(Path(root).relative_to(local_dir) / filename)

                try:
                    files[rel_path] = {
                        "path": full_path,
                        "size": os.path.getsize(full_path),
                        "modified": os.path.getmtime(full_path),
                        "md5": self.calculate_md5(full_path)
                    }
                except Exception as e:
                    print(f"⚠️ 无法读取文件: {full_path} - {e}")

        return files

    def collect_remote_files(self, remote_dir: str = "/") -> Dict[str, Dict]:
        """收集远程目录下所有文件"""
        files = {}

        def walk_remote(path: str):
            info = self.client.list_remote(path)
            if not info:
                return

            if info.get("isDir") and info.get("items"):
                for item in info["items"]:
                    item_path = path.rstrip('/') + '/' + item["name"]
                    if item.get("isDir"):
                        if item["name"].startswith('.'):
                            continue
                        walk_remote(item_path)
                    else:
                        if item["name"].startswith('.'):
                            continue
                        rel_path = item_path[len(remote_dir):] if remote_dir != "/" else item_path[1:]
                        files[rel_path] = {
                            "path": item_path,
                            "size": item.get("size", 0),
                            "modified": item.get("modified", 0),
                            "md5": item.get("checksums", {}).get("md5", "")
                        }

        walk_remote(remote_dir)
        return files

    def upload_all(self, local_dir: str, remote_dir: str = "/", override: bool = False) -> Tuple[int, int]:
        """上传本地目录所有文件到云端"""
        print(f"\n📤 开始上传目录: {local_dir} -> {remote_dir}")

        local_files = self.collect_local_files(local_dir)
        success, failed = 0, 0

        for rel_path, info in local_files.items():
            remote_path = remote_dir.rstrip('/') + '/' + rel_path
            print(f"  ⬆️ {rel_path}")
            if self.client.upload_file(info["path"], remote_path, override):
                success += 1
            else:
                failed += 1

        print(f"\n📊 上传完成: 成功 {success}, 失败 {failed}")
        return success, failed

    def download_all(self, remote_dir: str = "/", local_dir: str) -> Tuple[int, int]:
        """下载云端目录所有文件到本地"""
        print(f"\n📥 开始下载目录: {remote_dir} -> {local_dir}")

        remote_files = self.collect_remote_files(remote_dir)
        success, failed = 0, 0

        for rel_path, info in remote_files.items():
            local_path = os.path.join(local_dir, rel_path)
            print(f"  ⬇️ {rel_path}")
            if self.client.download_file(info["path"], local_path):
                success += 1
            else:
                failed += 1

        print(f"\n📊 下载完成: 成功 {success}, 失败 {failed}")
        return success, failed

    def sync_upload(self, local_dir: str, remote_dir: str = "/") -> Tuple[int, int, int]:
        """智能上传：只上传新增或修改的文件"""
        print(f"\n🔄 智能上传同步: {local_dir} -> {remote_dir}")

        local_files = self.collect_local_files(local_dir)
        remote_files = self.collect_remote_files(remote_dir)

        uploaded, skipped, failed = 0, 0, 0

        for rel_path, local_info in local_files.items():
            remote_path = remote_dir.rstrip('/') + '/' + rel_path
            remote_info = remote_files.get(rel_path)

            need_upload = False
            reason = ""

            if not remote_info:
                need_upload = True
                reason = "新增"
            elif local_info["md5"] != remote_info["md5"]:
                need_upload = True
                reason = "已修改"
            elif local_info["modified"] > remote_info["modified"]:
                need_upload = True
                reason = "本地较新"

            if need_upload:
                print(f"  ⬆️ {rel_path} ({reason})")
                if self.client.upload_file(local_info["path"], remote_path, override=True):
                    uploaded += 1
                else:
                    failed += 1
            else:
                skipped += 1

        print(f"\n📊 同步完成: 上传 {uploaded}, 跳过 {skipped}, 失败 {failed}")
        return uploaded, skipped, failed

    def sync_download(self, remote_dir: str = "/", local_dir: str) -> Tuple[int, int, int]:
        """智能下载：只下载新增或修改的文件"""
        print(f"\n🔄 智能下载同步: {remote_dir} -> {local_dir}")

        local_files = self.collect_local_files(local_dir)
        remote_files = self.collect_remote_files(remote_dir)

        downloaded, skipped, failed = 0, 0, 0

        for rel_path, remote_info in remote_files.items():
            local_path = os.path.join(local_dir, rel_path)
            local_info = local_files.get(rel_path)

            need_download = False
            reason = ""

            if not local_info:
                need_download = True
                reason = "新增"
            elif local_info["md5"] != remote_info["md5"]:
                need_download = True
                reason = "已修改"
            elif remote_info["modified"] > local_info["modified"]:
                need_download = True
                reason = "云端较新"

            if need_download:
                print(f"  ⬇️ {rel_path} ({reason})")
                if self.client.download_file(remote_info["path"], local_path):
                    downloaded += 1
                else:
                    failed += 1
            else:
                skipped += 1

        print(f"\n📊 同步完成: 下载 {downloaded}, 跳过 {skipped}, 失败 {failed}")
        return downloaded, skipped, failed

    def sync_bidirectional(self, local_dir: str, remote_dir: str = "/") -> Dict:
        """双向同步：云端和本地互相同步"""
        print(f"\n🔄 双向同步: {local_dir} <-> {remote_dir}")

        local_files = self.collect_local_files(local_dir)
        remote_files = self.collect_remote_files(remote_dir)

        stats = {
            "uploaded": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0
        }

        # 处理本地文件
        for rel_path, local_info in local_files.items():
            remote_path = remote_dir.rstrip('/') + '/' + rel_path
            remote_info = remote_files.get(rel_path)

            if not remote_info:
                print(f"  ⬆️ {rel_path} (云端缺失)")
                if self.client.upload_file(local_info["path"], remote_path):
                    stats["uploaded"] += 1
                else:
                    stats["failed"] += 1
            elif local_info["md5"] != remote_info["md5"]:
                if local_info["modified"] >= remote_info["modified"]:
                    print(f"  ⬆️ {rel_path} (本地较新)")
                    if self.client.upload_file(local_info["path"], remote_path, override=True):
                        stats["uploaded"] += 1
                    else:
                        stats["failed"] += 1
                else:
                    print(f"  ⬇️ {rel_path} (云端较新)")
                    local_path = os.path.join(local_dir, rel_path)
                    if self.client.download_file(remote_info["path"], local_path):
                        stats["downloaded"] += 1
                    else:
                        stats["failed"] += 1
            else:
                stats["skipped"] += 1

        # 处理只在远程存在的文件
        for rel_path, remote_info in remote_files.items():
            if rel_path not in local_files:
                print(f"  ⬇️ {rel_path} (本地缺失)")
                local_path = os.path.join(local_dir, rel_path)
                if self.client.download_file(remote_info["path"], local_path):
                    stats["downloaded"] += 1
                else:
                    stats["failed"] += 1

        print(f"\n📊 双向同步完成:")
        print(f"   上传: {stats['uploaded']}, 下载: {stats['downloaded']}")
        print(f"   跳过: {stats['skipped']}, 失败: {stats['failed']}")
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="目录同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 上传整个目录到云端
  python directory_sync.py upload --url http://localhost:8080 --user admin --password pwd --local ./data --remote /backup

  # 从云端下载整个目录
  python directory_sync.py download --url http://localhost:8080 --user admin --password pwd --remote /backup --local ./data

  # 智能上传（只上传变化的文件）
  python directory_sync.py sync-up --url http://localhost:8080 --user admin --password pwd --local ./data --remote /backup

  # 智能下载（只下载变化的文件）
  python directory_sync.py sync-down --url http://localhost:8080 --user admin --password pwd --remote /backup --local ./data

  # 双向同步
  python directory_sync.py sync --url http://localhost:8080 --user admin --password pwd --local ./data --remote /backup
        """
    )

    parser.add_argument("command", choices=[
        "upload", "download", "sync-up", "sync-down", "sync"
    ], help="执行命令")

    parser.add_argument("--url", required=True, help="FileBrowser 服务地址")
    parser.add_argument("--user", required=True, help="用户名")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--local", required=True, help="本地目录路径")
    parser.add_argument("--remote", default="/", help="远程目录路径")
    parser.add_argument("--override", action="store_true", help="强制覆盖已存在的文件")

    args = parser.parse_args()

    # 创建客户端并登录
    client = FileBrowserClient(args.url, args.user, args.password)
    if not client.login():
        return

    syncer = DirectorySyncer(client)

    # 执行命令
    if args.command == "upload":
        syncer.upload_all(args.local, args.remote, args.override)

    elif args.command == "download":
        syncer.download_all(args.remote, args.local)

    elif args.command == "sync-up":
        syncer.sync_upload(args.local, args.remote)

    elif args.command == "sync-down":
        syncer.sync_download(args.remote, args.local)

    elif args.command == "sync":
        syncer.sync_bidirectional(args.local, args.remote)


if __name__ == "__main__":
    main()