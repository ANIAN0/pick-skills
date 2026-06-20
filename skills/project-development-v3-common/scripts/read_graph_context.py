from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
import re
from typing import Any

from build_graph_index import _digest_bytes
from graph_core import Graph, Node, load_graph, semantic_hash


def _neighbors(graph: Graph, node_id: str, direction: str) -> list[str]:
    values: set[str] = set()
    if direction in {"outgoing", "both"}:
        parent = graph.nodes[node_id].data.get("parent")
        if isinstance(parent, str):
            values.add(parent)
        values.update(target for _kind, target, scope in graph.forward_edges.get(node_id, []) if scope == "project")
    if direction in {"incoming", "both"}:
        values.update(graph.children.get(node_id, []))
        values.update(source for _kind, source, scope in graph.reverse_edges.get(node_id, []) if scope == "project")
    return sorted(value for value in values if value in graph.nodes)


def select_documents(
    graph: Graph,
    *,
    ids: list[str] | None = None,
    root: str | None = None,
    direction: str = "both",
    depth: int = 0,
) -> list[str]:
    seeds = sorted(set(ids or ([] if root is None else [root])))
    unknown = [node_id for node_id in seeds if node_id not in graph.nodes]
    if unknown:
        raise ValueError("unknown document IDs: " + ", ".join(unknown))
    selected: list[str] = []
    seen: set[str] = set()
    queue = deque((node_id, 0) for node_id in seeds)
    while queue:
        node_id, current_depth = queue.popleft()
        if node_id in seen:
            continue
        seen.add(node_id)
        selected.append(node_id)
        if current_depth < depth:
            queue.extend((neighbor, current_depth + 1) for neighbor in _neighbors(graph, node_id, direction))
    return selected


def _document(node: Node) -> dict[str, Any]:
    item_pattern = re.compile(r"^#{2,6}\s+((?:R|A|F|D|C|T|V|REV)-\d+)\b\s*(.*)$", re.MULTILINE)
    return {
        "id": node.id,
        "document_type": node.document_type,
        "title": node.data.get("title"),
        "status": node.data.get("status"),
        "scope_ref": node.data.get("scope_ref"),
        "source_path": node.relative_path,
        "source_digest": _digest_bytes(node.path.read_bytes()),
        "semantic_digest": semantic_hash(node),
        "confirmation": node.data.get("confirmation"),
        "body": node.body,
        "items": [
            {"id": match.group(1), "title": match.group(2).strip()}
            for match in item_pattern.finditer(node.body)
        ],
    }


def build_context_bundle(
    graph: Graph,
    selected_ids: list[str],
    *,
    max_documents: int,
    max_chars: int,
) -> dict[str, Any]:
    if max_documents < 1 or max_chars < 1:
        raise ValueError("max_documents and max_chars must be positive")
    documents: list[dict[str, Any]] = []
    omitted: list[dict[str, str]] = []
    used_chars = 0
    for node_id in selected_ids:
        document = _document(graph.nodes[node_id])
        size = len(document["body"])
        if len(documents) >= max_documents:
            omitted.append({"id": node_id, "reason": "max_documents"})
        elif used_chars + size > max_chars:
            omitted.append({"id": node_id, "reason": "max_chars"})
        else:
            documents.append(document)
            used_chars += size
    included = {document["id"] for document in documents}
    edges = []
    for source in sorted(included):
        parent = graph.nodes[source].data.get("parent")
        if parent in included:
            edges.append({"source": source, "target": parent, "type": "parent", "scope": "project"})
        for kind, target, scope in graph.forward_edges.get(source, []):
            if target in included:
                edges.append({"source": source, "target": target, "type": kind, "scope": scope})
    return {
        "schema_version": 1,
        "documents": documents,
        "edges": edges,
        "omitted": omitted,
        "truncated": bool(omitted),
        "selected_count": len(selected_ids),
        "included_count": len(documents),
        "used_chars": used_chars,
    }


def render_markdown(bundle: dict[str, Any]) -> str:
    parts = ["# Context Bundle", ""]
    for document in bundle["documents"]:
        parts.extend(
            [
                f"## {document['id']} — {document.get('title') or ''}",
                "",
                f"- source: `{document['source_path']}`",
                f"- digest: `{document['source_digest']}`",
                "",
                document["body"].rstrip(),
                "",
            ]
        )
    if bundle["omitted"]:
        parts.extend(["## Omitted", ""])
        parts.extend(f"- {item['id']}: {item['reason']}" for item in bundle["omitted"])
    return "\n".join(parts).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read multiple related v3 documents in one deterministic context bundle.")
    parser.add_argument("graph_root", type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--ids", nargs="+")
    selection.add_argument("--root")
    parser.add_argument("--direction", choices=("incoming", "outgoing", "both"), default="both")
    parser.add_argument("--depth", type=int, default=0)
    parser.add_argument("--max-documents", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=100_000)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    graph = load_graph(args.graph_root)
    if not graph.valid:
        print(json.dumps({"valid": False, "issues": [issue.as_dict() for issue in graph.issues]}, ensure_ascii=False))
        return 1
    try:
        selected = select_documents(
            graph,
            ids=args.ids,
            root=args.root,
            direction=args.direction,
            depth=args.depth,
        )
        bundle = build_context_bundle(
            graph,
            selected,
            max_documents=args.max_documents,
            max_chars=args.max_chars,
        )
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    if args.format == "markdown":
        print(render_markdown(bundle), end="")
    else:
        print(json.dumps({"valid": True, **bundle}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
