from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def render_document(data: dict[str, Any], body: str) -> str:
    return "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n" + body


def create_document(path: Path, data: dict[str, Any], body: str) -> str:
    """Create a document without silently replacing user-owned content.

    An identical rerun is idempotent. A semantic difference at an existing path
    is a conflict and must go through an explicit revision/update workflow.
    """
    content = render_document(data, body)
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return "unchanged"
        raise FileExistsError(f"document conflict: {path}; explicit revision is required")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return "created"


def update_document(path: Path, data: dict[str, Any], body: str, *, expected_revision: int) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"invalid document frontmatter: {path}")
    current = yaml.safe_load(text.split("---\n", 2)[1]) or {}
    if current.get("revision") != expected_revision:
        raise ValueError(f"revision conflict: {path}; expected {expected_revision}, found {current.get('revision')}")
    merged = dict(current)
    merged.update(data)
    merged["revision"] = expected_revision + 1
    path.write_text(render_document(merged, body), encoding="utf-8", newline="\n")
    return "updated"
