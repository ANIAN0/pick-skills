from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Any

import yaml


COMMON = Path(__file__).resolve().parents[2] / "project-development-v3-common/scripts"
if str(COMMON) not in sys.path:
    sys.path.insert(0, str(COMMON))

from compute_impact import compute_impact  # noqa: E402
from graph_core import load_graph, semantic_hash  # noqa: E402


def _write(path: Path, data: dict[str, Any]) -> None:
    body = f"# {data['title']}\n\n" + "\n\n".join(
        f"## {finding['id']} {finding['title']}\n\n- 严重度：{finding['severity']}\n- 责任：{finding['responsible_document']}#{finding.get('responsible_item') or ''}\n- 状态：{finding['status']}"
        for finding in data["findings"]
    ) + "\n"
    path.write_text("---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n" + body, encoding="utf-8", newline="\n")


def create_review_report(project_root: Path, responsible_document: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    graph = load_graph(project_root)
    responsible = graph.nodes.get(responsible_document)
    if not responsible:
        raise ValueError(f"responsible document not found: {responsible_document}")
    impacts = [item.__dict__ for item in compute_impact(graph, responsible_document, "content")]
    actionable = [item for item in impacts if not item["reason"].startswith("report-only:")]
    normalized = []
    for index, finding in enumerate(findings, 1):
        normalized.append({
            "id": finding.get("id", f"REV-{index:03d}"),
            "title": finding["title"],
            "severity": finding["severity"],
            "responsible_document": responsible_document,
            "responsible_item": finding.get("responsible_item"),
            "owner_skill": finding["owner_skill"],
            "impact_set": impacts,
            "review_scope": [item["node_id"] for item in actionable],
            "close_conditions": finding.get("close_conditions", []),
            "close_evidence": [],
            "responsible_hash_at_open": semantic_hash(responsible),
            "status": "open",
        })
    report_id = "DOC-REVIEW-" + responsible_document.replace("DOC-", "")
    data = {
        "type": "project-development/document-node",
        "id": report_id,
        "document_type": "review-report",
        "title": f"{responsible.data['title']} 评审报告",
        "status": "blocked" if any(item["severity"] in {"BLOCKER", "HIGH"} for item in normalized) else "draft",
        "revision": 1,
        "parent": responsible_document,
        "scope_ref": responsible.data.get("scope_ref"),
        "relations": [{"type": "reviews", "target": responsible_document, "scope": "project"}],
        "findings": normalized,
    }
    directory = responsible.path.parent / "supporting"
    directory.mkdir(exist_ok=True)
    path = directory / "review-report.md"
    _write(path, data)
    return {"status": data["status"], "document": report_id, "path": str(path), "findings": normalized}


def close_finding(project_root: Path, report_id: str, finding_id: str, evidence_paths: list[str]) -> dict[str, Any]:
    graph = load_graph(project_root)
    report = graph.nodes.get(report_id)
    if not report or report.document_type != "review-report":
        raise ValueError("review report not found")
    finding = next((item for item in report.data["findings"] if item["id"] == finding_id), None)
    if not finding:
        raise ValueError("finding not found")
    missing = [path for path in evidence_paths if not (project_root / path).is_file()]
    if missing:
        return {"status": "blocked", "reason": "close_evidence_missing", "missing": missing}
    if not finding.get("close_conditions"):
        return {"status": "blocked", "reason": "close_conditions_missing"}
    current = load_graph(project_root)
    responsible = current.nodes.get(finding["responsible_document"])
    if not responsible or semantic_hash(responsible) == finding.get("responsible_hash_at_open"):
        return {"status": "blocked", "reason": "responsible_document_unchanged"}
    impact = [item.__dict__ for item in compute_impact(current, finding["responsible_document"], "content")]
    review_scope = [item["node_id"] for item in impact if not item["reason"].startswith("report-only:")]
    evidence_values = []
    for relative in evidence_paths:
        try:
            value = json.loads((project_root / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"status": "blocked", "reason": "close_evidence_invalid", "path": relative}
        if value.get("result") != "passed" or value.get("finding_id") != finding_id:
            return {"status": "blocked", "reason": "close_evidence_not_passed", "path": relative}
        if not set(review_scope) <= set(value.get("reviewed_documents") or []):
            return {"status": "blocked", "reason": "review_scope_incomplete", "path": relative}
        evidence_values.append(value)
    finding["impact_set"] = impact
    finding["review_scope"] = review_scope
    finding["close_evidence"] = evidence_paths
    finding["close_evidence_records"] = evidence_values
    finding["status"] = "closed"
    report.data["status"] = "confirmed" if all(item["status"] == "closed" or item["severity"] not in {"BLOCKER", "HIGH"} for item in report.data["findings"]) else "blocked"
    _write(report.path, report.data)
    return {"status": "closed", "finding": finding, "report_status": report.data["status"]}
