#!/usr/bin/env python3
"""持久化并检查 V3 五阶段入口，不代替阶段工作或用户确认。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STAGE_ORDER = ["requirements", "tech-design", "planning", "execution", "acceptance"]
MODE_START = {"full": 0, "extension": 0, "task": 2, "bug": 2}
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_path(project_root: Path, version: str, run_id: str) -> Path:
    path = project_root / "workplace" / version / "workflow-runs" / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _save(project_root: Path, run: dict[str, Any]) -> None:
    path = _run_path(project_root, run["version"], run["id"])
    path.write_text(
        json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _resolve_project_path(project_root: Path, raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(project_root.resolve())
    except ValueError as error:
        raise ValueError(f"package path escapes project root: {raw}") from error
    return candidate


def _metadata(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"entry not found: {path}")
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"entry frontmatter missing: {path}")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("\"'")
    return result


def _link_target(raw: str) -> str:
    match = MARKDOWN_LINK.fullmatch(raw.strip())
    return match.group(1) if match else raw.strip()


def _passed_review(entry: Path, raw: str) -> tuple[bool, str, Path | None]:
    if not raw or raw == "pending":
        return False, "review_pending", None
    target = Path(_link_target(raw))
    if not target.is_absolute():
        target = entry.parent / target
    target = target.resolve()
    try:
        review = _metadata(target)
    except ValueError:
        return False, "review_missing", target
    if review.get("status") != "passed":
        return False, "review_not_passed", target
    return True, "passed", target


def _fingerprint(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _validate_stage(project_root: Path, stage: str, raw_path: str) -> dict[str, Any]:
    try:
        entry = _resolve_project_path(project_root, raw_path)
        metadata = _metadata(entry)
    except ValueError as error:
        return {"valid": False, "reason": str(error), "package": raw_path}

    review_field = "review"
    if stage == "planning":
        review_field = "plan_review"
    elif stage == "execution":
        review_field = "execution_review"

    if stage in {"requirements", "tech-design", "planning", "execution"}:
        if metadata.get("status") != "confirmed":
            return {"valid": False, "reason": "stage_not_confirmed", "package": raw_path}
    elif metadata.get("status") != "confirmed":
        return {"valid": False, "reason": "acceptance_not_confirmed", "package": raw_path}

    if stage == "execution" and metadata.get("execution_status") != "confirmed":
        return {"valid": False, "reason": "execution_not_confirmed", "package": raw_path}

    review_ok, reason, review_path = _passed_review(entry, metadata.get(review_field, ""))
    if not review_ok:
        return {"valid": False, "reason": reason, "package": raw_path}

    paths = [entry]
    if review_path is not None:
        paths.append(review_path)
    return {
        "valid": True,
        "reason": "confirmed",
        "package": raw_path,
        "fingerprint": _fingerprint(paths),
        "checked_at": _now(),
    }


def evaluate_run(project_root: Path, run: dict[str, Any]) -> dict[str, Any]:
    start = MODE_START[run["mode"]]
    for stage in STAGE_ORDER[start:]:
        package = run["stage_packages"].get(stage)
        if not package:
            run.update(
                status="blocked",
                current_stage=stage,
                resume_stage=stage,
                pause_reason=f"{stage}:package_missing",
                updated_at=_now(),
            )
            _save(project_root, run)
            return run

        current = _validate_stage(project_root, stage, package)
        previous = run["stage_status"].get(stage)
        if previous and previous.get("valid") and current.get("valid"):
            if previous.get("fingerprint") != current.get("fingerprint"):
                current = {**current, "valid": False, "reason": "confirmation_stale"}
        run["stage_status"][stage] = current
        if not current["valid"]:
            run.update(
                status="blocked",
                current_stage=stage,
                resume_stage=stage,
                pause_reason=f"{stage}:{current['reason']}",
                updated_at=_now(),
            )
            _save(project_root, run)
            return run

    run.update(
        status="done",
        current_stage=None,
        resume_stage=None,
        pause_reason=None,
        completed_at=_now(),
        updated_at=_now(),
    )
    _save(project_root, run)
    return run


def start_run(
    project_root: Path,
    version: str,
    mode: str,
    scope_ref: str,
    stage_packages: dict[str, str],
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    if mode not in MODE_START:
        raise ValueError(f"unknown mode: {mode}")
    if not re.fullmatch(r"\d+(?:\.\d+)?", version):
        raise ValueError("version must be an integer or two-part number")
    identity = run_id or "RUN-" + uuid.uuid4().hex[:12].upper()
    run = {
        "id": identity,
        "type": "project-development/workflow-run",
        "version": version,
        "mode": mode,
        "scope_ref": scope_ref,
        "stage_packages": dict(stage_packages),
        "stage_status": {},
        "status": "in_progress",
        "current_stage": STAGE_ORDER[MODE_START[mode]],
        "resume_stage": None,
        "pause_reason": None,
        "started_at": _now(),
        "updated_at": _now(),
        "completed_at": None,
    }
    return evaluate_run(project_root.resolve(), run)


def resume_run(
    project_root: Path,
    version: str,
    run_id: str,
    *,
    package_updates: dict[str, str] | None = None,
    reset_gate: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    path = _run_path(root, version, run_id)
    if not path.is_file():
        raise ValueError(f"workflow run not found: {run_id}")
    run = json.loads(path.read_text(encoding="utf-8"))
    run["stage_packages"].update(package_updates or {})
    if reset_gate is not None:
        if reset_gate not in STAGE_ORDER:
            raise ValueError(f"unknown reset gate: {reset_gate}")
        reset_index = STAGE_ORDER.index(reset_gate)
        for stage in STAGE_ORDER[reset_index:]:
            run["stage_status"].pop(stage, None)
        run["completed_at"] = None
    return evaluate_run(root, run)


def _packages(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"package must use stage=path: {value}")
        stage, path = value.split("=", 1)
        if stage not in STAGE_ORDER:
            raise ValueError(f"unknown package stage: {stage}")
        result[stage] = path
    return result


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="编排 V3 五阶段入口和人工确认")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--project-root", type=Path, required=True)
    start.add_argument("--version", required=True)
    start.add_argument("--mode", choices=sorted(MODE_START), required=True)
    start.add_argument("--scope-ref", required=True)
    start.add_argument("--package", action="append", default=[])
    start.add_argument("--run-id")

    resume = subparsers.add_parser("resume")
    resume.add_argument("--project-root", type=Path, required=True)
    resume.add_argument("--version", required=True)
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--package", action="append", default=[])
    resume.add_argument("--reset-gate", choices=STAGE_ORDER)

    args = parser.parse_args()
    try:
        if args.command == "start":
            run = start_run(
                args.project_root,
                args.version,
                args.mode,
                args.scope_ref,
                _packages(args.package),
                run_id=args.run_id,
            )
        else:
            run = resume_run(
                args.project_root,
                args.version,
                args.run_id,
                package_updates=_packages(args.package),
                reset_gate=args.reset_gate,
            )
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(run, ensure_ascii=False, sort_keys=True))
    return 0 if run["status"] == "done" else 2


if __name__ == "__main__":
    raise SystemExit(main())
