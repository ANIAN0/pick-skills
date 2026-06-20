from __future__ import annotations

import argparse
import json
from pathlib import Path

from graph_core import load_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a project-development v3 hierarchical Markdown graph without modifying it.")
    parser.add_argument(
        "graph_root",
        type=Path,
        help="Project or graph root containing stories/; legacy nodes/ remains read-only compatible",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit one JSON result object")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    graph = load_graph(args.graph_root)
    result = graph.result()
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"nodes={result['node_count']} edges={result['edge_count']} valid={str(result['valid']).lower()}")
        for issue in graph.issues:
            location = issue.file
            if issue.node_id:
                location += f":{issue.node_id}"
            if issue.field:
                location += f":{issue.field}"
            print(f"{issue.code} {location} {issue.message}")
    return 0 if graph.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
