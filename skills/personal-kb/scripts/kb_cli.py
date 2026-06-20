#!/usr/bin/env python3
"""personal-kb 的确定性初始化与边界检查 CLI。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


DEFAULT_GLOBAL_ROOT = "~/personal-kb"


def _resolve(path: str, base: Path | None = None) -> Path:
    expanded = Path(os.path.expandvars(os.path.expanduser(path)))
    if not expanded.is_absolute() and base is not None:
        expanded = base / expanded
    return expanded.resolve()


def check_global(root: str = DEFAULT_GLOBAL_ROOT, *, explicit: bool = False) -> dict[str, Any]:
    resolved = _resolve(root)
    error = None
    if not resolved.exists():
        error = f"全局知识库目录不存在: {resolved}" if explicit else None
    elif not resolved.is_dir():
        error = f"全局知识库路径不是目录: {resolved}"
    elif not os.access(resolved, os.R_OK | os.W_OK):
        error = f"全局知识库目录不可读写: {resolved}"
    return {
        "mode": "global",
        "root": str(resolved),
        "available": resolved.is_dir() and os.access(resolved, os.R_OK | os.W_OK),
        "explicit": explicit,
        "error": error,
    }


def init_project(
    project_root: Path,
    *,
    project_kb_dir: str = "project-kb",
    project_rules_file: str = "PROJECT_RULES.md",
) -> dict[str, Any]:
    root = project_root.resolve()
    rules = root / project_rules_file
    if not rules.is_file():
        return {
            "mode": "project",
            "root": str(root / project_kb_dir),
            "created": [],
            "error": f"项目规则文件不存在: {rules}",
        }

    kb_root = root / project_kb_dir
    code_root = kb_root / "code"
    kb_root.mkdir(parents=True, exist_ok=True)
    code_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    files = {
        kb_root / "README.md": (
            "# 项目知识库\n\n"
            f"- 项目规则：[[../{project_rules_file}]]\n"
            "- 代码说明入口：[[code/README]]\n\n"
            "本知识库由 `personal-kb` 维护，按源码相对路径镜像代码说明。\n"
        ),
        code_root / "README.md": (
            "# 代码文件说明\n\n"
            "每个源码文件对应 `project-kb/code/<源码相对路径>.md`。\n\n"
            "单文件条目必须记录功能点、相关文件、重要逻辑、测试文件、修改注意事项和最近更新。\n"
        ),
        kb_root / "changelog.md": (
            "# 知识库变更记录\n\n"
            "由 `personal-kb` 在批量创建或更新条目时追加记录。\n"
        ),
    }
    for path, content in files.items():
        if not path.exists():
            path.write_text(content, encoding="utf-8", newline="\n")
            created.append(str(path))

    rules_text = rules.read_text(encoding="utf-8")
    expected_links = (f"[[{project_kb_dir}/README]]", f"[[{project_kb_dir}/code/README]]")
    missing_links = [link for link in expected_links if link not in rules_text]
    return {
        "mode": "project",
        "root": str(kb_root),
        "created": created,
        "missing_rule_links": missing_links,
        "warnings": [] if not missing_links else ["PROJECT_RULES.md 缺少项目知识库入口链接"],
        "error": None,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="初始化或检查 personal-kb 存储边界。")
    subparsers = parser.add_subparsers(dest="command", required=True)
    project = subparsers.add_parser("init-project", help="初始化项目内 project-kb")
    project.add_argument("--project-root", type=Path, required=True)
    project.add_argument("--project-kb-dir", default="project-kb")
    project.add_argument("--project-rules-file", default="PROJECT_RULES.md")
    global_parser = subparsers.add_parser("check-global", help="检查全局研究知识库")
    global_parser.add_argument("--root", default=DEFAULT_GLOBAL_ROOT)
    global_parser.add_argument("--explicit", action="store_true")
    args = parser.parse_args()

    if args.command == "init-project":
        result = init_project(
            args.project_root,
            project_kb_dir=args.project_kb_dir,
            project_rules_file=args.project_rules_file,
        )
    else:
        result = check_global(args.root, explicit=args.explicit)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
