#!/usr/bin/env python3
"""生成 Wiki 来源覆盖账本，并严格检查覆盖、来源路径与本地链接。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:  # pragma: no cover - 由验证错误覆盖
    yaml = None


STATUSES = {"mapped", "consolidated", "superseded", "duplicate", "excluded", "pending"}
DEFAULT_EXCLUDED_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".pnpm",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".next",
    ".nuxt",
    ".turbo",
    "dist",
    "build",
    "coverage",
    "target",
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SOURCE_WITH_SYMBOL = re.compile(
    r"^(.+\.(?:py|pyi|js|jsx|ts|tsx|vue|go|rs|java|kt|md|ya?ml|json|toml|sql|csv|html?|txt))(?:[:#].*)?$",
    re.IGNORECASE,
)
MAX_ISSUES = 250


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _normalize_rel(value: str) -> str:
    return Path(value.replace("\\", "/").strip("/")).as_posix()


def _is_explicitly_excluded(relative_dir: str, excluded: set[str]) -> bool:
    path = Path(relative_dir)
    if any(part in DEFAULT_EXCLUDED_NAMES for part in path.parts):
        return True
    return any(relative_dir == item or relative_dir.startswith(item + "/") for item in excluded)


def discover_files(
    project_root: Path,
    *,
    wiki_root: Path,
    excluded_dirs: set[str],
) -> tuple[list[str], list[str]]:
    """不读取 .gitignore；只应用明确排除目录，并记录空目录。"""
    files: list[str] = []
    empty_dirs: list[str] = []
    wiki_rel = _relative(project_root, wiki_root)
    explicit = {_normalize_rel(item) for item in excluded_dirs if item.strip()}
    explicit.add(wiki_rel)

    for current_text, dir_names, file_names in os.walk(project_root, topdown=True, followlinks=False):
        current = Path(current_text)
        current_rel = "" if current == project_root else _relative(project_root, current)
        kept_dirs: list[str] = []
        for name in sorted(dir_names):
            child_rel = f"{current_rel}/{name}".strip("/")
            if not _is_explicitly_excluded(child_rel, explicit):
                kept_dirs.append(name)
        dir_names[:] = kept_dirs

        kept_files = []
        for name in sorted(file_names):
            path = current / name
            if path.is_symlink():
                continue
            kept_files.append(name)
            files.append(_relative(project_root, path))
        if current_rel and not kept_dirs and not kept_files:
            empty_dirs.append(current_rel)
    return sorted(files), sorted(empty_dirs)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"无法读取 coverage 文件: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("coverage 文件顶层必须是对象")
    return data


def inventory(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    wiki_root = (project_root / args.wiki_root).resolve()
    try:
        wiki_root.relative_to(project_root)
    except ValueError:
        return {"error": "wiki-root 必须位于 project-root 内"}
    coverage_path = wiki_root / "_meta" / "coverage.json"

    existing: dict[str, Any] = {}
    if coverage_path.is_file():
        try:
            existing = _load_json(coverage_path)
        except ValueError as error:
            return {"error": str(error)}
    old_files = existing.get("files", {}) if isinstance(existing.get("files", {}), dict) else {}
    old_scope = existing.get("scope", {}) if isinstance(existing.get("scope", {}), dict) else {}
    authoritative = args.authoritative_root or old_scope.get("authoritative_roots", [])
    excluded = set(args.exclude_dir or old_scope.get("excluded_dirs", []))
    missing_authoritative = [
        item for item in authoritative if not (project_root / _normalize_rel(item)).exists()
    ]
    if missing_authoritative:
        return {"error": f"权威来源根目录不存在: {', '.join(missing_authoritative)}"}
    discovered, empty_dirs = discover_files(
        project_root, wiki_root=wiki_root, excluded_dirs=excluded
    )

    entries: dict[str, dict[str, Any]] = {}
    added: list[str] = []
    for path in discovered:
        previous = old_files.get(path)
        if isinstance(previous, dict):
            entries[path] = previous
        else:
            entries[path] = {"status": "pending", "targets": [], "reason": ""}
            added.append(path)
    removed = sorted(set(old_files) - set(discovered))
    payload = {
        "version": 1,
        "generated_at": _now(),
        "scope": {
            "wiki_root": _relative(project_root, wiki_root),
            "authoritative_roots": sorted({_normalize_rel(item) for item in authoritative}),
            "excluded_dirs": sorted({_normalize_rel(item) for item in excluded}),
            "default_excluded_names": sorted(DEFAULT_EXCLUDED_NAMES),
            "empty_dirs": empty_dirs,
        },
        "files": entries,
    }
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return {
        "coverage_file": str(coverage_path),
        "inventory_total": len(entries),
        "added": added,
        "removed": removed,
        "empty_dirs": empty_dirs,
        "status_counts": dict(Counter(item.get("status") for item in entries.values())),
        "error": None,
    }


def _issue(items: list[dict[str, str]], path: str, message: str) -> None:
    if len(items) < MAX_ISSUES:
        items.append({"path": path, "message": message})


def _link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(" ", 1)[0]
    return unquote(urlsplit(target).path).replace("\\", "/")


def _within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _check_markdown(
    project_root: Path,
    wiki_root: Path,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    if yaml is None:
        _issue(errors, str(wiki_root), "缺少 PyYAML，无法验证 frontmatter 来源")
    for page in sorted(wiki_root.rglob("*.md")):
        relative = _relative(wiki_root, page)
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            _issue(errors, relative, f"无法读取 Markdown: {error}")
            continue
        for raw in MARKDOWN_LINK.findall(text):
            if raw.strip().startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_text = _link_target(raw)
            if not path_text:
                continue
            target = (
                project_root / path_text.lstrip("/")
                if path_text.startswith("/")
                else page.parent / path_text
            ).resolve()
            if not _within(project_root, target):
                _issue(errors, relative, f"本地链接越出项目根: {raw}")
            elif not target.exists():
                _issue(errors, relative, f"本地链接目标不存在: {raw}")

        match = FRONTMATTER.match(text)
        is_control = page.name in {"index.md", "log.md", "INSTRUCTIONS.md"} or relative.startswith("_meta/")
        if not match:
            if not is_control:
                _issue(errors, relative, "普通内容页缺少 YAML frontmatter")
            continue
        if yaml is None:
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            _issue(errors, relative, f"frontmatter 无法解析: {error}")
            continue
        if not isinstance(metadata, dict):
            _issue(errors, relative, "frontmatter 必须是对象")
            continue
        sources = metadata.get("sources")
        if not is_control and (not isinstance(sources, list) or not sources):
            _issue(errors, relative, "普通内容页缺少非空 sources")
            continue
        if not isinstance(sources, list):
            continue
        for source in sources:
            if not isinstance(source, str) or not source.strip():
                _issue(errors, relative, "sources 必须包含非空字符串")
                continue
            raw_source = source.strip()
            if raw_source.startswith(("http://", "https://")):
                continue
            match_source = SOURCE_WITH_SYMBOL.match(raw_source)
            path_text = match_source.group(1) if match_source else raw_source
            target = (
                (page.parent / path_text).resolve()
                if path_text.startswith(("./", "../"))
                else (project_root / path_text.lstrip("/")).resolve()
            )
            if not _within(project_root, target):
                _issue(errors, relative, f"source 越出项目根: {source}")
            elif not target.exists():
                _issue(errors, relative, f"source 路径不存在: {source}")
            elif target.is_dir():
                _issue(warnings, relative, f"source 只指向目录，不能证明具体结论: {source}")


def validate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    wiki_root = (project_root / args.wiki_root).resolve()
    coverage_path = wiki_root / "_meta" / "coverage.json"
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not coverage_path.is_file():
        return {
            "coverage_file": str(coverage_path),
            "errors": [{"path": str(coverage_path), "message": "coverage 文件不存在"}],
            "warnings": [],
            "valid": False,
        }
    try:
        coverage = _load_json(coverage_path)
    except ValueError as error:
        return {"errors": [{"path": str(coverage_path), "message": str(error)}], "warnings": [], "valid": False}
    scope = coverage.get("scope", {}) if isinstance(coverage.get("scope"), dict) else {}
    excluded = set(scope.get("excluded_dirs", []))
    authoritative = {_normalize_rel(item) for item in scope.get("authoritative_roots", [])}
    for root in sorted(authoritative):
        if not (project_root / root).exists():
            _issue(errors, root, "coverage 声明的权威来源根目录不存在")
    discovered, _ = discover_files(project_root, wiki_root=wiki_root, excluded_dirs=excluded)
    entries = coverage.get("files", {}) if isinstance(coverage.get("files"), dict) else {}
    discovered_set = set(discovered)
    entry_set = set(entries)
    for path in sorted(discovered_set - entry_set):
        _issue(errors, path, "文件系统存在但 coverage 未登记")
    for path in sorted(entry_set - discovered_set):
        _issue(errors, path, "coverage 条目已失效，文件系统中不存在")

    counts: Counter[str] = Counter()
    for path, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            _issue(errors, path, "coverage 条目必须是对象")
            continue
        status = entry.get("status")
        counts[str(status)] += 1
        if status not in STATUSES:
            _issue(errors, path, f"未知处置状态: {status}")
            continue
        if status == "pending":
            _issue(errors, path, "来源仍为 pending")
        if status in {"mapped", "consolidated"}:
            targets = entry.get("targets")
            if not isinstance(targets, list) or not targets:
                _issue(errors, path, f"{status} 缺少目标页")
            else:
                for target in targets:
                    if not isinstance(target, str) or not (wiki_root / target).is_file():
                        _issue(errors, path, f"目标页不存在: {target}")
        if status in {"superseded", "duplicate", "excluded"} and not str(entry.get("reason", "")).strip():
            _issue(errors, path, f"{status} 缺少可复核理由")
        if any(path == root or path.startswith(root + "/") for root in authoritative) and status == "excluded":
            if len(str(entry.get("reason", "")).strip()) < 8:
                _issue(errors, path, "权威来源排除理由过于笼统")

    _check_markdown(project_root, wiki_root, errors, warnings)
    total_by_status = sum(counts.values())
    if total_by_status != len(entries):
        _issue(errors, str(coverage_path), "处置状态计数不等于 inventory_total")
    return {
        "coverage_file": str(coverage_path),
        "inventory_total": len(entries),
        "status_counts": dict(sorted(counts.items())),
        "errors": errors,
        "error_count": len(errors),
        "errors_truncated": len(errors) >= MAX_ISSUES,
        "warnings": warnings,
        "warning_count": len(warnings),
        "warnings_truncated": len(warnings) >= MAX_ISSUES,
        "valid": not errors,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="生成并验证 Wiki 全量来源覆盖账本。")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("inventory", "validate"):
        child = subparsers.add_parser(command)
        child.add_argument("--project-root", type=Path, required=True)
        child.add_argument("--wiki-root", required=True, help="相对于 project-root 的 Wiki 根目录")
        if command == "inventory":
            child.add_argument("--authoritative-root", action="append", default=[])
            child.add_argument("--exclude-dir", action="append", default=[])
    args = parser.parse_args()
    result = inventory(args) if args.command == "inventory" else validate(args)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result.get("error") or result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
