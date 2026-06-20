from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


COMMON = Path(__file__).resolve().parents[2] / "project-development-v3-common/scripts"
if str(COMMON) not in sys.path:
    sys.path.insert(0, str(COMMON))

from confirmation_core import confirmation_status, record_confirmation  # noqa: E402
from document_io import create_document  # noqa: E402
from graph_core import load_graph, semantic_hash  # noqa: E402


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result:
        raise ValueError("feature slug must contain ASCII letters or digits")
    return result


def _scope_directory(requirement_path: Path, scope: dict[str, Any]) -> Path:
    item = scope.get("item")
    if item is None:
        return requirement_path.parent
    return requirement_path.parent / "features" / f"{item}-{_slug(scope['slug'])}"


def _body(scope: dict[str, Any]) -> str:
    parts = [f"# {scope['title']}", ""]
    for item in scope.get("decisions", []):
        parts.extend([f"## {item['id']} {item['title']}", "", item.get("description", ""), ""])
    for item in scope.get("changes", []):
        parts.extend([f"## {item['id']} {item['title']}", "", item.get("description", ""), ""])
    for item in scope.get("verifications", []):
        parts.extend([f"## {item['id']} {item['title']}", "", item.get("description", ""), ""])
    return "\n".join(parts).rstrip() + "\n"


def generate_tech_design(
    project_root: Path,
    handoff: dict[str, Any],
) -> dict[str, Any]:
    requirements_scope = handoff["requirements_scope_ref"]
    input_ids = handoff["requirements_documents"]
    upstream = confirmation_status(project_root, "G-REQ", requirements_scope, input_ids)
    if not upstream["valid"]:
        return {"status": "blocked", "reason": "g_req_" + upstream["reason"]}
    graph = load_graph(project_root)
    requested = handoff["scopes"]
    feature_documents = {scope["document"] for scope in requested if scope.get("item")}
    if any(scope.get("item") is None and scope["document"] in feature_documents for scope in requested):
        raise ValueError("cannot generate parent and feature tech designs for the same requirements scope")
    created: list[str] = []
    design_ids: list[str] = []
    confirmation_packages: list[dict[str, Any]] = []
    input_hashes = {node_id: semantic_hash(graph.nodes[node_id]) for node_id in input_ids}
    for scope in requested:
        requirement = graph.nodes.get(scope["document"])
        if not requirement or requirement.document_type != "requirements":
            raise ValueError(f"requirements document not found: {scope['document']}")
        directory = _scope_directory(requirement.path, scope)
        suffix = scope.get("item") or scope["document"].replace("DOC-REQ-", "")
        design_id = f"DOC-TECH-{suffix}"
        data = {
            "type": "project-development/document-node",
            "id": design_id,
            "document_type": "tech-design",
            "title": scope["title"],
            "status": "draft",
            "revision": 1,
            "parent": scope["document"],
            "scope_ref": {"document": scope["document"], "item": scope.get("item")},
            "relations": [{"type": "derives-from", "target": scope["document"], "scope": "project"}],
            "input_confirmation_hashes": input_hashes,
            "knowledge_refs": handoff.get("knowledge_refs", []),
            "deliverable": handoff["deliverable"],
        }
        path = directory / "tech-design.md"
        create_document(path, data, _body(scope))
        created.append(str(path))
        design_ids.append(design_id)
        package_scope = {"document": scope["document"], "item": scope.get("item")}
        package_ids = input_ids + [design_id]
        confirmation_packages.append({"scope_ref": package_scope, "document_ids": package_ids, "confirmation": confirmation_status(project_root, "G-DESIGN", package_scope, package_ids)})
    all_valid = all(package["confirmation"]["valid"] for package in confirmation_packages)
    result = {"status": "ready_for_planning" if all_valid else "awaiting_g_design", "created": created, "documents": design_ids, "confirmation_packages": confirmation_packages, "deliverable": handoff["deliverable"]}
    if len(confirmation_packages) == 1:
        result.update({"package_document_ids": confirmation_packages[0]["document_ids"], "scope_ref": confirmation_packages[0]["scope_ref"], "confirmation": confirmation_packages[0]["confirmation"]})
    return result
