#!/usr/bin/env python3
"""初始化当前项目的最小 V3 研发工作区。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PERSONAL_KB_SCRIPTS = Path(__file__).resolve().parents[2] / "personal-kb" / "scripts"
if str(PERSONAL_KB_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PERSONAL_KB_SCRIPTS))
from kb_cli import init_project, validate_project  # noqa: E402


STAGE_DIRS = (
    "requirements",
    "tech-design",
    "implementation-planning",
    "acceptance",
)
VERSION_PATTERN = re.compile(r"\d+(?:\.\d+)?")


def _ensure_directory(path: Path, result: dict[str, Any]) -> None:
    if path.exists():
        if path.is_dir():
            result["preserved"].append(str(path))
        else:
            result["errors"].append(f"预期目录但发现文件: {path}")
        return
    path.mkdir(parents=True)
    result["created"].append(str(path))


def _write_if_missing(path: Path, content: str, result: dict[str, Any]) -> None:
    if path.exists():
        result["preserved"].append(str(path))
        return
    path.write_text(content, encoding="utf-8", newline="\n")
    result["created"].append(str(path))


def initialize_workspace(project_root: Path, version: str) -> dict[str, Any]:
    root = project_root.resolve()
    actual_version = version.strip()
    result: dict[str, Any] = {
        "project_root": str(root),
        "version": actual_version,
        "created": [],
        "preserved": [],
        "warnings": [],
        "errors": [],
    }

    if not root.is_dir():
        result["errors"].append(f"项目根目录不存在或不是目录: {root}")
        return result
    if not VERSION_PATTERN.fullmatch(actual_version):
        result["errors"].append("版本必须是整数或两段数字，例如 3 或 3.1")
        return result

    version_root = root / "workplace" / actual_version
    _ensure_directory(version_root, result)
    for stage in STAGE_DIRS:
        _ensure_directory(version_root / stage, result)
    if result["errors"]:
        return result

    _write_if_missing(
        root / "AGENTS.md",
        "# Agent 入口\n\n开始项目工作前，先读取同级 `PROJECT_RULES.md`。\n",
        result,
    )
    _write_if_missing(
        root / "PROJECT_RULES.md",
        """# 项目规则

本文件只记录修改当前项目之前必须知道的规则。

## 项目知识库

- [项目知识库](project-kb/index.md)
- [代码知识](project-kb/code/index.md)

## 项目规则与验证

- 仅在确认真实项目约束后补充规则和验证命令。
""",
        result,
    )

    kb_result = init_project(root)
    result["personal_kb"] = kb_result
    result["created"].extend(kb_result.get("created", []))
    result["warnings"].extend(kb_result.get("warnings", []))
    if kb_result.get("error"):
        result["errors"].append(kb_result["error"])
        return result

    validation = validate_project(root)
    result["personal_kb_validation"] = validation
    result["warnings"].extend(item["message"] for item in validation["warnings"])
    result["errors"].extend(
        f"{item['path']}: {item['message']}" for item in validation["errors"]
    )
    return result


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="初始化最小 V3 项目工作区")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    result = initialize_workspace(args.project_root, args.version)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
