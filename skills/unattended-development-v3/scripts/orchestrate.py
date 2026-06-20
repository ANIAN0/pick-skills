from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys


COMMON = Path(__file__).resolve().parents[2] / "project-development-v3-common/scripts"
if str(COMMON) not in sys.path:
    sys.path.insert(0, str(COMMON))

from confirmation_core import confirmation_status  # noqa: E402


GATE_ORDER = ["G-REQ", "G-DESIGN", "G-PLAN", "G-ACCEPT"]
MODE_START = {"full": 0, "extension": 0, "task": 2, "bug": 2}


def _run_path(project_root: Path, run_id: str) -> Path:
    path = project_root / "graph/runs" / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _save(project_root: Path, run: dict[str, Any]) -> None:
    _run_path(project_root, run["id"]).write_text(json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_stage_action(project_root: Path, run: dict[str, Any], gate: str) -> list[str] | None:
    action = (run.get("stage_actions") or {}).get(gate)
    if not action:
        return None
    command = action.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(value, str) for value in command):
        raise ValueError(f"invalid stage action for {gate}")
    completed = subprocess.run(command, cwd=project_root, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=False, check=False)
    record = {"gate": gate, "command": command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr, "ran_at": datetime.now(timezone.utc).isoformat()}
    run.setdefault("stage_records", []).append(record)
    try:
        result = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        run["pause_reason"] = f"{gate}:stage_output_invalid"
        return None
    record["result"] = result
    documents = result.get("package_document_ids")
    if not isinstance(documents, list) or not documents:
        run["pause_reason"] = f"{gate}:stage_package_missing"
        return None
    return documents


def evaluate_run(project_root: Path, run: dict[str, Any]) -> dict[str, Any]:
    start = MODE_START[run["mode"]]
    for gate in GATE_ORDER[start:]:
        package = run["gate_packages"].get(gate)
        if not package:
            package = _run_stage_action(project_root, run, gate)
            if package:
                run["gate_packages"][gate] = package
            else:
                reason = run.get("pause_reason") or f"{gate}:package_missing"
                run.update({"status": "blocked", "current_gate": gate, "resume_gate": gate, "pause_reason": reason, "updated_at": datetime.now(timezone.utc).isoformat()})
                _save(project_root, run)
                return run
        status = confirmation_status(project_root, gate, run["scope_ref"], package)
        run["gate_status"][gate] = status
        if not status["valid"]:
            run.update({"status": "blocked", "current_gate": gate, "resume_gate": gate, "pause_reason": f"{gate}:{status['reason']}", "updated_at": datetime.now(timezone.utc).isoformat()})
            _save(project_root, run)
            return run
    run.update({"status": "done", "current_gate": None, "resume_gate": None, "pause_reason": None, "completed_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()})
    _save(project_root, run)
    return run


def start_run(project_root: Path, mode: str, scope_ref: dict[str, Any], gate_packages: dict[str, list[str]], *, run_id: str | None = None, stage_actions: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    if mode not in MODE_START:
        raise ValueError(f"unknown mode: {mode}")
    identity = run_id or "RUN-" + uuid.uuid4().hex[:12].upper()
    run = {
        "id": identity,
        "type": "project-development/workflow-run",
        "mode": mode,
        "scope_ref": scope_ref,
        "gate_packages": gate_packages,
        "gate_status": {},
        "stage_actions": stage_actions or {},
        "stage_records": [],
        "status": "in_progress",
        "current_gate": GATE_ORDER[MODE_START[mode]],
        "resume_gate": None,
        "pause_reason": None,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    return evaluate_run(project_root, run)


def resume_run(project_root: Path, run_id: str) -> dict[str, Any]:
    path = _run_path(project_root, run_id)
    if not path.is_file():
        raise ValueError(f"workflow run not found: {run_id}")
    run = json.loads(path.read_text(encoding="utf-8"))
    return evaluate_run(project_root, run)
