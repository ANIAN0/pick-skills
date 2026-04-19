#!/usr/bin/env python3
"""
版本管理脚本
创建新版本目录、归档旧版本、查看版本状态
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List

from filebrowser_client import load_config


# 版本目录结构
VERSION_SUBDIRS = [
    "requirements",
    "references",
    "prototypes",
    "tech-design",
    "plan",
    "tests"
]


def parse_version(version: str) -> tuple:
    """解析版本号 (如 '1.0' -> (1, 0))"""
    parts = version.split('.')
    if len(parts) != 2:
        raise ValueError(f"无效版本号格式: {version}")
    return int(parts[0]), int(parts[1])


def format_version(major: int, minor: int) -> str:
    """格式化版本号"""
    return f"{major}.{minor}"


def increment_version(version: str) -> str:
    """递增版本号（minor + 1）"""
    major, minor = parse_version(version)
    return format_version(major, minor + 1)


def get_version_status(config_path: str) -> Dict:
    """获取版本状态"""
    config = load_config(config_path)
    ws_config = config.get("workspace", {})
    project_root = Path(config_path).parent

    workplace_dir = ws_config.get("workplace_dir", "workplace")
    current_version = ws_config.get("current_version", "1.0")
    workplace_path = project_root / workplace_dir

    status = {
        "current_version": current_version,
        "versions": [],
        "archived": [],
        "archive_path": str(workplace_path / "archive")
    }

    # 扫描版本目录
    if workplace_path.exists():
        for item in workplace_path.iterdir():
            if item.is_dir() and item.name != "archive":
                try:
                    parse_version(item.name)
                    status["versions"].append(item.name)
                except ValueError:
                    pass

        # 扫描归档目录
        archive_path = workplace_path / "archive"
        if archive_path.exists():
            for item in archive_path.iterdir():
                if item.is_dir():
                    try:
                        parse_version(item.name)
                        status["archived"].append(item.name)
                    except ValueError:
                        pass

    # 排序版本列表
    status["versions"].sort(key=lambda v: parse_version(v))
    status["archived"].sort(key=lambda v: parse_version(v))

    return status


def create_version(config_path: str, target_version: str = None) -> Dict:
    """创建新版本目录"""
    print("\n🆕 开始创建新版本...\n")

    config = load_config(config_path)
    ws_config = config.get("workspace", {})
    project_root = Path(config_path).parent

    workplace_dir = ws_config.get("workplace_dir", "workplace")
    current_version = ws_config.get("current_version", "1.0")
    workplace_path = project_root / workplace_dir

    # 计算新版本号
    if target_version:
        new_version = target_version
    else:
        new_version = increment_version(current_version)

    results = {
        "new_version": new_version,
        "directories_created": [],
        "errors": []
    }

    # 检查版本是否已存在
    new_version_path = workplace_path / new_version
    if new_version_path.exists():
        results["errors"].append(f"版本 {new_version} 已存在")
        print(f"❌ 版本 {new_version} 已存在，请先归档或使用其他版本号")
        return results

    # 创建版本目录
    new_version_path.mkdir(parents=True, exist_ok=True)
    results["directories_created"].append(str(new_version_path))
    print(f"✅ 创建版本目录: {new_version}")

    # 创建子目录
    for subdir in VERSION_SUBDIRS:
        subdir_path = new_version_path / subdir
        subdir_path.mkdir(exist_ok=True)
        results["directories_created"].append(str(subdir_path))
        print(f"  ├── {subdir}/")

    # 更新配置中的当前版本
    update_config_version(config_path, new_version)

    print(f"\n📊 创建完成:")
    print(f"   新版本: {new_version}")
    print(f"   目录数: {len(results['directories_created'])}")

    return results


def archive_version(config_path: str, target_version: str = None) -> Dict:
    """归档版本目录"""
    print("\n📦 开始归档版本...\n")

    config = load_config(config_path)
    ws_config = config.get("workspace", {})
    project_root = Path(config_path).parent

    workplace_dir = ws_config.get("workplace_dir", "workplace")
    current_version = ws_config.get("current_version", "1.0")
    workplace_path = project_root / workplace_dir
    archive_path = workplace_path / "archive"

    # 确定要归档的版本
    if target_version:
        archive_version_num = target_version
    else:
        # 归档当前版本之前的版本（不包括当前版本）
        status = get_version_status(config_path)
        versions = status["versions"]
        if current_version in versions:
            # 归档当前版本之前所有版本
            archive_version_num = current_version
        else:
            results["errors"].append("无法确定要归档的版本")
            return {"errors": ["无法确定要归档的版本"]}

    results = {
        "archived_version": archive_version_num,
        "moved_path": None,
        "errors": []
    }

    # 检查源版本目录
    source_path = workplace_path / archive_version_num
    if not source_path.exists():
        results["errors"].append(f"版本 {archive_version_num} 目录不存在")
        print(f"❌ 版本 {archive_version_num} 目录不存在")
        return results

    # 确保归档目录存在
    archive_path.mkdir(exist_ok=True)

    # 目标路径
    target_path = archive_path / archive_version_num

    # 检查目标是否已存在
    if target_path.exists():
        results["errors"].append(f"归档目录 {archive_version_num} 已存在")
        print(f"❌ 归档目录 {archive_version_num} 已存在")
        return results

    # 移动目录
    try:
        shutil.move(str(source_path), str(target_path))
        results["moved_path"] = str(target_path)
        print(f"✅ 归档成功: {archive_version_num} -> archive/{archive_version_num}")
    except Exception as e:
        results["errors"].append(f"移动失败: {e}")
        print(f"❌ 归档失败: {e}")
        return results

    print(f"\n📊 归档完成:")
    print(f"   归档版本: {archive_version_num}")

    return results


def update_config_version(config_path: str, version: str):
    """更新配置文件中的版本号"""
    config = load_config(config_path)
    config["workspace"]["current_version"] = version

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def print_status(config_path: str):
    """打印版本状态"""
    status = get_version_status(config_path)

    print("\n📋 版本状态:\n")
    print(f"当前版本: {status['current_version']}")
    print(f"\n活跃版本:")
    for v in status['versions']:
        marker = " *" if v == status['current_version'] else ""
        print(f"  {v}{marker}")

    if status['archived']:
        print(f"\n已归档:")
        for v in status['archived']:
            print(f"  {v} (archived)")

    print(f"\n归档路径: {status['archive_path']}")


def main():
    parser = argparse.ArgumentParser(
        description="版本管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 创建新版本（自动递增，如 1.0 -> 1.1）
  python version_manager.py create --config skillconfig.json

  # 创建指定版本
  python version_manager.py create --config skillconfig.json --version 2.0

  # 归档当前版本
  python version_manager.py archive --config skillconfig.json

  # 归档指定版本
  python version_manager.py archive --config skillconfig.json --version 1.0

  # 查看版本状态
  python version_manager.py status --config skillconfig.json
        """
    )

    parser.add_argument(
        "command",
        choices=["create", "archive", "status"],
        help="执行命令: create(创建新版本), archive(归档版本), status(查看状态)"
    )

    parser.add_argument(
        "--config",
        default="skillconfig.json",
        help="配置文件路径"
    )

    parser.add_argument(
        "--version",
        help="指定版本号（可选，默认自动计算）"
    )

    args = parser.parse_args()

    if args.command == "create":
        create_version(args.config, args.version)
    elif args.command == "archive":
        archive_version(args.config, args.version)
    elif args.command == "status":
        print_status(args.config)


if __name__ == "__main__":
    main()