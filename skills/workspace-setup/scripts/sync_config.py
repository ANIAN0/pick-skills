#!/usr/bin/env python3
"""
配置文件同步脚本
上传/下载/双向同步 CLAUDE.md、AGENTS.md 和 skills 目录
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

from filebrowser_client import load_config, get_client, get_remote_path


CONFIG_FILES = ["CLAUDE.md", "AGENTS.md"]
SKILLS_DIR = "skills"


def collect_local_files(local_dir: str) -> Dict[str, Dict]:
    """收集本地目录下所有文件"""
    files = {}
    local_dir = Path(local_dir)

    if not local_dir.exists():
        return files

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
                    "modified": os.path.getmtime(full_path)
                }
            except Exception:
                pass

    return files


def upload_directory(client, local_dir: str, remote_dir: str) -> Tuple[int, int]:
    """上传整个目录"""
    print(f"  📁 上传目录: {local_dir} -> {remote_dir}")

    local_files = collect_local_files(local_dir)
    success, failed = 0, 0

    for rel_path, info in local_files.items():
        remote_path = remote_dir.rstrip('/') + '/' + rel_path
        print(f"    ⬆️ {rel_path}")
        if client.upload_file(info["path"], remote_path, override=True):
            success += 1
        else:
            failed += 1

    return success, failed


def download_directory(client, remote_dir: str, local_dir: str) -> Tuple[int, int]:
    """下载整个目录（简化版本，递归获取）"""
    print(f"  📁 下载目录: {remote_dir} -> {local_dir}")

    success, failed = 0, 0

    def walk_and_download(remote_path: str, local_base: str):
        info = client.list_remote(remote_path)
        if not info:
            return

        if info.get("isDir") and info.get("items"):
            for item in info["items"]:
                item_path = remote_path.rstrip('/') + '/' + item["name"]
                if item.get("isDir"):
                    if item["name"].startswith('.'):
                        continue
                    walk_and_download(item_path, local_base)
                else:
                    if item["name"].startswith('.'):
                        continue
                    rel_path = item_path[len(remote_dir):] if remote_dir != "/" else item_path[1:]
                    local_path = os.path.join(local_base, rel_path.lstrip('/'))
                    print(f"    ⬇️ {rel_path.lstrip('/')}")
                    if client.download_file(item_path, local_path):
                        success += 1
                    else:
                        failed += 1

    walk_and_download(remote_dir, local_dir)
    return success, failed


def upload_configs(config_path: str, sync_skills: bool = False) -> Dict:
    """上传配置文件到 filebrowser"""
    print("\n📤 开始上传配置文件...\n")

    config = load_config(config_path)
    client = get_client(config)
    project_root = Path(config_path).parent

    results = {
        "uploaded": [],
        "skills_uploaded": 0,
        "skipped": [],
        "errors": []
    }

    if not client.login():
        results["errors"].append("登录失败")
        return results

    # 确保云端目录存在
    ws_config = config.get("workspace", {})
    fb_config = config.get("filebrowser", {})
    base_path = fb_config.get("remote_base_path", "/config")
    config_pack = ws_config.get("config_pack", "")
    remote_dir = f"{base_path.rstrip('/')}/{config_pack}"
    client.create_directory(remote_dir)

    # 上传配置文件
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

    # 上传skills目录
    if sync_skills:
        local_skills = project_root / SKILLS_DIR
        remote_skills = f"{remote_dir}/{SKILLS_DIR}"
        if local_skills.exists():
            success, failed = upload_directory(client, str(local_skills), remote_skills)
            results["skills_uploaded"] = success
            if failed > 0:
                results["errors"].append(f"skills目录上传失败: {failed}个文件")
        else:
            results["skipped"].append("skills (本地不存在)")

    print(f"\n📊 上传完成:")
    print(f"   配置文件: {len(results['uploaded'])}")
    if sync_skills:
        print(f"   skills文件: {results['skills_uploaded']}")
    print(f"   跳过: {len(results['skipped'])}")
    print(f"   失败: {len(results['errors'])}")

    return results


def download_configs(config_path: str, sync_skills: bool = False) -> Dict:
    """从 filebrowser 下载配置文件"""
    print("\n📥 开始下载配置文件...\n")

    config = load_config(config_path)
    client = get_client(config)
    project_root = Path(config_path).parent

    results = {
        "downloaded": [],
        "skills_downloaded": 0,
        "skipped": [],
        "errors": []
    }

    if not client.login():
        results["errors"].append("登录失败")
        return results

    # 下载配置文件
    for filename in CONFIG_FILES:
        local_path = project_root / filename
        remote_path = get_remote_path(config, filename)

        if client.download_file(remote_path, str(local_path)):
            results["downloaded"].append(filename)
        else:
            results["skipped"].append(f"{filename} (云端不存在)")
            print(f"⚠️ 跳过: {filename} - 云端文件不存在")

    # 下载skills目录
    if sync_skills:
        ws_config = config.get("workspace", {})
        fb_config = config.get("filebrowser", {})
        base_path = fb_config.get("remote_base_path", "/config")
        config_pack = ws_config.get("config_pack", "")
        remote_skills = f"{base_path.rstrip('/')}/{config_pack}/{SKILLS_DIR}"
        local_skills = project_root / SKILLS_DIR

        success, failed = download_directory(client, remote_skills, str(local_skills))
        results["skills_downloaded"] = success
        if failed > 0:
            results["errors"].append(f"skills目录下载失败: {failed}个文件")

    print(f"\n📊 下载完成:")
    print(f"   配置文件: {len(results['downloaded'])}")
    if sync_skills:
        print(f"   skills文件: {results['skills_downloaded']}")
    print(f"   跳过: {len(results['skipped'])}")
    print(f"   失败: {len(results['errors'])}")

    return results


def sync_configs(config_path: str, sync_skills: bool = False) -> Dict:
    """双向同步配置文件（基于修改时间）"""
    print("\n🔄 开始双向同步配置文件...\n")

    config = load_config(config_path)
    client = get_client(config)
    project_root = Path(config_path).parent

    results = {
        "uploaded": [],
        "downloaded": [],
        "skills_uploaded": 0,
        "skills_downloaded": 0,
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
            print(f"  ⬆️ {filename} (云端缺失)")
            if client.upload_file(str(local_path), remote_path, override=True):
                results["uploaded"].append(filename)
            else:
                results["errors"].append(f"上传失败: {filename}")

        elif not local_exists and remote_mtime > 0:
            print(f"  ⬇️ {filename} (本地缺失)")
            if client.download_file(remote_path, str(local_path)):
                results["downloaded"].append(filename)
            else:
                results["errors"].append(f"下载失败: {filename}")

        elif local_mtime > remote_mtime:
            print(f"  ⬆️ {filename} (本地较新)")
            if client.upload_file(str(local_path), remote_path, override=True):
                results["uploaded"].append(filename)
            else:
                results["errors"].append(f"上传失败: {filename}")

        elif remote_mtime > local_mtime:
            print(f"  ⬇️ {filename} (云端较新)")
            if client.download_file(remote_path, str(local_path)):
                results["downloaded"].append(filename)
            else:
                results["errors"].append(f"下载失败: {filename}")

        else:
            results["skipped"].append(filename)
            print(f"  ⏭️ {filename} (无需更新)")

    # skills目录同步（简化：上传本地所有文件）
    if sync_skills:
        ws_config = config.get("workspace", {})
        fb_config = config.get("filebrowser", {})
        base_path = fb_config.get("remote_base_path", "/config")
        config_pack = ws_config.get("config_pack", "")
        remote_skills = f"{base_path.rstrip('/')}/{config_pack}/{SKILLS_DIR}"
        local_skills = project_root / SKILLS_DIR

        if local_skills.exists():
            success, failed = upload_directory(client, str(local_skills), remote_skills)
            results["skills_uploaded"] = success
            if failed > 0:
                results["errors"].append(f"skills目录上传失败: {failed}个文件")

    print(f"\n📊 同步完成:")
    print(f"   上传配置: {len(results['uploaded'])}")
    print(f"   下载配置: {len(results['downloaded'])}")
    if sync_skills:
        print(f"   skills上传: {results['skills_uploaded']}")
    print(f"   跳过: {len(results['skipped'])}")
    print(f"   失败: {len(results['errors'])}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="配置文件同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 上传配置文件到 filebrowser
  python sync_config.py upload --config skillconfig.json

  # 上传配置文件和skills目录
  python sync_config.py upload --config skillconfig.json --sync-skills

  # 从 filebrowser 下载配置文件
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

    parser.add_argument(
        "--sync-skills",
        action="store_true",
        help="同时同步 skills 目录"
    )

    args = parser.parse_args()

    if args.command == "upload":
        upload_configs(args.config, args.sync_skills)
    elif args.command == "download":
        download_configs(args.config, args.sync_skills)
    elif args.command == "sync":
        sync_configs(args.config, args.sync_skills)


if __name__ == "__main__":
    main()