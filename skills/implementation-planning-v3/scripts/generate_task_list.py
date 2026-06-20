from __future__ import annotations

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


def _approved(task: dict[str, Any]) -> bool:
    approval = task.get("approval")
    return isinstance(approval, dict) and approval.get("approved") is True and bool(approval.get("approved_by")) and bool(approval.get("approved_at"))


def _guarded(task: dict[str, Any]) -> bool:
    return task.get("criticality") == "core" or task.get("infrastructure") is True


def _body(title: str, tasks: list[dict[str, Any]]) -> str:
    parts = [f"# {title}", ""]
    for task in tasks:
        parts.extend([f"## {task['id']} {task['title']}", ""])
        for key in ("criticality", "infrastructure", "risk", "executor_requirement", "executor_profile", "approval", "depends_on", "change_ids", "verification_ids", "target_files", "assertions"):
            parts.append(f"- {key}: `{yaml.safe_dump(task.get(key), allow_unicode=True, default_flow_style=True).strip()}`")
        parts.extend(["", task.get("steps", ""), ""])
    return "\n".join(parts).rstrip() + "\n"


def _validate_task_graph(tasks: list[dict[str, Any]]) -> None:
    by_id = {task.get("id"): task for task in tasks}
    if None in by_id or len(by_id) != len(tasks):
        raise ValueError("task ids must be non-empty and unique")
    for task in tasks:
        for field in ("change_ids", "verification_ids", "target_files", "assertions", "steps"):
            if not task.get(field):
                raise ValueError(f"{task['id']} missing required field: {field}")
        unknown = set(task.get("depends_on") or []) - by_id.keys()
        if unknown:
            raise ValueError(f"{task['id']} has unknown dependencies: {sorted(unknown)}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError(f"task dependency cycle: {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in by_id[task_id].get("depends_on") or []:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in by_id:
        visit(task_id)


def generate_task_lists(project_root: Path, handoff: dict[str, Any]) -> dict[str, Any]:
    scope = handoff["design_scope_ref"]
    package_ids = handoff["design_package_documents"]
    upstream = confirmation_status(project_root, "G-DESIGN", scope, package_ids)
    if not upstream["valid"]:
        return {"status": "blocked", "reason": "g_design_" + upstream["reason"]}
    graph = load_graph(project_root)
    test_plan_ids = list(handoff.get("test_plan_documents") or [])
    if not test_plan_ids:
        return {"status": "blocked", "reason": "test_plan_documents_missing"}
    for test_id in test_plan_ids:
        test_plan = graph.nodes.get(test_id)
        if not test_plan or test_plan.document_type != "test-plan" or test_plan.data.get("scope_ref") != scope:
            return {"status": "blocked", "reason": "test_plan_scope_mismatch", "document": test_id}
    created: list[str] = []
    task_documents: list[str] = []
    blocked_tasks: list[str] = []
    for plan in handoff["plans"]:
        _validate_task_graph(plan["tasks"])
        design = graph.nodes.get(plan["tech_design_id"])
        if not design or design.document_type != "tech-design":
            raise ValueError(f"tech design not found: {plan['tech_design_id']}")
        plan_blocked = [task["id"] for task in plan["tasks"] if _guarded(task) and task.get("executor_profile") != "senior" and not _approved(task)]
        blocked_tasks.extend(plan_blocked)
        task_doc_id = design.id.replace("DOC-TECH-", "DOC-TASKS-")
        data = {
            "type": "project-development/document-node",
            "id": task_doc_id,
            "document_type": "task-list",
            "title": plan["title"],
            "status": "blocked" if plan_blocked else "draft",
            "revision": 1,
            "parent": design.id,
            "scope_ref": design.data["scope_ref"],
            "relations": [{"type": "plans", "target": design.id, "scope": "project"}],
            "input_confirmation_hashes": {design.id: semantic_hash(design)},
            "deliverable": handoff["deliverable"],
            "tasks": plan["tasks"],
            "execution_records": [],
            "root_causes": [],
        }
        path = design.path.parent / "task-list.md"
        create_document(path, data, _body(plan["title"], plan["tasks"]))
        created.append(str(path))
        task_documents.append(task_doc_id)
    if blocked_tasks:
        return {"status": "blocked", "reason": "executor_gate", "blocked_tasks": sorted(blocked_tasks), "created": created}
    all_ids = package_ids + task_documents + test_plan_ids
    status = confirmation_status(project_root, "G-PLAN", scope, all_ids)
    return {"status": "ready_for_execution" if status["valid"] else "awaiting_g_plan", "documents": task_documents, "package_document_ids": all_ids, "created": created, "scope_ref": scope, "confirmation": status, "deliverable": handoff["deliverable"]}
