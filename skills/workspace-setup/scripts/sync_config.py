#!/usr/bin/env python3
"""
配置文件同步脚本
上传/下载/双向同步 CLAUDE.md 和 AGENTS.md
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List

from filebrowser_client import load_config, get_client, get_remote_path


CONFIG_FILES = ["CLAUDE.md", "AGENTS.md"]


def upload_configs(config_path: str) -> Dict:
    """上传配置文件到 filebrowser"""
    print("\n📤 开始上传配置文件...\n")

    config = load_config(config_path)
    client = get_client(config)
    project_root = Path(config_path).parent

    results = {
        "uploaded": [],
        "skipped": [],
        "errors": []
    }

    if not client.login():
        results["errors"].append("登录失败")
        return results

    # 确保远程目录存在
    ws_config = config.get("workspace", {})
    fb_config = config.get("filebrowser", {})
    base_path = fb_config.get("remote_base_path", "/skills")
    skill_name = ws_config.get("skill_name", "")
    remote_dir = f"{base_path.rstrip('/')}/{skill_name}"
    client.create_directory(remote_dir)

    for filename in CONFIG_FILES:
        local_path = project_root / filename
        remote_path = get_remote_path(config, filename)

        if local_path.exists():
            if client.upload_file(str(local_path), remote_path, override=True):
                results["uploaded"].append(filename)
            else:
                results["errors"].append(f"上传失败: {filename}")
        else:
            results["skipped"].append(f"{filename} (本地不存在)")
            print(f"⚠️ 跳过: {filename} - 本地文件不存在")

    print(f"\n📊 上传完成:")
    print(f"   成功: {len(results['uploaded'])}")
    print(f"   跳过: {len(results['skipped'])}")
    print(f"   失败: {len(results['errors'])}")

    return results


def download_configs(config_path: str) -> Dict:
    """从 filebrowser 下载配置文件"""
    print("\n📥 开始下载配置文件...\n")

    config = load_config(config_path)
    client = get_client(config)
    project_root = Path(config_path).parent

    results = {
        "downloaded": [],
        "skipped": [],
        "errors": []
    }

    if not client.login():
        results["errors"].append("登录失败")
        return results

    for filename in CONFIG_FILES:
        local_path = project_root / filename
        remote_path = get_remote_path(config, filename)

        if client.download_file(remote_path, str(local_path)):
            results["downloaded"].append(filename)
        else:
            results["skipped"].append(f"{filename} (远程不存在)")
            print(f"⚠️ 跳过: {filename} - 远程文件不存在")

    print(f"\n📊 下载完成:")
    print(f"   成功: {len(results['downloaded'])}")
    print(f"   跳过: {len(results['skipped'])}")
    print(f"   失败: {len(results['errors'])}")

    return results


def sync_configs(config_path: str) -> Dict:
    """双向同步配置文件（基于修改时间）"""
    print("\n🔄 开始双向同步配置文件...\n")

    config = load_config(config)
    client = get_client(config)
    project_root = Path(config_path).parent

    results = {
        "uploaded": [],
        "downloaded": [],
        "skipped": [],
        "errors": []
    }

    if not client.login():
        results["errors"].append("登录失败")
        return results

    for filename in CONFIG_FILES:
        local_path = project_root / filename
        remote_path = get_remote_path(config, filename)

        # 获取本地修改时间
        local_exists = local_path.exists()
        local_mtime = local_path.stat().st_mtime if local_exists else 0

        # 获取远程信息
        remote_info = client.list_remote(remote_path)
        remote_mtime = 0

        if remote_info and not remote_info.get("isDir", True):
            # 解析远程修改时间
            modified_str = remote_info.get("modified", "")
            if modified_str:
                try:
                    from datetime import datetime
                    remote_mtime = datetime.fromisoformat(
                        modified_str.replace('Z', '+00:00')
                    ).timestamp()
                except Exception:
                    remote_mtime = 0

        # 决定同步方向
        if local_exists and remote_mtime == 0:
            # 只有本地存在，上传
            print(f"  ⬆️ {filename} (远程缺失)")
            if client.upload_file(str(local_path), remote_path, override=True):
                results["uploaded"].append(filename)
            else:
                results["errors"].append(f"上传失败: {filename}")

        elif not local_exists and remote_mtime > 0:
            # 只有远程存在，下载
            print(f"  ⬇️ {filename} (本地缺失)")
            if client.download_file(remote_path, str(local_path)):
                results["downloaded"].append(filename)
            else:
                results["errors"].append(f"下载失败: {filename}")

        elif local_mtime > remote_mtime:
            # 本地较新，上传
            print(f"  ⬆️ {filename} (本地较新)")
            if client.upload_file(str(local_path), remote_path, override=True):
                results["uploaded"].append(filename)
            else:
                results["errors"].append(f"上传失败: {filename}")

        elif remote_mtime > local_mtime:
            # 远程较新，下载
            print(f"  ⬇️ {filename} (远程较新)")
            if client.download_file(remote_path, str(local_path)):
                results["downloaded"].append(filename)
            else:
                results["errors"].append(f"下载失败: {filename}")

        else:
            # 相同时间，跳过
            results["skipped"].append(filename)
            print(f"  ⏭️ {filename} (无需更新)")

    print(f"\n📊 同步完成:")
    print(f"   上传: {len(results['uploaded'])}")
    print(f"   下载: {len(results['downloaded'])}")
    print(f"   跳过: {len(results['skipped'])}")
    print(f"   失败: {len(results['errors'])}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="配置文件同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 上传本地变更到 filebrowser
  python sync_config.py upload --config skillconfig.json

  # 从 filebrowser 下载最新配置
  python sync_config.py download --config skillconfig.json

  # 双向同步（检查变更）
  python sync_config.py sync --config skillconfig.json
        """
    )

    parser.add_argument(
        "command",
        choices=["upload", "download", "sync"],
        help="执行命令: upload(上传), download(下载), sync(双向同步)"
    )

    parser.add_argument(
        "--config",
        default="skillconfig.json",
        help="配置文件路径"
    )

    args = parser.parse_args()

    if args.command == "upload":
        upload_configs(args.config)
    elif args.command == "download":
        download_configs(args.config)
    elif args.command == "sync":
        sync_configs(args.config)


if __name__ == "__main__":
    main()