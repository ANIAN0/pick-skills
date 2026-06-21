#!/usr/bin/env python3
"""初始化并校验当前项目的最小 OKF project-kb。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:  # pragma: no cover - 由运行环境错误路径覆盖
    yaml = None


FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK = re.compile(r"\[\[[^\]]+\]\]")
DATE_HEADING = re.compile(r"(?m)^##\s+\d{4}-\d{2}-\d{2}\s*$")


def _parse_frontmatter(
    match: re.Match[str] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if match is None:
        return None, "缺少 YAML frontmatter"
    if yaml is None:
        return None, "无法解析 YAML frontmatter：缺少 PyYAML"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return None, f"YAML frontmatter 无法解析: {error}"
    if not isinstance(data, dict):
        return None, "YAML frontmatter 必须是映射"
    return data, None


def _minimal_files(project_rules_file: str) -> dict[str, str]:
    return {
        "index.md": (
            '---\nokf_version: "0.1"\n---\n\n'
            "# 项目知识库\n\n"
            "本知识库保存当前项目长期有效、经过验证的知识。\n\n"
            "## 入口\n\n"
            "- [代码知识](code/index.md) - 按源码路径维护的职责、逻辑和测试映射。\n\n"
            f"## 项目规则\n\n- [项目规则](../{project_rules_file})\n"
        ),
        "log.md": (
            "# 项目知识库更新记录\n\n"
            "<!-- 按 YYYY-MM-DD 倒序记录有意义的知识变化。 -->\n"
        ),
        "code/index.md": (
            "# 代码知识\n\n"
            "按源码相对路径镜像项目代码知识。\n"
        ),
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
            "root": str(root / project_kb_dir),
            "created": [],
            "error": f"项目规则文件不存在: {rules}",
        }

    kb_root = root / project_kb_dir
    kb_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for relative_path, content in _minimal_files(project_rules_file).items():
        path = kb_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8", newline="\n")
            created.append(str(path))

    rules_text = rules.read_text(encoding="utf-8")
    expected_target = f"{project_kb_dir}/index.md"
    has_entry_link = any(
        _link_target(raw) == expected_target
        for raw in MARKDOWN_LINK.findall(rules_text)
    )
    legacy_files = [
        str(path)
        for path in (kb_root / "README.md", kb_root / "changelog.md")
        if path.exists()
    ]
    warnings: list[str] = []
    if not has_entry_link:
        warnings.append("PROJECT_RULES.md 缺少指向 project-kb/index.md 的标准 Markdown 链接")
    if legacy_files:
        warnings.append("发现旧知识库保留文件；请按迁移流程处理，不会自动覆盖或删除")
    return {
        "root": str(kb_root),
        "created": created,
        "missing_rule_links": [] if has_entry_link else [expected_target],
        "legacy_files": legacy_files,
        "warnings": warnings,
        "error": None,
    }


def _link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(" ", 1)[0]
    return unquote(urlsplit(target).path).replace("\\", "/")


def _resolve_local_link(source: Path, raw: str, kb_root: Path) -> Path | None:
    target = raw.strip()
    if target.startswith(("#", "mailto:", "http://", "https://")):
        return None
    path_text = _link_target(target)
    if not path_text:
        return None
    candidate = kb_root / path_text.lstrip("/") if path_text.startswith("/") else source.parent / path_text
    candidate = candidate.resolve()
    if candidate.is_dir():
        candidate = candidate / "index.md"
    return candidate


def validate_project(
    project_root: Path,
    *,
    project_kb_dir: str = "project-kb",
) -> dict[str, Any]:
    root = project_root.resolve()
    kb_root = root / project_kb_dir
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    checked = 0

    if not kb_root.is_dir():
        return {
            "root": str(kb_root),
            "checked_files": 0,
            "errors": [{"path": str(kb_root), "message": "项目知识库目录不存在"}],
            "warnings": [],
            "valid": False,
        }

    required = (kb_root / "index.md", kb_root / "log.md", kb_root / "code" / "index.md")
    for path in required:
        if not path.is_file():
            errors.append({"path": str(path), "message": "缺少最小 OKF bundle 文件"})

    legacy = (kb_root / "README.md", kb_root / "changelog.md")
    for path in legacy:
        if path.exists():
            errors.append({"path": str(path), "message": "旧保留文件尚未迁移为 index.md 或 log.md"})

    for path in sorted(kb_root.rglob("*.md")):
        checked += 1
        relative = path.relative_to(kb_root).as_posix()
        text = path.read_text(encoding="utf-8")
        if WIKI_LINK.search(text):
            errors.append({"path": relative, "message": "包含不可移植的 wiki link"})

        match = FRONTMATTER.match(text)
        if path.name == "index.md":
            if path == kb_root / "index.md":
                metadata, parse_error = _parse_frontmatter(match)
                if parse_error:
                    errors.append({"path": relative, "message": parse_error})
                elif str(metadata.get("okf_version")) != "0.1":
                    errors.append({"path": relative, "message": "根 index.md 缺少 okf_version: \"0.1\""})
            if path != kb_root / "index.md" and FRONTMATTER.match(text):
                errors.append({"path": relative, "message": "子目录 index.md 不应包含 frontmatter"})
        elif path.name == "log.md":
            if FRONTMATTER.match(text):
                errors.append({"path": relative, "message": "log.md 不应包含 frontmatter"})
            if "## " in text and not DATE_HEADING.search(text):
                errors.append({"path": relative, "message": "log.md 日期标题必须使用 YYYY-MM-DD"})
        else:
            metadata, parse_error = _parse_frontmatter(match)
            if parse_error:
                errors.append({"path": relative, "message": parse_error})
            elif not isinstance(metadata.get("type"), str) or not metadata["type"].strip():
                errors.append({"path": relative, "message": "概念文档缺少非空 type"})

        for raw_link in MARKDOWN_LINK.findall(text):
            target = _resolve_local_link(path, raw_link, kb_root)
            if target is not None and not target.exists():
                errors.append(
                    {"path": relative, "message": f"本地链接目标不存在: {raw_link.strip()}"}
                )

    if not any(path.name != "index.md" for path in (kb_root / "code").rglob("*.md")):
        warnings.append({"path": "code/index.md", "message": "尚无代码概念；按实际需要创建"})

    return {
        "root": str(kb_root),
        "checked_files": checked,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="初始化或校验当前项目的 OKF project-kb。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    project = subparsers.add_parser("init-project", help="初始化最小 OKF project-kb")
    project.add_argument("--project-root", type=Path, required=True)
    project.add_argument("--project-kb-dir", default="project-kb")
    project.add_argument("--project-rules-file", default="PROJECT_RULES.md")

    validate = subparsers.add_parser("validate-project", help="校验 OKF 格式和本地链接")
    validate.add_argument("--project-root", type=Path, required=True)
    validate.add_argument("--project-kb-dir", default="project-kb")
    args = parser.parse_args()

    if args.command == "init-project":
        result = init_project(
            args.project_root,
            project_kb_dir=args.project_kb_dir,
            project_rules_file=args.project_rules_file,
        )
    else:
        result = validate_project(args.project_root, project_kb_dir=args.project_kb_dir)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result.get("error") or result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
