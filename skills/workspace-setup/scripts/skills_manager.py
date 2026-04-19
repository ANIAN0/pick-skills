#!/usr/bin/env python3
"""
技能管理脚本
封装 npx skills 命令，提供技能搜索、安装、更新等功能
"""

import subprocess
import argparse
from typing import Dict, List


def run_skills_command(args: List[str]) -> Dict:
    """运行 npx skills 命令"""
    cmd = ["npx", "skills"] + args
    print(f"\n🔧 执行命令: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout + result.stderr
        print(output)

        return {
            "success": result.returncode == 0,
            "output": output,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        print("❌ 命令超时")
        return {
            "success": False,
            "output": "命令超时",
            "returncode": -1
        }
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return {
            "success": False,
            "output": str(e),
            "returncode": -1
        }


def find_skills(query: str = "") -> Dict:
    """搜索技能"""
    print(f"\n🔍 搜索技能: {query if query else '(交互式)'}")
    args = ["find"]
    if query:
        args.extend(query.split())
    return run_skills_command(args)


def add_skill(package: str, global_install: bool = True, skip_confirm: bool = True) -> Dict:
    """安装技能"""
    print(f"\n📥 安装技能: {package}")
    args = ["add", package]
    if global_install:
        args.append("-g")
    if skip_confirm:
        args.append("-y")
    return run_skills_command(args)


def check_updates() -> Dict:
    """检查技能更新"""
    print("\n🔔 检查技能更新...")
    return run_skills_command(["check"])


def update_skills() -> Dict:
    """更新所有技能"""
    print("\n⬆️ 更新所有技能...")
    return run_skills_command(["update"])


def list_installed() -> Dict:
    """列出已安装技能"""
    print("\n📋 已安装技能...")
    return run_skills_command(["list"])


def main():
    parser = argparse.ArgumentParser(
        description="技能管理工具（封装 npx skills）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 搜索技能（交互式）
  python skills_manager.py find

  # 搜索指定技能
  python skills_manager.py find "react testing"

  # 安装技能（全局安装，跳过确认）
  python skills_manager.py add "vercel-labs/agent-skills@react-best-practices"

  # 安装技能（本地安装）
  python skills_manager.py add "vercel-labs/agent-skills@react-best-practices" --no-global

  # 检查更新
  python skills_manager.py check

  # 更新所有技能
  python skills_manager.py update

  # 列出已安装技能
  python skills_manager.py list
        """
    )

    parser.add_argument(
        "command",
        choices=["find", "add", "check", "update", "list"],
        help="执行命令"
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="命令参数（如搜索关键词或技能包名）"
    )

    parser.add_argument(
        "--no-global",
        action="store_true",
        help="本地安装（不使用 -g 标志）"
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="需要确认（不使用 -y 标志）"
    )

    args = parser.parse_args()

    if args.command == "find":
        query = " ".join(args.args) if args.args else ""
        find_skills(query)

    elif args.command == "add":
        if not args.args:
            print("❌ 请指定要安装的技能包名")
            return
        package = args.args[0]
        add_skill(
            package,
            global_install=not args.no_global,
            skip_confirm=not args.confirm
        )

    elif args.command == "check":
        check_updates()

    elif args.command == "update":
        update_skills()

    elif args.command == "list":
        list_installed()


if __name__ == "__main__":
    main()