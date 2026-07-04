#!/usr/bin/env python3
"""初始化并校验当前项目的最小 OKF project-kb。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
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


def _minimal_files() -> dict[str, str]:
    return {
        "index.md": (
            '---\nokf_version: "0.1"\n---\n\n'
            "# 项目知识库\n\n"
            "本知识库保存当前项目长期有效、经过验证的知识。\n\n"
            "## 入口\n\n"
            "- [代码知识](code/index.md) - 按源码路径维护的职责、逻辑和测试映射。\n"
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
    kb_root = root / project_kb_dir
    kb_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for relative_path, content in _minimal_files().items():
        path = kb_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8", newline="\n")
            created.append(str(path))

    warnings: list[str] = []
    missing_rule_links: list[str] = []
    rules = root / project_rules_file
    if rules.is_file():
        rules_text = rules.read_text(encoding="utf-8")
        expected_target = f"{project_kb_dir}/index.md"
        has_entry_link = any(
            _link_target(raw) == expected_target
            for raw in MARKDOWN_LINK.findall(rules_text)
        )
        if not has_entry_link:
            warnings.append(f"{project_rules_file} 缺少指向 {expected_target} 的标准 Markdown 链接")
            missing_rule_links.append(expected_target)
    legacy_files = [
        str(path)
        for path in (kb_root / "README.md", kb_root / "changelog.md")
        if path.exists()
    ]
    if legacy_files:
        warnings.append("发现旧知识库保留文件；请按迁移流程处理，不会自动覆盖或删除")
    return {
        "root": str(kb_root),
        "created": created,
        "missing_rule_links": missing_rule_links,
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


def _safe_bundle_path(kb_root: Path, relative: str) -> Path | None:
    """解析 kb_root 内的相对路径；空字符串或越界返回 None 或 kb_root。"""
    cleaned = _link_target(relative).lstrip("/") if relative else ""
    candidate = kb_root if not cleaned else (kb_root / cleaned)
    try:
        candidate = candidate.resolve()
        candidate.relative_to(kb_root.resolve())
    except (OSError, ValueError):
        return None
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
            else:
                for required_field in ("type", "title", "description"):
                    value = metadata.get(required_field)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            {
                                "path": relative,
                                "message": f"概念文档缺少非空 {required_field}",
                            }
                        )
                if metadata.get("type") == "Project Code":
                    source_path = metadata.get("source_path")
                    if not isinstance(source_path, str) or not source_path.strip():
                        errors.append(
                            {
                                "path": relative,
                                "message": "Project Code 概念缺少非空 source_path",
                            }
                        )

        for raw_link in MARKDOWN_LINK.findall(text):
            target = _resolve_local_link(path, raw_link, kb_root)
            if target is not None and not target.exists():
                # OKF v0.1 §9: 消费侧 MUST NOT reject a bundle because of broken
                # cross-links. 把断链归为 warning；写入侧另行通过质量检查发现。
                warnings.append(
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _now_date() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def _parse_concept_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """frontmatter 接受 JSON 或 YAML 文本；type/title/description 必填。"""
    stripped = text.strip()
    if not stripped:
        return None, "frontmatter 不能为空"
    if yaml is None:
        return None, "无法解析 frontmatter：缺少 PyYAML"
    data: Any
    try:
        if stripped.startswith("{"):
            data = json.loads(stripped)
        else:
            data = yaml.safe_load(stripped)
    except (json.JSONDecodeError, yaml.YAMLError) as error:
        return None, f"frontmatter 解析失败: {error}"
    if not isinstance(data, dict):
        return None, "frontmatter 必须是映射"
    for required_field in ("type", "title", "description"):
        value = data.get(required_field)
        if not isinstance(value, str) or not value.strip():
            return None, f"frontmatter 缺少非空 {required_field} 字段"
    if data.get("type") == "Project Code":
        source_path = data.get("source_path")
        if not isinstance(source_path, str) or not source_path.strip():
            return None, "Project Code frontmatter 缺少非空 source_path 字段"
    return data, None


def _append_index_link(index_path: Path, rel_link: str, title: str, description: str) -> bool:
    """在 index.md 末尾的 `## 入口` / `## 条目` 段落（缺则末尾）追加链接，已存在则跳过。"""
    if not index_path.exists():
        return False
    text = index_path.read_text(encoding="utf-8")
    if f"]({rel_link})" in text:
        return False
    lines = text.splitlines(keepends=True)
    insert_at = len(lines)
    for idx, line in enumerate(lines):
        if re.match(r"^##\s+", line):
            candidate = idx + 1
            while candidate < len(lines) and not re.match(r"^##\s+", lines[candidate]) and lines[candidate].strip() == "":
                candidate += 1
            insert_at = candidate
    entry = f"- [{title}]({rel_link})"
    if description:
        entry += f" - {description}"
    lines.insert(insert_at, entry + "\n")
    index_path.write_text("".join(lines), encoding="utf-8", newline="\n")
    return True


def _append_log_entry(kb_root: Path, mode: str, rel_link: str, frontmatter: dict[str, Any]) -> None:
    """在 log.md 的当天标题下追加一条记录。"""
    log_path = kb_root / "log.md"
    if not log_path.exists():
        log_path.write_text(
            "# 项目知识库更新记录\n\n<!-- 按 YYYY-MM-DD 倒序记录有意义的知识变化。 -->\n\n",
            encoding="utf-8",
            newline="\n",
        )
    title = str(frontmatter.get("title", rel_link))
    action = "Creation" if mode == "create" else "Update"
    line = f"- **{action}**: [{title}]({rel_link})"
    text = log_path.read_text(encoding="utf-8")
    heading = f"## {_now_date()}"
    if heading in text:
        parts = text.split(heading, 1)
        tail = parts[1]
        if "\n## " in tail:
            head, rest = tail.split("\n## ", 1)
            head = head.rstrip("\n") + "\n" + line + "\n\n## "
            text = parts[0] + heading + head + rest
        else:
            text = parts[0] + heading + "\n" + line + "\n"
    else:
        text = text.rstrip() + f"\n\n{heading}\n\n{line}\n"
    log_path.write_text(text, encoding="utf-8", newline="\n")


def write_concept(
    project_root: Path,
    *,
    path: str,
    frontmatter_text: str,
    content_text: str,
    mode: str = "create",
    project_kb_dir: str = "project-kb",
) -> dict[str, Any]:
    """写入或更新一个 OKF 概念文档；同步父目录 index.md 与 log.md。"""
    if mode not in ("create", "update"):
        return {"path": path, "error": f"不支持的 mode: {mode}（create 或 update）"}

    kb_root = project_root.resolve() / project_kb_dir
    if not kb_root.is_dir():
        return {
            "path": path,
            "error": f"项目知识库目录不存在: {kb_root}；先运行 init-project",
        }

    target = _safe_bundle_path(kb_root, path)
    if target is None or target.suffix != ".md":
        return {"path": path, "error": f"路径不合法或越界: {path}"}

    frontmatter, parse_error = _parse_concept_frontmatter(frontmatter_text)
    if parse_error:
        return {"path": path, "error": parse_error}

    exists = target.is_file()
    if mode == "create" and exists:
        return {"path": path, "error": f"目标已存在: {path}；用 --mode update"}
    if mode == "update" and not exists:
        return {"path": path, "error": f"目标不存在: {path}；用 --mode create"}

    frontmatter.setdefault("timestamp", _now_iso())
    title = str(frontmatter.get("title", target.stem))
    description = str(frontmatter.get("description", "")).strip()

    fm_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).rstrip()
    body = content_text.rstrip() + "\n"
    file_content = f"---\n{fm_yaml}\n---\n\n{body}"

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(file_content, encoding="utf-8", newline="\n")

    rel_link = target.relative_to(kb_root).as_posix()
    parent_dir = target.parent
    parent_index = parent_dir / "index.md"
    if parent_index == kb_root / "index.md":
        if not parent_index.exists():
            parent_index.write_text(
                '---\nokf_version: "0.1"\n---\n\n# 项目知识库\n\n'
                "本知识库保存当前项目长期有效、经过验证的知识。\n\n## 入口\n\n",
                encoding="utf-8",
                newline="\n",
            )
        _append_index_link(parent_index, rel_link, title, description)
    else:
        if not parent_index.exists():
            parent_index.write_text(
                f"# {parent_dir.name}\n\n按主题维护的知识条目。\n\n## 条目\n\n",
                encoding="utf-8",
                newline="\n",
            )
        _append_index_link(parent_index, target.name, title, description)

    _append_log_entry(kb_root, mode, rel_link, frontmatter)

    return {
        "path": rel_link,
        "mode": mode,
        "created": mode == "create",
        "updated": mode == "update",
        "frontmatter": frontmatter,
        "error": None,
    }


def list_kb(
    project_root: Path,
    *,
    path: str = "",
    project_kb_dir: str = "project-kb",
) -> dict[str, Any]:
    """列出 project-kb 内某子目录的条目。"""
    kb_root = project_root.resolve() / project_kb_dir
    if not kb_root.is_dir():
        return {
            "root": str(kb_root),
            "path": path,
            "items": [],
            "error": f"项目知识库目录不存在: {kb_root}",
        }
    target = _safe_bundle_path(kb_root, path)
    if target is None or not target.is_dir():
        return {
            "root": str(kb_root),
            "path": path,
            "items": [],
            "error": f"路径不存在或越界: {path or '.'}",
        }
    items: list[dict[str, str]] = []
    for entry in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        items.append(
            {
                "name": entry.name,
                "path": entry.relative_to(kb_root).as_posix(),
                "type": "directory" if entry.is_dir() else "file",
            }
        )
    return {"root": str(kb_root), "path": path, "items": items, "error": None}


def read_kb(
    project_root: Path,
    *,
    path: str,
    project_kb_dir: str = "project-kb",
) -> dict[str, Any]:
    """读取 project-kb 内单个文件的全文。"""
    kb_root = project_root.resolve() / project_kb_dir
    if not kb_root.is_dir():
        return {
            "root": str(kb_root),
            "path": path,
            "content": None,
            "error": f"项目知识库目录不存在: {kb_root}",
        }
    target = _safe_bundle_path(kb_root, path)
    if target is None or not target.is_file():
        return {
            "root": str(kb_root),
            "path": path,
            "content": None,
            "error": f"文件不存在或越界: {path}",
        }
    return {
        "root": str(kb_root),
        "path": path,
        "content": target.read_text(encoding="utf-8"),
        "error": None,
    }


def search_kb(
    project_root: Path,
    *,
    query: str,
    path: str = "",
    project_kb_dir: str = "project-kb",
) -> dict[str, Any]:
    """在 project-kb 的 .md 文件中做大小写不敏感的正则搜索。"""
    kb_root = project_root.resolve() / project_kb_dir
    if not kb_root.is_dir():
        return {
            "root": str(kb_root),
            "query": query,
            "matches": [],
            "error": f"项目知识库目录不存在: {kb_root}",
        }
    target = _safe_bundle_path(kb_root, path)
    if target is None or not target.exists():
        return {
            "root": str(kb_root),
            "query": query,
            "matches": [],
            "error": f"路径不存在或越界: {path or '.'}",
        }
    try:
        regex = re.compile(query, re.IGNORECASE)
    except re.error as exc:
        return {
            "root": str(kb_root),
            "query": query,
            "matches": [],
            "error": f"无效正则: {exc}",
        }

    files: list[Path]
    if target.is_file():
        files = [target] if target.suffix == ".md" else []
    else:
        files = sorted(target.rglob("*.md"))

    matches: list[dict[str, Any]] = []
    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                matches.append(
                    {
                        "file": file.relative_to(kb_root).as_posix(),
                        "line": line_no,
                        "content": line.strip(),
                    }
                )
    return {"root": str(kb_root), "query": query, "matches": matches, "error": None}


def generate_viz(
    project_root: Path,
    *,
    output: Path | None = None,
    bundle_name: str = "",
    project_kb_dir: str = "project-kb",
) -> dict[str, Any]:
    """把 project-kb 渲染成单文件 HTML 可视化（输出在 project-kb 内）。"""
    from viz.generator import generate_visualization

    project_root = project_root.resolve()
    kb_root = project_root / project_kb_dir
    if not kb_root.is_dir():
        return {
            "root": str(kb_root),
            "output": None,
            "error": f"项目知识库目录不存在: {kb_root}",
        }
    target = output if output is not None else kb_root / "viz.html"
    target = Path(target)
    counts = generate_visualization(
        kb_root,
        target,
        bundle_name=bundle_name or None,
    )
    return {
        "root": str(kb_root),
        "output": str(target),
        "bundle_name": bundle_name or kb_root.resolve().name,
        **counts,
        "error": None,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="初始化、校验或浏览当前项目的 OKF project-kb。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    project = subparsers.add_parser("init-project", help="初始化最小 OKF project-kb")
    project.add_argument("--project-root", type=Path, required=True)
    project.add_argument("--project-kb-dir", default="project-kb")
    project.add_argument("--project-rules-file", default="PROJECT_RULES.md")

    validate = subparsers.add_parser("validate-project", help="校验 OKF 格式和本地链接")
    validate.add_argument("--project-root", type=Path, required=True)
    validate.add_argument("--project-kb-dir", default="project-kb")

    list_cmd = subparsers.add_parser("list-kb", help="列出 project-kb 中的条目")
    list_cmd.add_argument("--project-root", type=Path, required=True)
    list_cmd.add_argument("--path", default="", help="相对于 project-kb 的子路径；空字符串表示根目录")
    list_cmd.add_argument("--project-kb-dir", default="project-kb")

    read_cmd = subparsers.add_parser("read-kb", help="读取 project-kb 中的单个文件")
    read_cmd.add_argument("--project-root", type=Path, required=True)
    read_cmd.add_argument("--path", required=True, help="相对于 project-kb 的文件路径")
    read_cmd.add_argument("--project-kb-dir", default="project-kb")

    search_cmd = subparsers.add_parser("search-kb", help="在 project-kb 的 .md 文件中正则搜索")
    search_cmd.add_argument("--project-root", type=Path, required=True)
    search_cmd.add_argument("--query", required=True, help="正则表达式（大小写不敏感）")
    search_cmd.add_argument("--path", default="", help="限定搜索的子目录或单个 .md 文件")
    search_cmd.add_argument("--project-kb-dir", default="project-kb")

    viz_cmd = subparsers.add_parser("viz", help="把 project-kb 渲染成单文件 HTML 可视化")
    viz_cmd.add_argument("--project-root", type=Path, required=True)
    viz_cmd.add_argument(
        "--output",
        type=Path,
        default=None,
        help="HTML 输出路径；默认写到 <project-kb>/viz.html",
    )
    viz_cmd.add_argument(
        "--bundle-name",
        default="",
        help="在 HTML 顶部显示的 bundle 名称；默认用 project-kb 目录名",
    )
    viz_cmd.add_argument("--project-kb-dir", default="project-kb")

    write_cmd = subparsers.add_parser("write-concept", help="写入或更新一个 OKF 概念文档")
    write_cmd.add_argument("--project-root", type=Path, required=True)
    write_cmd.add_argument("--path", required=True, help="相对于 project-kb 的文件路径，如 architecture/auth-flow.md")
    write_cmd.add_argument(
        "--frontmatter",
        required=True,
        help="YAML 或 JSON 字符串；必须包含非空 type/title/description 字段",
    )
    write_cmd.add_argument(
        "--content",
        required=True,
        help="Markdown 正文（frontmatter 之外的 body）",
    )
    write_cmd.add_argument(
        "--mode",
        choices=["create", "update"],
        default="create",
        help="create 写入新文档，update 覆盖已有文档",
    )
    write_cmd.add_argument("--project-kb-dir", default="project-kb")

    args = parser.parse_args()

    commands: dict[str, Any] = {
        "init-project": lambda: init_project(
            args.project_root,
            project_kb_dir=args.project_kb_dir,
            project_rules_file=args.project_rules_file,
        ),
        "validate-project": lambda: validate_project(
            args.project_root, project_kb_dir=args.project_kb_dir
        ),
        "list-kb": lambda: list_kb(
            args.project_root,
            path=args.path,
            project_kb_dir=args.project_kb_dir,
        ),
        "read-kb": lambda: read_kb(
            args.project_root,
            path=args.path,
            project_kb_dir=args.project_kb_dir,
        ),
        "search-kb": lambda: search_kb(
            args.project_root,
            query=args.query,
            path=args.path,
            project_kb_dir=args.project_kb_dir,
        ),
        "viz": lambda: generate_viz(
            args.project_root,
            output=args.output,
            bundle_name=args.bundle_name,
            project_kb_dir=args.project_kb_dir,
        ),
        "write-concept": lambda: write_concept(
            args.project_root,
            path=args.path,
            frontmatter_text=args.frontmatter,
            content_text=args.content,
            mode=args.mode,
            project_kb_dir=args.project_kb_dir,
        ),
    }
    result = commands[args.command]()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result.get("error") or result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
