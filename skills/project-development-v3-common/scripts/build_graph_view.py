from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from markdown_it import MarkdownIt


TEMPLATE = Path(__file__).resolve().parents[1] / "assets/graph-view/index.template.html"
SAFE_SCHEMES = {"", "http", "https", "mailto"}


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}源无效：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}源无效：根节点必须是对象")
    return value


def load_graph(path: Path) -> dict[str, Any]:
    value = load_json(path, "图谱")
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


def _markdown_renderer() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False}).enable("table")
    default_link_open = md.renderer.rules.get("link_open")

    def safe_link(tokens, idx, options, env):
        href = tokens[idx].attrGet("href")
        if href is not None:
            if href == "#unsafe-link" or urlparse(href).scheme.lower() not in SAFE_SCHEMES:
                tokens[idx].attrSet("href", "#unsafe-link")
                tokens[idx].attrSet("data-blocked-link", "true")
        if default_link_open:
            return default_link_open(tokens, idx, options, env)
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["link_open"] = safe_link
    return md


def _headings(rendered: str) -> tuple[str, list[dict[str, str]]]:
    toc: list[dict[str, str]] = []
    counts: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        level, content = match.group(1), match.group(2)
        plain = re.sub(r"<[^>]+>", "", content)
        base = re.sub(r"[^\w\-\u4e00-\u9fff]+", "-", html.unescape(plain).lower()).strip("-") or "section"
        counts[base] = counts.get(base, 0) + 1
        anchor = base if counts[base] == 1 else f"{base}-{counts[base]}"
        toc.append({"level": level, "title": html.unescape(plain), "anchor": anchor})
        return f'<h{level} id="{html.escape(anchor)}">{content}</h{level}>'

    return re.sub(r"<h([1-6])>(.*?)</h\1>", replace, rendered, flags=re.DOTALL), toc


def project_documents(graph: dict[str, Any], documents: dict[str, Any] | None) -> dict[str, Any]:
    source = (documents or {}).get("documents", {})
    if not isinstance(source, dict):
        raise ValueError("正文源无效：documents 必须是对象")
    md = _markdown_renderer()
    projected: dict[str, Any] = {}
    for node in graph["nodes"]:
        node_id = node["id"]
        document = source.get(node_id)
        if not isinstance(document, dict):
            projected[node_id] = {"status": "missing", "message": "正文缺失：documents.json 中没有该文档。"}
            continue
        if document.get("source_digest") != node.get("source_digest"):
            projected[node_id] = {"status": "digest-mismatch", "message": "正文摘要与图索引不一致，请重建派生索引。"}
            continue
        body = document.get("body")
        if not isinstance(body, str):
            projected[node_id] = {"status": "render-error", "message": "正文渲染失败：body 不是字符串。"}
            continue
        try:
            safe_body = re.sub(r"\]\(\s*(?:javascript|data):[^\n)]*(?:\)[^\n)]*)?\)", "](#unsafe-link)", body, flags=re.IGNORECASE)
            rendered, toc = _headings(md.render(safe_body))
        except Exception as exc:
            projected[node_id] = {"status": "render-error", "message": f"正文渲染失败：{exc}"}
            continue
        projected[node_id] = {
            "status": "ready",
            "rendered_html": rendered,
            "toc": toc,
            "source_digest": document["source_digest"],
            "source_path": document.get("source_path"),
            "body_length": len(body),
        }
    return projected


def build_view(graph_path: Path, output: Path, documents_path: Path | None = None) -> str:
    graph = load_graph(graph_path)
    state = classify(graph)
    documents = load_json(documents_path, "正文") if documents_path else None
    payload = {"graph": graph, "documents": project_documents(graph, documents)}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = TEMPLATE.read_text(encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("__VIEW_DATA__", encoded).replace("__VIEW_STATE__", state), encoding="utf-8", newline="\n")
    return state


def build_error_view(output: Path, message: str) -> None:
    graph = {"nodes": [], "structural_edges": [], "relation_edges": [], "build_error": message}
    payload = json.dumps({"graph": graph, "documents": {}}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__VIEW_DATA__", payload).replace("__VIEW_STATE__", "invalid-source"), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="构建离线 SVG 项目关系画布与正文阅读页。")
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--documents", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        state = build_view(args.graph, args.output, args.documents)
    except ValueError as exc:
        build_error_view(args.output, str(exc))
        print(f"GRAPH_VIEW_BUILD_FAILED {exc}")
        return 1
    print(json.dumps({"valid": True, "state": state, "output": str(args.output)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
