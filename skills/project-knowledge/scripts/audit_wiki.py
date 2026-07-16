#!/usr/bin/env python3
"""生成 Wiki 来源覆盖账本，并严格检查覆盖、来源路径与本地链接。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:  # pragma: no cover - 由验证错误覆盖
    yaml = None


STATUSES = {
    "mapped",
    "consolidated",
    "superseded",
    "duplicate",
    "ignored",
    "sensitive",
    "unsupported",
    "conversion_failed",
    "read_failed",
    "pending",
}
BLOCKING_STATUSES = {"pending", "read_failed", "conversion_failed"}
AUTHORITATIVE_BLOCKING_STATUSES = BLOCKING_STATUSES | {"ignored", "unsupported"}
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
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
HTML_LINK = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SOURCE_WITH_SYMBOL = re.compile(
    r"^(.+\.(?:py|pyi|js|jsx|ts|tsx|vue|go|rs|java|kt|md|ya?ml|json|toml|sql|csv|html?|txt))(?:[:#].*)?$",
    re.IGNORECASE,
)
MAX_ISSUES = 250
OBJECT_SOURCE_SUFFIXES = {
    ".md", ".markdown", ".txt", ".doc", ".docx", ".pdf", ".html", ".htm", ".csv", ".xlsx"
}
OBJECT_HINT_PATTERN = re.compile(
    r"(?:\bREQ[-_ ]?\d+\b|\bPRD\b|\brequirements?\b|\bfeatures?\b|需求|规则|迭代|版本|决策|能力)",
    re.IGNORECASE,
)
STABLE_ID_PATTERN = re.compile(r"\b(?:REQ|PRD|RULE|DEC|ITER)[-_ ]?\d+\b", re.IGNORECASE)
CAPTURE_SCHEMA = "okf-conversation-capture/v1"
CAPTURE_KINDS = {"user-decision", "problem-report", "observation", "experience", "resolution"}


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _normalize_rel(value: str) -> str:
    return Path(value.replace("\\", "/").strip("/")).as_posix()


def _resolve_input_path(project_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else project_root / path).resolve()


def _valid_evidence_locator(
    project_root: Path, source_rel: str, raw: Any, sha256: str | None
) -> bool:
    if not isinstance(raw, str):
        return False
    evidence = raw.strip().replace("\\", "/")
    if not evidence.startswith(source_rel) or len(evidence) <= len(source_rel):
        return False
    separator = evidence[len(source_rel)]
    if separator not in {"#", ":"}:
        return False
    locator = evidence[len(source_rel) + 1 :].strip()
    if not locator:
        return False
    if locator.lower().startswith("sha256:"):
        prefix = locator.split(":", 1)[1].strip().lower()
        return len(prefix) >= 8 and isinstance(sha256, str) and sha256.lower().startswith(prefix)
    source_path = project_root / source_rel
    try:
        text = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    line_match = re.fullmatch(r"L(\d+)(?:-L?(\d+))?", locator, re.IGNORECASE)
    if line_match:
        start = int(line_match.group(1))
        end = int(line_match.group(2) or start)
        return 1 <= start <= end <= len(text.splitlines())
    folded = text.casefold()
    candidates = {locator.casefold(), locator.rsplit(".", 1)[-1].casefold()}
    candidates |= {item.replace("-", " ") for item in candidates}
    return any(len(item) >= 2 and item in folded for item in candidates)


def _detect_object_hints(path: Path) -> list[str]:
    if path.suffix.lower() not in {".md", ".markdown", ".txt", ".html", ".htm", ".csv"}:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    return sorted({match.group(0) for match in OBJECT_HINT_PATTERN.finditer(text)})[:20]


def _detect_stable_ids(path: Path) -> list[str]:
    if path.suffix.lower() not in {".md", ".markdown", ".txt", ".html", ".htm", ".csv"}:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    return sorted({match.group(0).upper().replace(" ", "-") for match in STABLE_ID_PATTERN.finditer(text)})


def _capture_metadata(path: Path) -> dict[str, Any] | None:
    """读取由 capture 命令生成的来源标记；普通 JSON 不受影响。"""
    if path.suffix.lower() != ".json":
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("schema") != CAPTURE_SCHEMA:
        return None
    kind = data.get("kind")
    capture_id = data.get("id")
    scope = data.get("scope")
    if (
        kind not in CAPTURE_KINDS
        or not isinstance(capture_id, str)
        or not capture_id.startswith("EVD-")
        or not isinstance(scope, str)
        or not scope.strip()
    ):
        return {"schema": CAPTURE_SCHEMA, "valid": False}
    assertion_type = "normative" if kind == "user-decision" else "reported"
    return {
        "schema": CAPTURE_SCHEMA,
        "valid": True,
        "id": capture_id,
        "kind": kind,
        "scope": scope.strip(),
        "assertion_type": assertion_type,
        "fact_eligible": False,
        "normative_eligible": kind == "user-decision",
        "verification_required": kind != "user-decision",
    }


def _is_explicitly_excluded(relative_dir: str, excluded: set[str]) -> bool:
    path = Path(relative_dir)
    if any(part in DEFAULT_EXCLUDED_NAMES for part in path.parts):
        return True
    return any(relative_dir == item or relative_dir.startswith(item + "/") for item in excluded)


def _is_protected(relative_dir: str, protected: set[str]) -> bool:
    return any(
        relative_dir == item
        or relative_dir.startswith(item + "/")
        or item.startswith(relative_dir + "/")
        for item in protected
    )


def discover_files(
    project_root: Path,
    *,
    wiki_root: Path,
    excluded_dirs: set[str],
    protected_dirs: set[str] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[str], list[dict[str, str]], list[dict[str, str]]]:
    """建立 canonical inventory；遍历、stat 和读取失败都进入结果，不能从分母消失。"""
    files: dict[str, dict[str, Any]] = {}
    empty_dirs: list[str] = []
    ignored_dirs: list[dict[str, str]] = []
    walk_errors: list[dict[str, str]] = []
    wiki_rel = _relative(project_root, wiki_root) if _within(project_root, wiki_root) else None
    explicit = {_normalize_rel(item) for item in excluded_dirs if item.strip()}
    protected = {_normalize_rel(item) for item in (protected_dirs or set()) if item.strip()}
    if wiki_rel is not None:
        explicit.add(wiki_rel)

    def on_walk_error(error: OSError) -> None:
        raw_path = Path(error.filename) if error.filename else project_root
        try:
            path = _relative(project_root, raw_path)
        except ValueError:
            path = str(raw_path)
        walk_errors.append({"path": path, "message": str(error)})

    for current_text, dir_names, file_names in os.walk(
        project_root, topdown=True, followlinks=False, onerror=on_walk_error
    ):
        current = Path(current_text)
        current_rel = "" if current == project_root else _relative(project_root, current)
        kept_dirs: list[str] = []
        for name in sorted(dir_names):
            child_rel = f"{current_rel}/{name}".strip("/")
            child_path = current / name
            is_wiki_output = wiki_rel is not None and (
                child_rel == wiki_rel or child_rel.startswith(wiki_rel + "/")
            )
            if is_wiki_output:
                ignored_dirs.append({"path": child_rel, "reason": "current Wiki output directory"})
            elif child_path.is_symlink():
                ignored_dirs.append({"path": child_rel, "reason": "symbolic link not followed"})
            elif _is_protected(child_rel, protected) or not _is_explicitly_excluded(child_rel, explicit):
                kept_dirs.append(name)
            else:
                ignored_dirs.append({"path": child_rel, "reason": "matched explicit/default exclusion"})
        dir_names[:] = kept_dirs

        kept_files: list[str] = []
        for name in sorted(file_names):
            path = current / name
            relative = _relative(project_root, path)
            if path.is_symlink():
                files[relative] = {
                    "discovery": "ignored",
                    "reason": "symbolic link not followed",
                    "size": None,
                    "sha256": None,
                }
                continue
            kept_files.append(name)
            digest = hashlib.sha256()
            try:
                size = path.stat().st_size
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                files[relative] = {
                    "discovery": "discovered",
                    "reason": "",
                    "size": size,
                    "sha256": digest.hexdigest(),
                }
            except (OSError, PermissionError) as error:
                files[relative] = {
                    "discovery": "read_failed",
                    "reason": str(error),
                    "size": None,
                    "sha256": None,
                }
        if current_rel and not kept_dirs and not kept_files:
            empty_dirs.append(current_rel)
    return dict(sorted(files.items())), sorted(empty_dirs), ignored_dirs, walk_errors


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
    wiki_root = _resolve_input_path(project_root, args.wiki_root)
    if wiki_root == project_root:
        return {"error": "wiki-root 不能与 project-root 相同，避免把输出当成来源"}
    raw_meta_root = getattr(args, "meta_root", None)
    meta_root = _resolve_input_path(project_root, raw_meta_root) if raw_meta_root else wiki_root / "_meta"
    coverage_path = meta_root / "coverage.json"

    existing: dict[str, Any] = {}
    if coverage_path.is_file():
        try:
            existing = _load_json(coverage_path)
        except ValueError as error:
            return {"error": str(error)}
    old_files = existing.get("files", {}) if isinstance(existing.get("files", {}), dict) else {}
    capture_registry: dict[str, Any] = {}
    registry_path = meta_root / "capture-registry.json"
    if registry_path.is_file():
        try:
            registry = _load_json(registry_path)
        except ValueError as error:
            return {"error": f"Capture registry 无法读取: {error}"}
        if registry.get("version") != 1 or not isinstance(registry.get("entries"), dict):
            return {"error": "Capture registry schema 无效"}
        capture_registry = registry["entries"]
    old_scope = existing.get("scope", {}) if isinstance(existing.get("scope", {}), dict) else {}
    authoritative = args.authoritative_root or old_scope.get("authoritative_roots", [])
    user_excluded = list(args.exclude_dir or old_scope.get("user_excluded_dirs", []))
    excluded = set(user_excluded)
    if _within(project_root, meta_root):
        excluded.add(_relative(project_root, meta_root))
    profile = getattr(args, "profile", None) or old_scope.get("profile", "generic")
    if profile == "personal" and user_excluded:
        return {
            "error": "personal profile 不允许用 --exclude-dir 移除来源；为每个真实来源根建立独立 manifest"
        }
    if profile in {"project", "product"} and not authoritative:
        return {"error": f"{profile} profile 必须显式声明至少一个 authoritative-root"}
    missing_authoritative = [
        item for item in authoritative if not (project_root / _normalize_rel(item)).exists()
    ]
    if missing_authoritative:
        return {"error": f"权威来源根目录不存在: {', '.join(missing_authoritative)}"}
    discovered, empty_dirs, ignored_dirs, walk_errors = discover_files(
        project_root,
        wiki_root=wiki_root,
        excluded_dirs=excluded,
        protected_dirs={_normalize_rel(item) for item in authoritative},
    )
    hidden_captures: list[str] = []
    for raw_path in capture_registry:
        if not isinstance(raw_path, str):
            return {"error": "Capture registry 来源路径必须是字符串"}
        capture_path = _normalize_rel(raw_path)
        candidate = (project_root / capture_path).resolve()
        if not _within(project_root, candidate):
            return {"error": f"Capture registry 来源越出 project-root: {raw_path}"}
        if candidate.is_file() and capture_path not in discovered:
            hidden_captures.append(capture_path)
    if hidden_captures:
        return {
            "error": "已登记 Capture 被 inventory 排除，拒绝生成不完整 coverage: "
            + ", ".join(sorted(hidden_captures))
        }

    entries: dict[str, dict[str, Any]] = {}
    added: list[str] = []
    changed: list[str] = []
    for path, discovery in discovered.items():
        previous = old_files.get(path)
        detected_capture = _capture_metadata(project_root / path)
        registered_capture = capture_registry.get(path)
        if not isinstance(registered_capture, dict) and isinstance(previous, dict):
            registered_capture = previous.get("capture")
        if isinstance(registered_capture, dict):
            registry_hash = registered_capture.get("source_sha256") or (
                previous.get("sha256") if isinstance(previous, dict) else None
            )
            registered_kind = registered_capture.get("kind")
            valid = (
                isinstance(detected_capture, dict)
                and detected_capture.get("valid") is True
                and detected_capture.get("id") == registered_capture.get("id")
                and discovery.get("sha256") == registry_hash
            )
            discovery["capture"] = {
                **registered_capture,
                "schema": CAPTURE_SCHEMA,
                "source_sha256": registry_hash,
                "fact_eligible": False,
                "normative_eligible": registered_kind == "user-decision",
                "valid": valid,
                "tampered": not valid,
            }
        elif detected_capture is not None:
            discovery["capture"] = detected_capture
        if profile == "product" and Path(path).suffix.lower() in OBJECT_SOURCE_SUFFIXES:
            discovery["object_hints"] = _detect_object_hints(project_root / path)
            discovery["stable_id_hints"] = _detect_stable_ids(project_root / path)
        fingerprint_matches = (
            isinstance(previous, dict)
            and previous.get("sha256") == discovery.get("sha256")
            and previous.get("discovery") == discovery.get("discovery")
        )
        if fingerprint_matches:
            entries[path] = {**previous, **discovery}
        else:
            status = discovery["discovery"] if discovery["discovery"] != "discovered" else "pending"
            entries[path] = {
                **discovery,
                "status": status,
                "targets": [],
                "evidence": [],
                "claims": [],
                "object_disposition": "unknown" if profile == "product" else "not_applicable",
                "objects": [],
                "reason": discovery.get("reason", ""),
            }
            if isinstance(previous, dict):
                changed.append(path)
            else:
                added.append(path)
    old_changes = existing.get("changes", {}) if isinstance(existing.get("changes"), dict) else {}
    old_removed = old_changes.get("removed", []) if isinstance(old_changes.get("removed"), list) else []
    removed = sorted(set(old_removed) | (set(old_files) - set(discovered)))
    payload = {
        "version": 2,
        "generated_at": _now(),
        "scan": {
            "state": "partial"
            if walk_errors or any(item["discovery"] == "read_failed" for item in discovered.values())
            else "complete",
            "discovered": len(entries),
            "walk_errors": walk_errors,
        },
        "scope": {
            "wiki_root": _relative(project_root, wiki_root)
            if _within(project_root, wiki_root)
            else str(wiki_root),
            "meta_root": _relative(project_root, meta_root)
            if _within(project_root, meta_root)
            else str(meta_root),
            "profile": profile,
            "authoritative_roots": sorted({_normalize_rel(item) for item in authoritative}),
            "user_excluded_dirs": sorted({_normalize_rel(item) for item in user_excluded}),
            "excluded_dirs": sorted({_normalize_rel(item) for item in excluded}),
            "default_excluded_names": sorted(DEFAULT_EXCLUDED_NAMES),
            "empty_dirs": empty_dirs,
            "ignored_dirs": ignored_dirs,
        },
        "changes": {"added": added, "changed": changed, "removed": removed},
        "files": entries,
        "objects": existing.get("objects", {}) if isinstance(existing.get("objects"), dict) else {},
        "pages": existing.get("pages", {}) if isinstance(existing.get("pages"), dict) else {},
        "review_overrides": existing.get("review_overrides", {})
        if isinstance(existing.get("review_overrides"), dict)
        else {},
        "review": existing.get("review", {}) if isinstance(existing.get("review"), dict) else {},
    }
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return {
        "coverage_file": str(coverage_path),
        "inventory_total": len(entries),
        "added": added,
        "changed": changed,
        "removed": removed,
        "empty_dirs": empty_dirs,
        "ignored_dirs": ignored_dirs,
        "walk_errors": walk_errors,
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


def _tree_sha256(root: Path, excluded_root: Path | None = None) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if excluded_root is not None and _within(excluded_root, path):
            continue
        relative = _relative(root, path)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        try:
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError as error:
            digest.update(f"READ_ERROR:{error}".encode("utf-8", errors="replace"))
        digest.update(b"\0")
    return digest.hexdigest()


def _coverage_sha256(coverage: dict[str, Any]) -> str:
    core = {key: value for key, value in coverage.items() if key != "review"}
    encoded = json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _check_markdown(
    project_root: Path,
    wiki_root: Path,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
    *,
    profile: str,
    sidecar_pages: dict[str, Any],
) -> tuple[dict[str, set[str]], dict[str, dict[str, Any]]]:
    page_sources: dict[str, set[str]] = {}
    page_metadata: dict[str, dict[str, Any]] = {}
    if yaml is None:
        _issue(errors, str(wiki_root), "缺少 PyYAML，无法验证 frontmatter 来源")
    for page in sorted(wiki_root.rglob("*.md")):
        relative = _relative(wiki_root, page)
        page_sources[relative] = set()
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            _issue(errors, relative, f"无法读取 Markdown: {error}")
            continue
        local_links = (
            MARKDOWN_LINK.findall(text)
            + REFERENCE_LINK.findall(text)
            + HTML_LINK.findall(text)
        )
        for raw in local_links:
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
            if not _within(project_root, target) and not _within(wiki_root, target):
                _issue(errors, relative, f"本地链接越出项目根与 OKF 根: {raw}")
            elif not target.exists():
                _issue(errors, relative, f"本地链接目标不存在: {raw}")

        match = FRONTMATTER.match(text)
        is_control = page.name in {"index.md", "purpose.md", "log.md", "INSTRUCTIONS.md"} or relative.startswith("_meta/")
        metadata: Any = None
        if match and yaml is not None:
            try:
                metadata = yaml.safe_load(match.group(1))
            except yaml.YAMLError as error:
                _issue(errors, relative, f"frontmatter 无法解析: {error}")
                continue
        elif not match and profile == "generic" and isinstance(sidecar_pages.get(relative), dict):
            metadata = sidecar_pages[relative]
        elif not match:
            if not is_control:
                _issue(
                    errors,
                    relative,
                    "普通内容页缺少 YAML frontmatter；建设类 profile 必须写入 OKF 概念页，发布视图请单独按 generic 检查",
                )
            continue
        if not isinstance(metadata, dict):
            _issue(errors, relative, "frontmatter 必须是对象")
            continue
        page_metadata[relative] = metadata
        if not is_control:
            for field in ("type", "title", "description", "state", "updated_at"):
                value = metadata.get(field)
                valid_value = (
                    isinstance(value, (date, datetime))
                    or (isinstance(value, str) and bool(value.strip()))
                    if field == "updated_at"
                    else isinstance(value, str) and bool(value.strip())
                )
                if not valid_value:
                    _issue(errors, relative, f"普通内容页缺少非空 {field}")
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
            else:
                page_sources[relative].add(_relative(project_root, target))
    return page_sources, page_metadata


def validate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    wiki_root = _resolve_input_path(project_root, args.wiki_root)
    if wiki_root == project_root:
        return {
            "errors": [{"path": str(wiki_root), "message": "wiki-root 不能与 project-root 相同"}],
            "warnings": [],
            "valid": False,
        }
    raw_meta_root = getattr(args, "meta_root", None)
    meta_root = _resolve_input_path(project_root, raw_meta_root) if raw_meta_root else wiki_root / "_meta"
    coverage_path = meta_root / "coverage.json"
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
    if coverage.get("version") != 2:
        _issue(errors, str(coverage_path), "coverage schema 已过期；重新运行 inventory 生成 v2 账本")
    scope = coverage.get("scope", {}) if isinstance(coverage.get("scope"), dict) else {}
    expected_profile = getattr(args, "profile", None)
    if expected_profile is None:
        _issue(errors, str(coverage_path), "validate 必须显式传入期望 --profile")
    elif scope.get("profile") != expected_profile:
        _issue(
            errors,
            str(coverage_path),
            f"coverage profile 与期望不一致: {scope.get('profile')} != {expected_profile}",
        )
    changes = coverage.get("changes", {}) if isinstance(coverage.get("changes"), dict) else {}
    removed_sources = changes.get("removed", []) if isinstance(changes.get("removed"), list) else []
    for path in removed_sources:
        _issue(errors, str(path), "已删除/移动来源尚未完成陈旧页面、关系和导航清理；处理后清空 changes.removed")
    excluded = set(scope.get("excluded_dirs", []))
    authoritative = {_normalize_rel(item) for item in scope.get("authoritative_roots", [])}
    for root in sorted(authoritative):
        if not (project_root / root).exists():
            _issue(errors, root, "coverage 声明的权威来源根目录不存在")
    discovered, _, _, walk_errors = discover_files(
        project_root,
        wiki_root=wiki_root,
        excluded_dirs=excluded,
        protected_dirs=authoritative,
    )
    for item in walk_errors:
        _issue(errors, item["path"], f"目录遍历失败: {item['message']}")
    entries = coverage.get("files", {}) if isinstance(coverage.get("files"), dict) else {}
    discovered_set = set(discovered)
    entry_set = set(entries)
    for path in sorted(discovered_set - entry_set):
        _issue(errors, path, "文件系统存在但 coverage 未登记")
    for path in sorted(entry_set - discovered_set):
        _issue(errors, path, "coverage 条目已失效，文件系统中不存在")

    for path in sorted(discovered_set & entry_set):
        entry = entries.get(path)
        current = discovered[path]
        if not isinstance(entry, dict):
            continue
        if entry.get("sha256") != current.get("sha256") or entry.get("discovery") != current.get("discovery"):
            _issue(errors, path, "来源内容或可读状态已变化；重新运行 inventory 后重新处置")

    profile = scope.get("profile", "generic")
    raw_source_filter = getattr(args, "source", None)
    source_filter = _normalize_rel(raw_source_filter) if raw_source_filter else None
    if profile in {"personal", "project", "product"}:
        for relative_control in ("purpose.md", "INSTRUCTIONS.md", "log.md", "_meta/schema.md", "_meta/state.json"):
            if not (wiki_root / relative_control).is_file():
                _issue(errors, relative_control, "OKF 规范知识层缺少必需控制面文件")
        root_index = wiki_root / "index.md"
        if not root_index.is_file():
            _issue(errors, "index.md", "OKF 规范知识层缺少根 index.md")
        else:
            try:
                root_text = root_index.read_text(encoding="utf-8")
                root_match = FRONTMATTER.match(root_text)
                if not root_match or yaml is None:
                    _issue(errors, "index.md", 'OKF 根 index.md 缺少可解析 frontmatter 与 okf_version: "0.1"')
                else:
                    root_metadata = yaml.safe_load(root_match.group(1))
                    if not isinstance(root_metadata, dict) or str(root_metadata.get("okf_version")) != "0.1":
                        _issue(errors, "index.md", 'OKF 根 index.md 必须声明 okf_version: "0.1"')
            except (OSError, UnicodeError, yaml.YAMLError if yaml is not None else ValueError) as error:
                _issue(errors, "index.md", f"OKF 根 index.md 无法解析: {error}")
    pages = coverage.get("pages", {}) if isinstance(coverage.get("pages"), dict) else {}
    if profile in {"personal", "project", "product"} and pages:
        _issue(errors, "coverage.pages", "OKF 规范知识层不能用发布页 sidecar 代替概念页")
    page_sources, page_metadata = _check_markdown(
        project_root,
        wiki_root,
        errors,
        warnings,
        profile=profile,
        sidecar_pages=pages,
    )
    for page_rel in pages:
        page_path = (wiki_root / _normalize_rel(str(page_rel))).resolve()
        if not _within(wiki_root, page_path) or not page_path.is_file():
            _issue(errors, str(page_rel), "coverage.pages 条目没有对应的内容页面")
            continue
        try:
            if FRONTMATTER.match(page_path.read_text(encoding="utf-8")):
                _issue(errors, str(page_rel), "页面已有 frontmatter，不应再用 coverage.pages 维护重复元数据")
        except (OSError, UnicodeError):
            pass
    objects = coverage.get("objects", {}) if isinstance(coverage.get("objects"), dict) else {}
    review = coverage.get("review", {}) if isinstance(coverage.get("review"), dict) else {}
    review_overrides = (
        coverage.get("review_overrides", {})
        if isinstance(coverage.get("review_overrides"), dict)
        else {}
    )
    none_overrides = {
        item.get("path"): item
        for item in review_overrides.get("none", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    stable_id_overrides = {
        (item.get("path"), str(item.get("id", "")).upper()): item
        for item in review_overrides.get("stable_ids", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    counts: Counter[str] = Counter()
    for path, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            _issue(errors, path, "coverage 条目必须是对象")
            continue
        capture = entry.get("capture")
        if capture is not None and (
            not isinstance(capture, dict)
            or capture.get("schema") != CAPTURE_SCHEMA
            or capture.get("valid") is not True
        ):
            _issue(errors, path, "对话 Capture 来源 schema 无效，不能进入知识库")
        status = entry.get("status")
        counts[str(status)] += 1
        if status not in STATUSES:
            _issue(errors, path, f"未知处置状态: {status}")
            continue
        if isinstance(capture, dict) and capture.get("valid") is True and status in {"ignored", "unsupported"}:
            _issue(errors, path, "用户明确创建的 Capture 不能以 ignored/unsupported 静默丢弃")
        discovery_state = entry.get("discovery")
        if discovery_state in {"read_failed", "ignored"} and status != discovery_state:
            _issue(errors, path, f"扫描状态 {discovery_state} 不能改写为处置状态 {status}")
        if status in BLOCKING_STATUSES:
            _issue(errors, path, f"来源处置仍处于阻塞状态: {status}")
        is_authoritative = any(
            path == root or path.startswith(root + "/") for root in authoritative
        )
        is_document_candidate = Path(path).suffix.lower() in OBJECT_SOURCE_SUFFIXES
        if is_authoritative and status in AUTHORITATIVE_BLOCKING_STATUSES:
            _issue(errors, path, f"权威来源不能以 {status} 通过完整性验收")
        if profile in {"project", "product"} and is_document_candidate and status in {"ignored", "unsupported"}:
            _issue(errors, path, f"{profile} profile 的文档候选不能以 {status} 绕过逐文件处置")
        if status in {"mapped", "consolidated", "superseded"}:
            targets = entry.get("targets")
            if not isinstance(targets, list) or not targets:
                _issue(errors, path, f"{status} 缺少目标页")
            else:
                has_precise_non_index_target = False
                for target in targets:
                    if not isinstance(target, str):
                        _issue(errors, path, f"目标页不存在: {target}")
                        continue
                    target_path = (wiki_root / target).resolve()
                    target_rel = _normalize_rel(target)
                    if not _within(wiki_root, target_path) or not target_path.is_file():
                        _issue(errors, path, f"目标页不存在或越出 OKF 根: {target}")
                        continue
                    if path in page_sources.get(target_rel, set()):
                        if Path(target_rel).name.lower() != "index.md":
                            has_precise_non_index_target = True
                    else:
                        _issue(errors, path, f"目标页未反向登记精确来源: {target_rel}")
                if is_authoritative and not has_precise_non_index_target:
                    _issue(errors, path, "权威来源不能只映射到总索引或目录 index.md")
            evidence = entry.get("evidence")
            if not isinstance(evidence, list) or not any(
                _valid_evidence_locator(project_root, path, item, entry.get("sha256"))
                for item in evidence
            ):
                _issue(
                    errors,
                    path,
                    f"{status} 缺少可验证 evidence；使用 <来源>#L行、#标题/ID、:符号或 #sha256:前缀",
                )
            claims = entry.get("claims")
            if not isinstance(claims, list) or not claims:
                _issue(errors, path, f"{status} 缺少 claims")
            else:
                claim_targets: set[str] = set()
                for index, claim in enumerate(claims):
                    claim_valid = False
                    if not isinstance(claim, dict):
                        _issue(errors, path, f"claim[{index}] 必须是对象")
                        continue
                    claim_target = claim.get("target")
                    claim_text = claim.get("text")
                    claim_evidence = claim.get("evidence")
                    if isinstance(capture, dict) and capture.get("valid") is True:
                        expected_assertion = capture.get("assertion_type")
                        if claim.get("assertion_type") != expected_assertion:
                            _issue(
                                errors,
                                path,
                                f"claim[{index}] assertion_type 必须是 {expected_assertion}；Capture 不能提升自身证明力",
                            )
                            continue
                    if (
                        isinstance(claim_target, str)
                        and claim_target in (targets if isinstance(targets, list) else [])
                        and isinstance(claim_text, str)
                        and len(claim_text.strip()) >= 8
                        and _valid_evidence_locator(
                            project_root, path, claim_evidence, entry.get("sha256")
                        )
                    ):
                        target_path = (wiki_root / _normalize_rel(claim_target)).resolve()
                        try:
                            if claim_text.strip().casefold() in target_path.read_text(
                                encoding="utf-8"
                            ).casefold():
                                claim_valid = True
                                claim_targets.add(_normalize_rel(claim_target))
                        except (OSError, UnicodeError):
                            pass
                    if not claim_valid:
                        _issue(errors, path, f"claim[{index}] 的 evidence/text/target 未逐条验证")
                expected_claim_targets = {
                    _normalize_rel(target) for target in (targets if isinstance(targets, list) else [])
                    if isinstance(target, str)
                }
                if claim_targets != expected_claim_targets:
                    _issue(errors, path, "claims 未逐目标覆盖全部 targets")
        if status == "duplicate":
            canonical = entry.get("canonical_source")
            canonical_entry = entries.get(canonical) if isinstance(canonical, str) else None
            if canonical == path or not isinstance(canonical_entry, dict):
                _issue(errors, path, "duplicate 必须指向另一个已登记 canonical_source")
            elif entry.get("sha256") != canonical_entry.get("sha256"):
                _issue(errors, path, "duplicate 仅用于内容指纹完全相同的来源；语义合并使用 consolidated")
        if status == "superseded":
            replacement = entry.get("replacement_source")
            if replacement == path or not isinstance(replacement, str) or not isinstance(entries.get(replacement), dict):
                _issue(errors, path, "superseded 必须指向另一个已登记 replacement_source")
        if status == "sensitive":
            sensitivity = entry.get("sensitivity")
            if sensitivity not in {"secret", "credential", "personal", "security", "restricted"}:
                _issue(errors, path, "sensitive 缺少明确 sensitivity 分类")
        if status in {
            "consolidated",
            "superseded",
            "duplicate",
            "ignored",
            "sensitive",
            "unsupported",
            "conversion_failed",
            "read_failed",
        } and not str(entry.get("reason", "")).strip():
            _issue(errors, path, f"{status} 缺少可复核理由")
        if is_authoritative and status in {"sensitive", "duplicate", "superseded"}:
            if len(str(entry.get("reason", "")).strip()) < 8:
                _issue(errors, path, "权威来源的非映射理由过于笼统")
        if profile == "product" and is_document_candidate:
            disposition = entry.get("object_disposition")
            object_ids = entry.get("objects")
            if disposition not in {"contains", "none"}:
                _issue(errors, path, "产品权威文档尚未判定是否包含稳定对象")
            elif disposition == "contains" and (not isinstance(object_ids, list) or not object_ids):
                _issue(errors, path, "标记为 contains 但未登记稳定对象 ID")
            elif disposition == "none" and len(str(entry.get("reason", "")).strip()) < 8:
                _issue(errors, path, "不包含稳定对象的判断缺少可复核理由")
            if disposition == "none" and entry.get("object_hints"):
                override = none_overrides.get(path)
                valid_override = (
                    isinstance(override, dict)
                    and len(str(override.get("rationale", "")).strip()) >= 8
                    and _valid_evidence_locator(
                        project_root, path, override.get("evidence"), entry.get("sha256")
                    )
                )
                if not valid_override:
                    _issue(
                        errors,
                        path,
                        "文档命中稳定对象提示词，不能直接标 none；需要 reviewer 在 none_overrides 提供有效 evidence 与 rationale",
                    )
            if isinstance(object_ids, list):
                for object_id in object_ids:
                    if not isinstance(object_id, str) or object_id not in objects:
                        _issue(errors, path, f"引用了未登记的稳定对象: {object_id}")
                for hinted_id in entry.get("stable_id_hints", []):
                    if hinted_id in object_ids:
                        continue
                    override = stable_id_overrides.get((path, str(hinted_id).upper()))
                    valid_override = (
                        isinstance(override, dict)
                        and len(str(override.get("rationale", "")).strip()) >= 8
                        and _valid_evidence_locator(
                            project_root, path, override.get("evidence"), entry.get("sha256")
                        )
                    )
                    if not valid_override:
                        _issue(
                            errors,
                            path,
                            f"来源出现稳定 ID {hinted_id}，必须登记为对象或在 review_overrides.stable_ids 说明仅为引用",
                        )

    for object_id, obj in sorted(objects.items()):
        object_path = f"objects:{object_id}"
        if not isinstance(obj, dict):
            _issue(errors, object_path, "稳定对象条目必须是对象")
            continue
        if not all(isinstance(obj.get(field), str) and obj[field].strip() for field in ("type", "id", "title")):
            _issue(errors, object_path, "稳定对象缺少非空 type/id/title")
        elif obj["id"] != object_id:
            _issue(errors, object_path, f"稳定对象 key 与 id 不一致: {obj['id']}")
        if object_id.upper().startswith("REQ") and obj.get("type") != "Product Requirement":
            _issue(errors, object_path, "REQ 稳定 ID 必须使用 Product Requirement 类型")
        sources = obj.get("source_paths")
        target = obj.get("target")
        if not isinstance(sources, list) or not sources:
            _issue(errors, object_path, "稳定对象缺少 source_paths")
            continue
        if not isinstance(target, str) or not target.strip():
            _issue(errors, object_path, "稳定对象缺少规范 target")
            continue
        target_rel = _normalize_rel(target)
        target_path = (wiki_root / target_rel).resolve()
        if not _within(wiki_root, target_path) or not target_path.is_file():
            _issue(errors, object_path, f"稳定对象目标页不存在或越界: {target}")
            continue
        if Path(target_rel).name.lower() == "index.md":
            _issue(errors, object_path, "稳定对象不能把 index.md 作为规范页")
        metadata = page_metadata.get(target_rel, {})
        for field in ("type", "id", "title"):
            if metadata.get(field) != obj.get(field):
                _issue(
                    errors,
                    object_path,
                    f"规范页 {field} 与稳定对象不一致: {metadata.get(field)!r} != {obj.get(field)!r}",
                )
        for source in sources:
            source_rel = _normalize_rel(str(source))
            source_entry = entries.get(source_rel)
            if not isinstance(source_entry, dict):
                _issue(errors, object_path, f"稳定对象来源未进入 coverage: {source}")
                continue
            if object_id not in source_entry.get("objects", []):
                _issue(errors, object_path, f"来源未反向登记稳定对象: {source}")
            if source_rel not in page_sources.get(target_rel, set()):
                _issue(errors, object_path, f"规范页未反向登记精确来源: {source}")

    page_ids: dict[str, list[str]] = {}
    for page_rel, metadata in page_metadata.items():
        page_id = metadata.get("id")
        if not isinstance(page_id, str) or not page_id.strip():
            continue
        page_ids.setdefault(page_id, []).append(page_rel)
        if profile == "product":
            obj = objects.get(page_id)
            if not isinstance(obj, dict):
                _issue(errors, page_rel, f"规范页 ID 未登记到 coverage.objects: {page_id}")
            elif _normalize_rel(str(obj.get("target", ""))) != page_rel:
                _issue(errors, page_rel, f"规范页不是稳定对象 {page_id} 声明的 target")
    for page_id, paths in page_ids.items():
        if len(paths) > 1:
            _issue(errors, f"id:{page_id}", f"多个规范页使用同一稳定 ID: {', '.join(paths)}")

    if profile in {"project", "product"}:
        registered_targets = {
            _normalize_rel(str(target))
            for entry in entries.values()
            if isinstance(entry, dict) and entry.get("status") in {"mapped", "consolidated"}
            for target in entry.get("targets", [])
            if isinstance(target, str)
        }
        registered_targets |= {
            _normalize_rel(str(obj.get("target")))
            for obj in objects.values()
            if isinstance(obj, dict) and isinstance(obj.get("target"), str)
        }
        for page_rel in page_metadata:
            if Path(page_rel).name in {"index.md", "purpose.md", "log.md", "INSTRUCTIONS.md"} or page_rel.startswith("_meta/"):
                continue
            if page_rel not in registered_targets:
                _issue(errors, page_rel, "正文页未被任何来源处置或稳定对象登记，可能是陈旧/孤立页面")

    wiki_sha256 = _tree_sha256(
        wiki_root, meta_root if _within(wiki_root, meta_root) else None
    )
    coverage_sha256 = _coverage_sha256(coverage)
    if profile in {"personal", "project", "product"}:
        required_review_strings = (
            "reviewer",
            "artifact",
            "artifact_sha256",
            "coverage_sha256",
            "wiki_sha256",
        )
        if review.get("status") != "passed":
            _issue(errors, "review", f"批量 {profile} Wiki 缺少 passed 的 fresh-context review")
        for field in required_review_strings:
            if not isinstance(review.get(field), str) or not review[field].strip():
                _issue(errors, "review", f"fresh-context review 缺少非空 {field}")
        if review.get("coverage_sha256") != coverage_sha256:
            _issue(errors, "review", "review 后 coverage 内容已变化，必须重新审查")
        if review.get("wiki_sha256") != wiki_sha256:
            _issue(errors, "review", "review 后 Wiki 内容已变化，必须重新审查")
        if review.get("blocker_count") != 0:
            _issue(errors, "review", "fresh-context review 仍有 blocker")
        artifact = review.get("artifact")
        artifact_data: dict[str, Any] = {}
        if isinstance(artifact, str) and artifact.strip():
            artifact_path = _resolve_input_path(project_root, artifact)
            allowed_artifact = any(
                _within(root, artifact_path) for root in (project_root, wiki_root, meta_root)
            )
            if not allowed_artifact or not artifact_path.is_file():
                _issue(errors, "review", f"review artifact 不存在或越出允许根: {artifact}")
            elif artifact_path.suffix.lower() != ".json":
                _issue(errors, "review", "review artifact 必须是可机读 JSON")
            else:
                try:
                    artifact_bytes = artifact_path.read_bytes()
                    artifact_data = json.loads(artifact_bytes.decode("utf-8"))
                    artifact_hash = hashlib.sha256(artifact_bytes).hexdigest()
                    if review.get("artifact_sha256") != artifact_hash:
                        _issue(errors, "review", "review artifact 内容已变化")
                except (OSError, UnicodeError, json.JSONDecodeError) as error:
                    _issue(errors, "review", f"review artifact 无法解析: {error}")
        if artifact_data:
            if artifact_data.get("reviewer") != review.get("reviewer"):
                _issue(errors, "review", "review summary 与 artifact 的 reviewer 不一致")
            if not isinstance(artifact_data.get("reviewed_at"), str) or not artifact_data["reviewed_at"].strip():
                _issue(errors, "review", "review artifact 缺少 reviewed_at")
            if artifact_data.get("fresh_context") is not True or artifact_data.get("participated_in_build") is not False:
                _issue(errors, "review", "review artifact 未声明 fresh_context=true 且 participated_in_build=false")
            reviewer_context = artifact_data.get("reviewer_context_id")
            builder_context = artifact_data.get("builder_context_id")
            if not all(isinstance(item, str) and item.strip() for item in (reviewer_context, builder_context)):
                _issue(errors, "review", "review artifact 缺少 reviewer_context_id/builder_context_id")
            elif reviewer_context == builder_context:
                _issue(errors, "review", "reviewer_context_id 不能与 builder_context_id 相同")
            if artifact_data.get("coverage_sha256") != coverage_sha256 or artifact_data.get("wiki_sha256") != wiki_sha256:
                _issue(errors, "review", "review artifact 未绑定当前 coverage/Wiki 摘要")
            if artifact_data.get("blocker_count") != 0:
                _issue(errors, "review", "review artifact 仍有 blocker")
            if not isinstance(artifact_data.get("findings"), list):
                _issue(errors, "review", "review artifact 缺少 findings 列表")
            retrieval_tests = artifact_data.get("retrieval_tests")
            minimum_tests = 3 if profile == "personal" else 4
            if not isinstance(retrieval_tests, list) or len(retrieval_tests) < minimum_tests:
                _issue(errors, "review", f"review artifact 至少需要 {minimum_tests} 个 retrieval_tests")
            elif any(
                not isinstance(item, dict)
                or not all(str(item.get(field, "")).strip() for field in ("question", "result", "evidence"))
                for item in retrieval_tests
            ):
                _issue(errors, "review", "每个 retrieval_test 必须包含 question/result/evidence")
            checks = artifact_data.get("coverage_checks")
            if not isinstance(checks, dict) or checks.get("filesystem_reconciled") is not True:
                _issue(errors, "review", "review artifact 未证明独立文件系统对账")
        expected_none = sorted(
            path
            for path, entry in entries.items()
            if isinstance(entry, dict) and entry.get("object_disposition") == "none"
        )
        reviewed_none = artifact_data.get("reviewed_none_sources")
        if profile == "product" and (
            not isinstance(reviewed_none, list)
            or sorted(str(item) for item in reviewed_none) != expected_none
        ):
            _issue(errors, "review", "reviewed_none_sources 必须逐项覆盖所有 object_disposition:none 文档")
        expected_sensitive = sorted(
            path
            for path, entry in entries.items()
            if isinstance(entry, dict) and entry.get("status") == "sensitive"
        )
        reviewed_sensitive = artifact_data.get("reviewed_sensitive_sources")
        if not isinstance(reviewed_sensitive, list) or sorted(
            str(item) for item in reviewed_sensitive
        ) != expected_sensitive:
            _issue(errors, "review", "reviewed_sensitive_sources 必须逐项覆盖所有 sensitive 来源")

    total_by_status = sum(counts[status] for status in STATUSES)
    if total_by_status != len(entries):
        _issue(errors, str(coverage_path), "处置状态计数不等于 inventory_total")
    if source_filter is not None:
        source_entry = entries.get(source_filter)
        relevant_paths = {
            source_filter,
            "index.md",
            "purpose.md",
            "INSTRUCTIONS.md",
            "log.md",
            "_meta/schema.md",
            str(coverage_path),
        }
        relevant_objects: set[str] = set()
        if not isinstance(source_entry, dict):
            _issue(errors, source_filter, "来源级校验目标未进入 coverage")
        else:
            relevant_paths.update(
                _normalize_rel(str(target))
                for target in source_entry.get("targets", [])
                if isinstance(target, str)
            )
            relevant_objects.update(
                str(object_id)
                for object_id in source_entry.get("objects", [])
                if isinstance(object_id, str)
            )

        def is_relevant(issue: dict[str, str]) -> bool:
            issue_path = str(issue.get("path", ""))
            if issue_path in relevant_paths:
                return True
            if issue_path.startswith("objects:"):
                return issue_path.removeprefix("objects:") in relevant_objects
            if issue_path.startswith("id:"):
                return issue_path.removeprefix("id:") in relevant_objects
            return False

        errors = [issue for issue in errors if is_relevant(issue)]
        warnings = [issue for issue in warnings if is_relevant(issue)]
    return {
        "coverage_file": str(coverage_path),
        "inventory_total": len(entries),
        "accounted_total": total_by_status,
        "scan_state": "partial"
        if walk_errors or any(item["discovery"] == "read_failed" for item in discovered.values())
        else "complete",
        "wiki_sha256": wiki_sha256,
        "coverage_sha256": coverage_sha256,
        "status_counts": dict(sorted(counts.items())),
        "source_filter": source_filter,
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
        child.add_argument(
            "--okf-root",
            "--wiki-root",
            dest="wiki_root",
            required=True,
            help="OKF 规范知识层根目录；--wiki-root 是兼容别名",
        )
        child.add_argument(
            "--meta-root",
            default=None,
            help="控制面目录；默认 <wiki-root>/_meta，公开站点可放到非发布目录",
        )
        child.add_argument(
            "--profile",
            choices=["generic", "personal", "project", "product"],
            required=command == "validate",
            default=None,
            help="inventory 记录 profile；validate 必须重复声明并与 coverage 锁定",
        )
        if command == "inventory":
            child.add_argument("--authoritative-root", action="append", default=[])
            child.add_argument("--exclude-dir", action="append", default=[])
        else:
            child.add_argument(
                "--source",
                default=None,
                help="只验证一个 coverage 来源事务；允许其他来源继续 pending，且不要求全库 review",
            )
    args = parser.parse_args()
    result = inventory(args) if args.command == "inventory" else validate(args)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result.get("error") or result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
