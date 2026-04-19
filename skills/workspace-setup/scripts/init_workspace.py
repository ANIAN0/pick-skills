#!/usr/bin/env python3
"""
初始化工作区脚本
下载CLAUDE.md、AGENTS.md，创建workplace目录和版本结构
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List

from filebrowser_client import load_config, get_client, get_remote_path


# 版本目录结构
VERSION_SUBDIRS = [
    "requirements",   # 需求文档
    "references",     # 参考文档
    "prototypes",     # 原型设计
    "tech-design",    # 技术方案
    "plan",           # 实施计划
    "tests"           # 测试文件
]

# 配置文件列表
CONFIG_FILES = ["CLAUDE.md", "AGENTS.md"]


def init_workspace(config_path: str, download_configs: bool = True) -> Dict:
    """初始化工作区"""
    print("\n🚀 开始初始化工作区...\n")

    # 加载配置
    config = load_config(config_path)
    ws_config = config.get("workspace", {})
    project_root = Path(config_path).parent

    # 获取配置
    workplace_dir = ws_config.get("workplace_dir", "workplace")
    current_version = ws_config.get("current_version", "1.0")
    config_pack = ws_config.get("config_pack", "")

    results = {
        "directories_created": [],
        "configs_downloaded": [],
        "configs_created": [],
        "errors": []
    }

    # 1. 创建workplace目录
    workplace_path = project_root / workplace_dir
    workplace_path.mkdir(exist_ok=True)
    results["directories_created"].append(str(workplace_path))
    print(f"✅ 创建工作目录: {workplace_path}")

    # 2. 创建archive目录
    archive_path = workplace_path / "archive"
    archive_path.mkdir(exist_ok=True)
    results["directories_created"].append(str(archive_path))
    print(f"✅ 创建归档目录: {archive_path}")

    # 3. 创建当前版本目录
    version_path = workplace_path / current_version
    version_path.mkdir(exist_ok=True)
    results["directories_created"].append(str(version_path))
    print(f"✅ 创建版本目录: {version_path}")

    # 4. 创建版本子目录
    for subdir in VERSION_SUBDIRS:
        subdir_path = version_path / subdir
        subdir_path.mkdir(exist_ok=True)
        results["directories_created"].append(str(subdir_path))
        print(f"  ├── {subdir}/")

    # 5. 处理配置文件
    if download_configs and config_pack:
        print(f"\n📥 从 filebrowser 下载配置文件...")
        client = get_client(config)
        if client.login():
            for filename in CONFIG_FILES:
                local_path = project_root / filename
                remote_path = get_remote_path(config, filename)

                if client.download_file(remote_path, str(local_path)):
                    results["configs_downloaded"].append(filename)
                else:
                    # 文件不存在，创建空模板
                    create_config_template(local_path, filename)
                    results["configs_created"].append(filename)
        else:
            results["errors"].append("filebrowser登录失败")
            # 创建默认配置文件
            for filename in CONFIG_FILES:
                local_path = project_root / filename
                create_config_template(local_path, filename)
                results["configs_created"].append(filename)
    else:
        # 不下载时创建默认配置文件
        print(f"\n📝 创建默认配置文件...")
        for filename in CONFIG_FILES:
            local_path = project_root / filename
            if not local_path.exists():
                create_config_template(local_path, filename)
                results["configs_created"].append(filename)

    # 6. 更新配置中的当前版本
    update_config_version(config_path, current_version)

    # 输出结果
    print(f"\n📊 初始化完成:")
    print(f"   目录创建: {len(results['directories_created'])}")
    print(f"   配置下载: {len(results['configs_downloaded'])}")
    print(f"   配置创建: {len(results['configs_created'])}")

    if results["errors"]:
        print(f"   错误: {len(results['errors'])}")
        for err in results["errors"]:
            print(f"   ❌ {err}")

    return results


def create_config_template(filepath: Path, filename: str):
    """创建配置文件模板"""
    templates = {
        "CLAUDE.md": "# Claude 配置\n\n本项目使用 Claude Code 进行开发。\n\n## 项目说明\n\n请在此添加项目说明。\n",
        "AGENTS.md": "# Agents 配置\n\n本项目使用 Agents 工具进行开发。\n\n## 技能配置\n\n请在此添加技能配置。\n"
    }

    content = templates.get(filename, f"# {filename}\n\n")
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ 创建模板: {filename}")


def update_config_version(config_path: str, version: str):
    """更新配置文件中的版本号"""
    config = load_config(config_path)
    config["workspace"]["current_version"] = version

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="初始化工作区")

    parser.add_argument(
        "--config",
        default="skillconfig.json",
        help="配置文件路径"
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="跳过从filebrowser下载配置文件"
    )

    args = parser.parse_args()

    init_workspace(
        config_path=args.config,
        download_configs=not args.skip_download
    )


if __name__ == "__main__":
    main()