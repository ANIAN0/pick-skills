from __future__ import annotations

import json
import hashlib
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


COMMON = Path(__file__).resolve().parents[2] / "project-development-v3-common/scripts"
if str(COMMON) not in sys.path:
    sys.path.insert(0, str(COMMON))

from confirmation_core import confirmation_status  # noqa: E402
from graph_core import FRONTMATTER_RE, load_graph  # noqa: E402


REQUIRED_RECORD_FIELDS = {"task_id", "verification_ids", "scope_ref", "command", "exit_code", "stdout", "stderr", "timestamp", "executor", "result", "artifact_paths"}


def validate_execution_record(record: dict[str, Any]) -> list[str]:
    errors = [f"missing:{field}" for field in sorted(REQUIRED_RECORD_FIELDS - record.keys())]
    if record.get("result") not in {"passed", "failed", "blocked", "not_verified"}:
        errors.append("result:invalid")
    if record.get("result") == "passed":
        if not isinstance(record.get("command"), str) or not record["command"].strip():
            errors.append("command:required")
        if record.get("exit_code") != 0:
            errors.append("exit_code:must_be_zero")
        if not isinstance(record.get("artifact_paths"), list) or not record["artifact_paths"]:
            errors.append("artifact_paths:required")
        if not str(record.get("executor") or "").strip():
            errors.append("executor:required")
        if not str(record.get("timestamp") or "").strip():
            errors.append("timestamp:required")
    return errors


def _write_node(path: Path, data: dict[str, Any], body: str) -> None:
    path.write_text("---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n" + body, encoding="utf-8", newline="\n")


def _approval_valid(task: dict[str, Any]) -> bool:
    approval = task.get("approval")
    return isinstance(approval, dict) and approval.get("approved") is True and bool(approval.get("approved_by")) and bool(approval.get("approved_at"))


def _fingerprint(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _task_map(tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for task in tasks:
        task_id = str(task.get("id") or "")
        if not task_id or task_id in result:
            raise ValueError(f"invalid or duplicate task id: {task_id!r}")
        result[task_id] = task
    for task in tasks:
        unknown = sorted(set(task.get("depends_on") or []) - result.keys())
        if unknown:
            raise ValueError(f"{task['id']} has unknown dependencies: {', '.join(unknown)}")
    return result


def _assertions_pass(project_root: Path, task: dict[str, Any]) -> tuple[bool, list[str]]:
    assertions = task.get("assertions") or {}
    targets = [project_root / value for value in task.get("target_files") or []]
    errors: list[str] = []
    for value in assertions.get("must_appear") or []:
        direct = project_root / value
        if not direct.exists() and not any(path.is_file() and value in path.read_text(encoding="utf-8", errors="replace") for path in targets):
            errors.append(f"must_appear:{value}")
    for value in assertions.get("must_disappear") or []:
        direct = project_root / value
        if direct.exists() or any(path.is_file() and value in path.read_text(encoding="utf-8", errors="replace") for path in targets):
            errors.append(f"must_disappear:{value}")
    for value in assertions.get("must_persist") or []:
        if not (project_root / value).exists():
            errors.append(f"must_persist:{value}")
    for item in assertions.get("must_propagate") or []:
        if isinstance(item, dict):
            value = str(item.get("value") or "")
            paths = [project_root / path for path in item.get("paths") or []]
            if not value or not paths or any(not path.is_file() or value not in path.read_text(encoding="utf-8", errors="replace") for path in paths):
                errors.append(f"must_propagate:{value or 'invalid'}")
        else:
            errors.append(f"must_propagate:invalid:{item}")
    return not errors, errors


def _run_verification_cases(project_root: Path, task: dict[str, Any], executor: str, scope: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in task.get("verification_commands") or []:
        command = case.get("command")
        if case.get("case") not in {"positive", "negative"} or not case.get("verification_id") or not isinstance(command, list) or not command:
            continue
        completed = subprocess.run(command, cwd=project_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, shell=False)
        expected = int(case.get("expected_exit_code", 0))
        artifacts = [project_root / value for value in case.get("artifact_paths") or []]
        artifacts_ok = all(path.is_file() for path in artifacts)
        result = "passed" if completed.returncode == expected and artifacts_ok else "failed"
        records.append({
            "task_id": task["id"], "verification_ids": [case["verification_id"]], "verification_case": case["case"],
            "scope_ref": scope, "command": shlex.join(command), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr, "timestamp": datetime.now(timezone.utc).isoformat(),
            "executor": executor, "result": result,
            "artifact_paths": [str(path.relative_to(project_root).as_posix()) for path in artifacts if path.is_file()],
        })
    return records


def execute_task_list(project_root: Path, task_list_id: str, *, executor: str, executor_profile: str = "standard") -> dict[str, Any]:
    if not executor.strip():
        raise ValueError("executor is required")
    confirmation_root = (project_root / "graph/.derived/confirmations")
    package = None
    for candidate in sorted(confirmation_root.glob("G-PLAN-*.json")):
        value = json.loads(candidate.read_text(encoding="utf-8"))
        if task_list_id in value.get("document_ids", []):
            package = value
            break
    if package is None:
        return {"status": "blocked", "reason": "g_plan_missing"}
    scope = package["scope_ref"]
    gate = confirmation_status(project_root, "G-PLAN", scope, package["document_ids"])
    if not gate["valid"]:
        return {"status": "blocked", "reason": "g_plan_" + gate["reason"]}
    graph = load_graph(project_root)
    task_list = graph.nodes.get(task_list_id)
    if not task_list or task_list.document_type != "task-list":
        raise ValueError(f"task list not found: {task_list_id}")
    if task_list.data["scope_ref"] != scope:
        return {"status": "blocked", "reason": "g_plan_scope_mismatch"}
    test_plan = next((node for node in graph.all_nodes if node.document_type == "test-plan" and node.data.get("scope_ref") == scope), None)
    if not test_plan:
        return {"status": "blocked", "reason": "test_plan_missing"}

    tasks = task_list.data.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("task list has no structured tasks")
    task_by_id = _task_map(tasks)
    records = list(task_list.data.get("execution_records") or [])
    root_causes = list(task_list.data.get("root_causes") or [])
    overall = "done"
    pending = list(tasks)
    while pending:
        progressed = False
        for task in list(pending):
            dependencies = [task_by_id[value] for value in task.get("depends_on") or []]
            if any(item.get("status") in {"failed", "blocked"} for item in dependencies):
                task["status"] = "blocked"
                overall = "blocked"
                pending.remove(task)
                progressed = True
                continue
            if any(item.get("status") != "done" for item in dependencies):
                continue
            if task.get("status") == "done" and any(record.get("task_id") == task["id"] and record.get("result") == "passed" for record in records):
                pending.remove(task)
                progressed = True
                continue
            guarded = task.get("criticality") == "core" or task.get("infrastructure") is True
            if guarded and executor_profile != "senior" and not _approval_valid(task):
                task["status"] = "blocked"
                overall = "blocked"
                pending.remove(task)
                progressed = True
                continue
            declared_verifications = {item.get("id") for item in test_plan.data.get("verifications") or []}
            if not task.get("verification_ids") or not set(task["verification_ids"]) <= declared_verifications:
                task["status"] = "blocked"
                overall = "blocked"
                pending.remove(task)
                progressed = True
                continue
            command = task.get("command")
            if not isinstance(command, list) or not command or not all(isinstance(value, str) for value in command):
                task["status"] = "blocked"
                overall = "blocked"
                records.append({"task_id": task["id"], "scope_ref": scope, "result": "blocked", "reason": "command_missing", "timestamp": datetime.now(timezone.utc).isoformat(), "executor": executor})
                pending.remove(task)
                progressed = True
                continue
            artifact_values = task.get("artifact_paths", [])
            if any(Path(value).is_absolute() or ".." in Path(value).parts for value in artifact_values):
                task["status"] = "blocked"
                overall = "blocked"
                pending.remove(task)
                progressed = True
                continue
            before = {value: _fingerprint(project_root / value) for value in artifact_values}
            completed = subprocess.run(command, cwd=project_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, shell=False)
            artifacts = [project_root / value for value in artifact_values]
            artifacts_changed = bool(artifacts) and all(path.is_file() and _fingerprint(path) != before[value] for path, value in zip(artifacts, artifact_values))
            assertion_ok, assertion_errors = _assertions_pass(project_root, task)
            result = "passed" if completed.returncode == 0 and artifacts_changed and assertion_ok else "failed"
            record = {
                "task_id": task["id"], "verification_ids": task.get("verification_ids", []), "scope_ref": scope,
                "command": shlex.join(command), "exit_code": completed.returncode, "stdout": completed.stdout,
                "stderr": completed.stderr, "timestamp": datetime.now(timezone.utc).isoformat(), "executor": executor,
                "result": result, "artifact_paths": [str(path.relative_to(project_root).as_posix()) for path in artifacts if path.is_file()],
                "assertion_errors": assertion_errors,
            }
            records.append(record)
            record_errors = validate_execution_record(record)
            if record_errors:
                record["result"] = "failed"
                record["integrity_errors"] = record_errors
                result = "failed"
            verification_records = _run_verification_cases(project_root, task, executor, scope) if result == "passed" else []
            records.extend(verification_records)
            required_cases = {(verification_id, case) for verification_id in task.get("verification_ids", []) for case in ("positive", "negative")}
            passed_cases = {((item.get("verification_ids") or [None])[0], item.get("verification_case")) for item in verification_records if item.get("result") == "passed"}
            if result == "passed" and not required_cases <= passed_cases:
                result = "failed"
                record["result"] = "failed"
                record["integrity_errors"] = sorted(f"verification_case_missing:{verification}:{case}" for verification, case in required_cases - passed_cases)
            task["status"] = "done" if result == "passed" else "failed"
            if result == "passed":
                for root_cause in root_causes:
                    if root_cause.get("task_id") == task["id"] and root_cause.get("status") == "open":
                        root_cause.update({"status": "resolved", "resolved_by_record": len(records) - 1, "resolved_at": record["timestamp"]})
            else:
                overall = "failed"
                root_causes.append({"id": f"RC-{len(root_causes)+1:03d}", "task_id": task["id"], "failed_record": records.index(record), "actual": completed.stderr or completed.stdout or "; ".join(record.get("integrity_errors") or assertion_errors) or "required artifact missing", "status": "open"})
            pending.remove(task)
            progressed = True
        if not progressed:
            for task in pending:
                task["status"] = "blocked"
            overall = "blocked"
            break
    task_list.data["tasks"] = tasks
    task_list.data["execution_records"] = records
    task_list.data["root_causes"] = root_causes
    task_list.data["status"] = "done" if overall == "done" else "blocked"
    base_body = task_list.body.split("\n## 执行记录\n", 1)[0].rstrip()
    body = base_body + "\n\n## 执行记录\n\n" + "\n".join(f"- {record['task_id']}: {record['result']} ({record.get('exit_code', 'n/a')})" for record in records) + "\n"
    _write_node(task_list.path, task_list.data, body)
    return {"status": overall, "task_list_id": task_list_id, "records": records, "root_causes": root_causes}
