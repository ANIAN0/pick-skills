"""将 project-kb 目录渲染成单文件 HTML 可视化查看器。

输出文件包含 cytoscape + marked（CDN 加载）和所有概念/边的内嵌数据，
无外部依赖，可在浏览器中离线打开。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from viz.document import OKFDocument, OKFDocumentError

# 兼容直接 `python viz/generator.py` 调用与作为子模块调用两种场景。
if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from viz.document import OKFDocument, OKFDocumentError  # noqa: F401

_INDEX_NAME = "index.md"
_LOG_NAME = "log.md"
_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)")

# personal-kb 概念的默认调色板；类型不在此表的会回落到默认色。
_TYPE_PALETTE = {
    "Project Domain": "#8b5cf6",
    "Project Architecture": "#0ea5e9",
    "Project Code": "#3b82f6",
    "Project Decision": "#f59e0b",
    "Project Workflow": "#10b981",
}
_DEFAULT_NODE_COLOR = "#94a3b8"


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    resource: str
    tags: list[str]
    body: str
    source_path: str = ""
    links_to: list[str] = field(default_factory=list)

    def to_node(self) -> dict[str, Any]:
        color = _TYPE_PALETTE.get(self.type, _DEFAULT_NODE_COLOR)
        return {
            "data": {
                "id": self.id,
                "label": self.title or self.id,
                "type": self.type,
                "description": self.description,
                "resource": self.resource,
                "tags": self.tags,
                "color": color,
                "size": 30 + min(60, len(self.body) // 200),
            }
        }


def _extract_links(body: str, doc_dir: Path, bundle_root: Path) -> list[str]:
    """从正文中抽取相对 markdown 链接，并归一化到相对 bundle 的 id。"""
    out: list[str] = []
    seen: set[str] = set()
    bundle_root_resolved = bundle_root.resolve()
    for m in _LINK_RE.finditer(body):
        target = m.group(1)
        if "://" in target or target.startswith("/"):
            continue
        try:
            resolved = (doc_dir / target).resolve().relative_to(bundle_root_resolved)
        except (OSError, ValueError):
            continue
        rel = resolved.as_posix()
        if rel.endswith(".md"):
            rel = rel[:-3]
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def _walk_concepts(bundle_root: Path) -> list[Concept]:
    """扫描 bundle_root 下所有非保留 frontmatter 文档。"""
    concepts: list[Concept] = []
    for md_path in sorted(bundle_root.rglob("*.md")):
        if md_path.name in (_INDEX_NAME, _LOG_NAME):
            continue
        rel = md_path.relative_to(bundle_root).with_suffix("")
        concept_id = "/".join(rel.parts)
        try:
            doc = OKFDocument.parse(md_path.read_text(encoding="utf-8"))
        except OKFDocumentError:
            continue
        fm = doc.frontmatter or {}
        type_value = str(fm.get("type") or "").strip()
        if not type_value:
            # OKF v0.1 §9 强制：缺 type 的文档不算合规概念；可视化里不展示。
            continue
        tags_value = fm.get("tags") or []
        if not isinstance(tags_value, list):
            tags_value = [str(tags_value)]
        concept = Concept(
            id=concept_id,
            type=type_value,
            title=str(fm.get("title") or concept_id),
            description=str(fm.get("description") or ""),
            resource=str(fm.get("resource") or ""),
            tags=[str(t) for t in tags_value],
            body=doc.body or "",
            source_path=str(fm.get("source_path") or ""),
            links_to=_extract_links(doc.body or "", md_path.parent, bundle_root),
        )
        concepts.append(concept)
    return concepts


def _build_graph(concepts: list[Concept]) -> dict[str, Any]:
    """构建 cytoscape 所需的 nodes/edges/bodies/types/palette。"""
    ids = {c.id for c in concepts}
    nodes = [c.to_node() for c in concepts]
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str]] = set()
    for c in concepts:
        for target in c.links_to:
            if target == c.id or target not in ids:
                continue
            key = (c.id, target)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append(
                {
                    "data": {
                        "id": f"{c.id}__{target}",
                        "source": c.id,
                        "target": target,
                    }
                }
            )
    bodies = {c.id: c.body for c in concepts}
    types = sorted({c.type for c in concepts})
    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": bodies,
        "types": types,
        "palette": _TYPE_PALETTE,
    }


def _load_template(template_path: Path) -> str:
    return template_path.read_text(encoding="utf-8")


def _load_asset(asset_path: Path) -> str:
    return asset_path.read_text(encoding="utf-8")


def generate_visualization(
    bundle_root: Path,
    out_path: Path,
    *,
    bundle_name: str | None = None,
    template_path: Path | None = None,
    css_path: Path | None = None,
    js_path: Path | None = None,
) -> dict[str, int]:
    """扫描 bundle，写出单文件 HTML 可视化。返回 concepts/edges/bytes 计数。"""
    bundle_root = Path(bundle_root)
    out_path = Path(out_path)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"项目知识库目录不存在: {bundle_root}")

    base_dir = Path(__file__).resolve().parent
    template = _load_template(template_path or base_dir / "template.html")
    css = _load_asset(css_path or base_dir / "static" / "viz.css")
    js = _load_asset(js_path or base_dir / "static" / "viz.js")

    concepts = _walk_concepts(bundle_root)
    graph = _build_graph(concepts)
    name = bundle_name or bundle_root.resolve().name

    html = (
        template
        .replace("/*__VIZ_CSS__*/", css)
        .replace("/*__VIZ_JS__*/", js)
        .replace("__BUNDLE_NAME__", json.dumps(name))
        .replace("__BUNDLE_DATA__", json.dumps(graph))
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    return {
        "concepts": len(concepts),
        "edges": len(graph["edges"]),
        "bytes": len(html.encode("utf-8")),
    }