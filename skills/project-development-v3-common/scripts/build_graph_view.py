from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "graph-view" / "index.template.html"


def load_graph(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"图谱源无效：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("图谱源无效：根节点必须是对象")
    for field in ("nodes", "structural_edges", "relation_edges"):
        if not isinstance(value.get(field), list):
            raise ValueError(f"图谱源无效：{field} 必须是数组")
    required = {"id", "status", "source_path"}
    for position, node in enumerate(value["nodes"]):
        if not isinstance(node, dict) or not required <= node.keys():
            raise ValueError(f"图谱源无效：第 {position} 个节点缺少 id/status/source_path")
    return value


def classify(graph: dict[str, Any]) -> str:
    if not graph["nodes"]:
        return "empty"
    expected = graph.get("current_source_digest")
    if expected is not None and expected != graph.get("source_digest"):
        return "stale-index"
    ids = {node["id"] for node in graph["nodes"]}
    edges = graph["structural_edges"] + graph["relation_edges"]
    if any(edge.get("source") not in ids or edge.get("target") not in ids for edge in edges):
        return "missing-detail"
    return "normal"


def build_view(graph_path: Path, output: Path) -> str:
    graph = load_graph(graph_path)
    state = classify(graph)
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("__GRAPH_DATA__", payload).replace("__VIEW_STATE__", state)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="\n")
    return state


def build_error_view(output: Path, message: str) -> None:
    graph = {"nodes": [], "structural_edges": [], "relation_edges": [], "build_error": message}
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("__GRAPH_DATA__", payload).replace("__VIEW_STATE__", "invalid-source")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="构建独立、只读的项目图谱页面。")
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        state = build_view(args.graph, args.output)
    except ValueError as exc:
        build_error_view(args.output, str(exc))
        print(f"GRAPH_VIEW_BUILD_FAILED {exc}")
        return 1
    print(json.dumps({"valid": True, "state": state, "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
