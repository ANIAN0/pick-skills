from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path

from graph_core import Graph, load_graph


STRONG_RELATIONS = {
    "depends-on",
    "verifies",
    "implements",
    "researches",
    "uses-knowledge",
    "specifies",
    "prototypes",
    "evidences",
}


@dataclass(frozen=True)
class ImpactItem:
    node_id: str
    reason: str
    via: list[str]
    depth: int


class ImpactError(ValueError):
    def __init__(self, code: str, message: str, *, node_id: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.node_id = node_id

    def as_dict(self) -> dict[str, str | None]:
        return {"code": self.code, "node_id": self.node_id, "message": str(self)}


def _record(
    items: dict[str, ImpactItem],
    node_id: str,
    reason: str,
    via: list[str],
) -> None:
    candidate = ImpactItem(node_id=node_id, reason=reason, via=via, depth=len(via) - 1)
    current = items.get(node_id)
    candidate_key = (candidate.reason.startswith("report-only:"), candidate.depth, candidate.reason, candidate.via)
    current_key = (
        (current.reason.startswith("report-only:"), current.depth, current.reason, current.via)
        if current
        else None
    )
    if current_key is None or candidate_key < current_key:
        items[node_id] = candidate


def _require_valid_graph(graph: Graph, changed: str, *, allow_external_target: bool = False) -> None:
    if not graph.valid:
        raise ImpactError("GRAPH_INVALID", "source graph must pass validation before impact analysis")
    known_external_target = allow_external_target and changed in graph.reverse_edges
    if changed not in graph.nodes and not known_external_target:
        raise ImpactError("CHANGED_NODE_UNKNOWN", f"changed node does not exist: {changed}", node_id=changed)


def content_impact(graph: Graph, changed: str) -> list[ImpactItem]:
    _require_valid_graph(graph, changed, allow_external_target=True)
    items: dict[str, ImpactItem] = {}
    _record(items, changed, "changed:content", [changed])

    node = graph.nodes.get(changed)
    if node is not None:
        parent = node.data.get("parent")
        if isinstance(parent, str) and parent in graph.nodes:
            _record(items, parent, "structural:direct-parent", [changed, parent])
        for child in graph.children.get(changed, []):
            _record(items, child, "structural:direct-child", [changed, child])

    queue: deque[tuple[str, list[str]]] = deque([(changed, [changed])])
    expanded = {changed}
    while queue:
        target, path = queue.popleft()
        for relation_type, source, _scope in graph.reverse_edges.get(target, []):
            next_path = path + [source]
            if relation_type in STRONG_RELATIONS:
                _record(items, source, f"reverse:{relation_type}", next_path)
                if source not in expanded:
                    expanded.add(source)
                    queue.append((source, next_path))
            elif relation_type == "references" and target == changed:
                _record(items, source, "report-only:references", next_path)

    return sorted(items.values(), key=lambda item: (item.depth, item.node_id, item.reason, item.via))


def move_impact(
    graph: Graph,
    changed: str,
    *,
    old_parent: str | None,
    new_parent: str | None,
) -> list[ImpactItem]:
    _require_valid_graph(graph, changed)
    for label, parent in (("old_parent", old_parent), ("new_parent", new_parent)):
        if parent is not None and parent not in graph.nodes:
            raise ImpactError("MOVE_PARENT_UNKNOWN", f"{label} does not exist: {parent}", node_id=parent)

    items: dict[str, ImpactItem] = {}
    _record(items, changed, "changed:move", [changed])
    if old_parent is not None:
        _record(items, old_parent, "move:old-parent", [changed, old_parent])
    if new_parent is not None:
        _record(items, new_parent, "move:new-parent", [changed, new_parent])
    for child in graph.children.get(changed, []):
        _record(items, child, "move:direct-child", [changed, child])
    return sorted(items.values(), key=lambda item: (item.depth, item.node_id, item.reason, item.via))


def delete_impact(graph: Graph, changed: str) -> list[ImpactItem]:
    _require_valid_graph(graph, changed)
    children = graph.children.get(changed, [])
    incoming = graph.reverse_edges.get(changed, [])
    if children or incoming:
        details: list[str] = []
        if children:
            details.append("children=" + ",".join(children))
        if incoming:
            details.append(
                "incoming=" + ",".join(f"{source}:{relation_type}" for relation_type, source, _scope in incoming)
            )
        raise ImpactError(
            "DELETE_BLOCKED",
            "node has structural children or incoming relations; " + "; ".join(details),
            node_id=changed,
        )
    items: dict[str, ImpactItem] = {}
    _record(items, changed, "changed:delete", [changed])
    parent = graph.nodes[changed].data.get("parent")
    if isinstance(parent, str) and parent in graph.nodes:
        _record(items, parent, "delete:direct-parent", [changed, parent])
    return sorted(items.values(), key=lambda item: (item.depth, item.node_id, item.reason, item.via))


def compute_impact(
    graph: Graph,
    changed: str,
    change_kind: str,
    *,
    old_parent: str | None = None,
    new_parent: str | None = None,
) -> list[ImpactItem]:
    if change_kind == "content":
        return content_impact(graph, changed)
    if change_kind == "move":
        return move_impact(graph, changed, old_parent=old_parent, new_parent=new_parent)
    if change_kind == "delete":
        return delete_impact(graph, changed)
    raise ImpactError("CHANGE_KIND_INVALID", f"unknown change kind: {change_kind}", node_id=changed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute local project-development v3 graph impact without modifying source files.")
    parser.add_argument("graph_root", type=Path)
    parser.add_argument("--changed", required=True, help="Stable ID of the changed node")
    parser.add_argument("--change-kind", required=True, choices=("content", "move", "delete"))
    parser.add_argument("--old-parent")
    parser.add_argument("--new-parent")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    graph = load_graph(args.graph_root)
    try:
        impacts = compute_impact(
            graph,
            args.changed,
            args.change_kind,
            old_parent=args.old_parent,
            new_parent=args.new_parent,
        )
    except ImpactError as exc:
        result = {"valid": False, "change_kind": args.change_kind, "changed": args.changed, "impacts": [], "error": exc.as_dict()}
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print(f"{exc.code} {exc.node_id or ''} {exc}")
        return 1

    result = {
        "valid": True,
        "change_kind": args.change_kind,
        "changed": args.changed,
        "impacts": [asdict(item) for item in impacts],
        "error": None,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        for item in impacts:
            print(f"{item.node_id} depth={item.depth} reason={item.reason} via={' -> '.join(item.via)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
