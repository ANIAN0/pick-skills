from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from graph_core import Graph, load_graph, semantic_hash


def _digest_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def source_digest(graph: Graph) -> str:
    digest = hashlib.sha256()
    for node in sorted(graph.all_nodes, key=lambda item: item.relative_path):
        digest.update(node.relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(node.path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def project_graph(graph: Graph, *, generated_at: str) -> dict[str, Any]:
    digest = source_digest(graph)
    nodes = []
    structural_edges = []
    relation_edges = []
    for node in sorted(graph.all_nodes, key=lambda item: (item.id or "", item.relative_path)):
        if not node.id:
            continue
        relations = node.data.get("relations", [])
        node_value = {
                "id": node.id,
                "document_type": node.document_type,
                "title": node.data.get("title"),
                "status": node.data.get("status"),
                "parent": node.data.get("parent"),
                "revision": node.data.get("revision"),
                "relations": relations if isinstance(relations, list) else [],
                "scope_ref": node.data.get("scope_ref"),
                "source_path": node.relative_path,
                "source_digest": _digest_bytes(node.path.read_bytes()),
            }
        if node.node_type is not None:
            node_value["node_type"] = node.node_type
        nodes.append(node_value)
        parent = node.data.get("parent")
        if isinstance(parent, str):
            structural_edges.append({"source": node.id, "target": parent, "type": "parent"})
        for relation_type, target, scope in graph.forward_edges.get(node.id, []):
            relation_edges.append(
                {"source": node.id, "target": target, "type": relation_type, "scope": scope}
            )
    structural_edges.sort(key=lambda edge: (edge["source"], edge["target"]))
    relation_edges.sort(key=lambda edge: (edge["source"], edge["type"], edge["target"], edge["scope"]))
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "source_digest": digest,
        "node_count": len(nodes),
        "edge_count": len(structural_edges) + len(relation_edges),
        "nodes": nodes,
        "structural_edges": structural_edges,
        "relation_edges": relation_edges,
    }


def project_documents(graph: Graph, *, generated_at: str) -> dict[str, Any]:
    digest = source_digest(graph)
    documents: dict[str, dict[str, Any]] = {}
    item_pattern = re.compile(r"^#{2,6}\s+((?:R|A|F|D|C|T|V|REV)-\d+)\b\s*(.*)$", re.MULTILINE)
    for node in sorted(graph.all_nodes, key=lambda item: (item.id or "", item.relative_path)):
        if not node.id:
            continue
        source_bytes = node.path.read_bytes()
        documents[node.id] = {
            "id": node.id,
            "document_type": node.document_type,
            "title": node.data.get("title"),
            "status": node.data.get("status"),
            "scope_ref": node.data.get("scope_ref"),
            "source_path": node.relative_path,
            "source_digest": _digest_bytes(source_bytes),
            "semantic_digest": semantic_hash(node),
            "body": node.body,
            "items": [
                {"id": match.group(1), "title": match.group(2).strip()}
                for match in item_pattern.finditer(node.body)
            ],
            "confirmation": node.data.get("confirmation"),
        }
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "source_digest": digest,
        "document_count": len(documents),
        "documents": documents,
    }


def project_backlinks(graph: Graph, *, generated_at: str) -> dict[str, Any]:
    digest = source_digest(graph)
    backlinks: dict[str, list[dict[str, Any]]] = {}
    children: dict[str, list[dict[str, Any]]] = {}
    for target, edges in sorted(graph.reverse_edges.items()):
        for relation_type, source, scope in edges:
            source_node = graph.nodes.get(source)
            backlinks.setdefault(target, []).append(
                {
                    "source": source,
                    "type": relation_type,
                    "scope": scope,
                    "source_path": source_node.relative_path if source_node else None,
                    "status": source_node.data.get("status") if source_node else None,
                }
            )
    for parent, child_ids in sorted(graph.children.items()):
        children[parent] = [
            {
                "id": child_id,
                "source_path": graph.nodes[child_id].relative_path,
                "status": graph.nodes[child_id].data.get("status"),
            }
            for child_id in child_ids
        ]
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "source_digest": digest,
        "backlinks": backlinks,
        "children": children,
    }


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def build_index(graph_root: Path, output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    graph = load_graph(graph_root)
    if not graph.valid:
        issue_summary = "; ".join(f"{issue.code}:{issue.file}:{issue.field or ''}" for issue in graph.issues)
        raise ValueError("source graph is invalid: " + issue_summary)
    generated_at = datetime.now(timezone.utc).isoformat()
    graph_value = project_graph(graph, generated_at=generated_at)
    backlinks_value = project_backlinks(graph, generated_at=generated_at)
    documents_value = project_documents(graph, generated_at=generated_at)
    _atomic_json(output / "graph.json", graph_value)
    _atomic_json(output / "backlinks.json", backlinks_value)
    _atomic_json(output / "documents.json", documents_value)
    return graph_value, backlinks_value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build disposable JSON indexes from a valid project-development v3 graph.")
    parser.add_argument("graph_root", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Derived output directory")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        graph_value, _backlinks_value = build_index(args.graph_root, args.output)
    except (OSError, ValueError) as exc:
        print(f"INDEX_BUILD_FAILED {exc}")
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "graph": str(args.output / "graph.json"),
                "backlinks": str(args.output / "backlinks.json"),
                "documents": str(args.output / "documents.json"),
                "node_count": graph_value["node_count"],
                "edge_count": graph_value["edge_count"],
                "source_digest": graph_value["source_digest"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
