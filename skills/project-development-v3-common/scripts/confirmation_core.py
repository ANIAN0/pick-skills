from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from graph_core import Graph, load_graph, semantic_hash


GATES = {"G-REQ", "G-DESIGN", "G-PLAN", "G-ACCEPT"}


def scope_hash(graph: Graph, gate: str, scope_ref: dict[str, Any], document_ids: list[str]) -> str:
    if gate not in GATES:
        raise ValueError(f"unknown gate: {gate}")
    missing = sorted(set(document_ids) - graph.nodes.keys())
    if missing:
        raise ValueError("unknown documents: " + ", ".join(missing))
    payload = {
        "gate": gate,
        "scope_ref": scope_ref,
        "documents": [(node_id, semantic_hash(graph.nodes[node_id])) for node_id in sorted(set(document_ids))],
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def confirmation_file(graph_root: Path, gate: str, scope_ref: dict[str, Any]) -> Path:
    document = re.sub(r"[^A-Za-z0-9-]", "-", str(scope_ref.get("document", "unknown")))
    item = re.sub(r"[^A-Za-z0-9-]", "-", str(scope_ref.get("item") or "all"))
    root = graph_root / "graph" if (graph_root / "graph").is_dir() else graph_root
    return root / ".derived" / "confirmations" / f"{gate}-{document}-{item}.json"


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


def record_confirmation(
    graph_root: Path,
    gate: str,
    scope_ref: dict[str, Any],
    document_ids: list[str],
    confirmed_by: str,
) -> dict[str, Any]:
    identity = confirmed_by.strip()
    if not identity or identity.lower() in {"unattended", "automatic", "agent"}:
        raise ValueError("a real user confirmation identity is required")
    graph = load_graph(graph_root)
    if not graph.valid:
        raise ValueError("graph must be valid before confirmation")
    value = {
        "gate": gate,
        "scope_ref": scope_ref,
        "document_ids": sorted(set(document_ids)),
        "document_hashes": {node_id: semantic_hash(graph.nodes[node_id]) for node_id in sorted(set(document_ids))},
        "scope_hash": scope_hash(graph, gate, scope_ref, document_ids),
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "confirmed_by": identity,
    }
    _atomic_json(confirmation_file(graph_root, gate, scope_ref), value)
    return value


def confirmation_covers_document(graph_root: Path, gate: str, scope_ref: dict[str, Any], document_id: str) -> bool:
    """Return true when the latest package explicitly confirmed this unchanged document."""
    graph = load_graph(graph_root)
    node = graph.nodes.get(document_id)
    path = confirmation_file(graph_root, gate, scope_ref)
    if not graph.valid or not node or not path.is_file():
        return False
    stored = json.loads(path.read_text(encoding="utf-8"))
    return stored.get("document_hashes", {}).get(document_id) == semantic_hash(node)


def confirmation_status(
    graph_root: Path,
    gate: str,
    scope_ref: dict[str, Any],
    document_ids: list[str],
) -> dict[str, Any]:
    graph = load_graph(graph_root)
    path = confirmation_file(graph_root, gate, scope_ref)
    if not graph.valid:
        return {"valid": False, "reason": "graph_invalid", "path": str(path)}
    if not path.is_file():
        return {"valid": False, "reason": "missing", "path": str(path)}
    stored = json.loads(path.read_text(encoding="utf-8"))
    current = scope_hash(graph, gate, scope_ref, document_ids)
    return {
        "valid": stored.get("scope_hash") == current,
        "reason": "valid" if stored.get("scope_hash") == current else "stale",
        "path": str(path),
        "stored_hash": stored.get("scope_hash"),
        "current_hash": current,
        "confirmed_by": stored.get("confirmed_by"),
    }
