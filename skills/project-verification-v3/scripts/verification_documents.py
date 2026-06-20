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
from graph_core import load_graph  # noqa: E402


def _write(path: Path, data: dict[str, Any], body: str) -> None:
    path.write_text("---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n" + body, encoding="utf-8", newline="\n")


def create_test_plans(project_root: Path, plans: list[dict[str, Any]]) -> dict[str, Any]:
    graph = load_graph(project_root)
    created = []
    ids = []
    for plan in plans:
        tech = graph.nodes.get(plan["tech_design_id"])
        if not tech or tech.document_type != "tech-design":
            raise ValueError(f"tech design not found: {plan['tech_design_id']}")
        verifications = plan.get("verifications") or []
        verification_ids = [item.get("id") for item in verifications]
        if not verification_ids or None in verification_ids or len(verification_ids) != len(set(verification_ids)):
            raise ValueError("verification ids must be non-empty and unique")
        if any(not item.get("positive") or not item.get("negative") for item in verifications):
            raise ValueError("every verification requires positive and negative cases")
        test_id = tech.id.replace("DOC-TECH-", "DOC-TEST-")
        data = {
            "type": "project-development/document-node",
            "id": test_id,
            "document_type": "test-plan",
            "title": plan["title"],
            "status": "draft",
            "revision": 1,
            "parent": tech.id,
            "scope_ref": tech.data["scope_ref"],
            "relations": [{"type": "tests", "target": tech.id, "scope": "project"}],
            "verifications": plan["verifications"],
        }
        body = f"# {plan['title']}\n\n" + "\n\n".join(f"## {item['id']} {item['title']}\n\n- 正向：{item.get('positive', '')}\n- 负向：{item.get('negative', '')}\n- 预期资产：{item.get('artifact', '')}" for item in plan["verifications"]) + "\n"
        path = tech.path.parent / "test-plan.md"
        create_document(path, data, body)
        created.append(str(path))
        ids.append(test_id)
    return {"status": "test_plans_ready", "documents": ids, "created": created}


def finalize_verification(
    project_root: Path,
    *,
    task_list_id: str,
    test_plan_id: str,
    package_document_ids: list[str],
) -> dict[str, Any]:
    graph = load_graph(project_root)
    task_list = graph.nodes.get(task_list_id)
    test_plan = graph.nodes.get(test_plan_id)
    if not task_list or task_list.document_type != "task-list" or not test_plan or test_plan.document_type != "test-plan":
        raise ValueError("task list and test plan are required")
    if task_list.data.get("scope_ref") != test_plan.data.get("scope_ref"):
        raise ValueError("task list and test plan scope_ref mismatch")
    records = task_list.data.get("execution_records") or []
    verification_ids = [item["id"] for item in test_plan.data.get("verifications", [])]
    results = []
    all_passed = True
    for verification_id in verification_ids:
        matching = [record for record in records if verification_id in record.get("verification_ids", [])]
        passed_cases = {
            record.get("verification_case")
            for record in matching
            if record.get("result") == "passed"
            and record.get("exit_code") is not None
            and record.get("artifact_paths") is not None
            and all((project_root / path).is_file() for path in record["artifact_paths"])
        }
        required_cases = {"positive", "negative"}
        result = "passed" if required_cases <= passed_cases else "failed"
        all_passed = all_passed and result == "passed"
        results.append({"verification_id": verification_id, "result": result, "required_cases": sorted(required_cases), "passed_cases": sorted(value for value in passed_cases if value), "execution_records": matching})
    report_id = test_plan.id.replace("DOC-TEST-", "DOC-VERIFY-")
    data = {
        "type": "project-development/document-node",
        "id": report_id,
        "document_type": "verification-report",
        "title": test_plan.data["title"].replace("测试计划", "验证报告"),
        "status": "ready" if all_passed else "blocked",
        "revision": 1,
        "parent": test_plan.id,
        "scope_ref": test_plan.data["scope_ref"],
        "relations": [{"type": "verifies", "target": test_plan.id, "scope": "project"}],
        "results": results,
        "acceptance": "passed" if all_passed else "failed",
    }
    body = f"# {data['title']}\n\n" + "\n".join(f"- {item['verification_id']}: {item['result']}" for item in results) + "\n"
    path = test_plan.path.parent / "verification-report.md"
    _write(path, data, body)
    if not all_passed:
        return {"status": "failed", "document": report_id, "results": results, "created": str(path)}
    return {"status": "awaiting_g_accept", "document": report_id, "results": results, "created": str(path), "package_document_ids": package_document_ids + [report_id]}


def accept_verification(project_root: Path, report_id: str, package_document_ids: list[str], *, confirmed_by: str) -> dict[str, Any]:
    """Record G-ACCEPT only as a separate, explicit user-confirmation action."""
    graph = load_graph(project_root)
    report = graph.nodes.get(report_id)
    if not report or report.document_type != "verification-report":
        raise ValueError("verification report not found")
    if report.data.get("acceptance") != "passed":
        return {"status": "blocked", "reason": "verification_not_passed"}
    package = sorted(set(package_document_ids + [report_id]))
    confirmation = record_confirmation(project_root, "G-ACCEPT", report.data["scope_ref"], package, confirmed_by)
    status = confirmation_status(project_root, "G-ACCEPT", report.data["scope_ref"], package)
    if not status["valid"]:
        return {"status": "blocked", "reason": "g_accept_invalid"}
    report.data["status"] = "done"
    _write(report.path, report.data, report.body)
    return {"status": "accepted", "document": report_id, "confirmation": confirmation}
