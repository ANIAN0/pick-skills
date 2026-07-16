#!/usr/bin/env python3
"""持久化 OKF 单来源摄入队列，并在提交前执行来源级校验。"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import audit_wiki


QUEUE_VERSION = 1
DISPOSITIONS = {
    "mapped",
    "consolidated",
    "superseded",
    "duplicate",
    "ignored",
    "sensitive",
    "unsupported",
}
CAPTURE_SCHEMA = "okf-conversation-capture/v1"
CAPTURE_KINDS = {"user-decision", "problem-report", "observation", "experience", "resolution"}
CAPTURE_ID = re.compile(r"^EVD-\d{8}-\d{6}-[A-F0-9]{8}$")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _normalize(value: str) -> str:
    return Path(value.replace("\\", "/").strip("/")).as_posix()


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else root / path).resolve()


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"无法读取 JSON {path}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError(f"JSON 根必须是对象: {path}")
    return data


def _save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temp.replace(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _resolve_evidence_file(project_root: Path, okf_root: Path, evidence: str) -> Path | None:
    raw = evidence.split("#", 1)[0].split(":L", 1)[0]
    for root in (project_root, okf_root):
        candidate = _resolve(root, raw)
        if audit_wiki._within(root, candidate) and candidate.is_file():
            return candidate
    return None


def _state_path(args: argparse.Namespace) -> Path:
    _, _, meta_root, _ = _paths(args)
    return meta_root / "state.json"


def _validate_design(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    _, okf_root, _, _ = _paths(args)
    path = _state_path(args)
    state = _load(path)
    if state.get("version") != 1:
        raise ValueError("_meta/state.json schema 无效")
    design = state.get("design") if isinstance(state.get("design"), dict) else {}
    def meaningful_list(value: Any, minimum: int = 1, maximum: int | None = None) -> bool:
        return (
            isinstance(value, list)
            and len(value) >= minimum
            and (maximum is None or len(value) <= maximum)
            and all(isinstance(item, str) and item.strip() for item in value)
        )

    rules = {
        "readers": lambda value: meaningful_list(value),
        "questions": lambda value: meaningful_list(value, 3, 7) and len(set(value)) == len(value),
        "boundaries": lambda value: meaningful_list(value),
        "source_priorities": lambda value: meaningful_list(value),
        "operational_conditions": lambda value: meaningful_list(value),
    }
    missing = [field for field, valid in rules.items() if not valid(design.get(field))]
    if missing:
        raise ValueError(f"design 阶段未完成，state.json 缺少有效字段: {', '.join(missing)}")
    template_markers = {
        "purpose.md": "在扫描来源前定义",
        "INSTRUCTIONS.md": "写入概念页前",
        "_meta/schema.md": "在写入概念页前定义",
    }
    for relative, marker in template_markers.items():
        control = okf_root / relative
        try:
            content = control.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"design 控制文件不可读: {relative}: {error}") from error
        if marker in content or len(content.strip()) < 40:
            raise ValueError(f"design 控制文件仍是占位内容: {relative}")
    return path, state


def _artifact(args: argparse.Namespace, task: dict[str, Any], source: str) -> tuple[Path, dict[str, Any]]:
    project_root, _, meta_root, _ = _paths(args)
    ref = task.get("analysis_artifact")
    if not isinstance(ref, str) or not ref:
        raise ValueError("任务缺少 analysis artifact")
    path = _resolve(project_root, ref)
    ingest_root = (meta_root / "ingest").resolve()
    if not audit_wiki._within(ingest_root, path) or not path.is_file():
        raise ValueError("analysis artifact 必须存在于 _meta/ingest")
    if _sha256(path) != task.get("analysis_sha256"):
        raise ValueError("analysis artifact 已变化；不能提交")
    data = _load(path)
    if data.get("source_path") != source or data.get("source_sha256") != task.get("source_sha256"):
        raise ValueError("analysis artifact 与当前来源事务不一致")
    return path, data


def _pending_source_blockers(queue: dict[str, Any], source: str, source_sha256: str | None) -> list[str]:
    backlog = queue.get("review_backlog", {}) if isinstance(queue.get("review_backlog"), dict) else {}
    return sorted(
        review_id
        for review_id, item in backlog.items()
        if isinstance(item, dict)
        and item.get("source_path") == source
        and item.get("source_sha256") == source_sha256
        and item.get("status") == "pending"
        and item.get("severity") == "blocker"
    )


def _snapshot_path(meta_root: Path, source: str) -> Path:
    return meta_root / "transactions" / (hashlib.sha256(source.encode("utf-8")).hexdigest() + ".json")


def _wiki_manifest(okf_root: Path, meta_root: Path) -> dict[str, str]:
    ignored = {
        (meta_root / "ingest-queue.json").resolve(),
        (meta_root / "ingest-queue.json.lock").resolve(),
        (meta_root / "ingest-queue.json.tmp").resolve(),
    }
    transactions = (meta_root / "transactions").resolve()
    return {
        str(path.resolve()): _sha256(path)
        for path in okf_root.rglob("*")
        if path.is_file()
        and path.resolve() not in ignored
        and not audit_wiki._within(transactions, path.resolve())
    }


def _create_snapshot(args: argparse.Namespace, source: str, targets: list[str]) -> str:
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    files: dict[str, Any] = {}
    for raw in [str(coverage_path), *(str(_resolve(okf_root, target)) for target in targets)]:
        candidate = Path(raw).resolve()
        if not (audit_wiki._within(okf_root, candidate) or candidate == coverage_path.resolve()):
            raise ValueError(f"写入目标越出 OKF: {candidate}")
        key = str(candidate)
        files[key] = {
            "existed": candidate.is_file(),
            "content_b64": base64.b64encode(candidate.read_bytes()).decode("ascii") if candidate.is_file() else None,
        }
    snapshot = _snapshot_path(meta_root, source)
    _save(snapshot, {
        "version": 1,
        "source": source,
        "created_at": _now(),
        "files": files,
        "baseline": _wiki_manifest(okf_root, meta_root),
    })
    return snapshot.relative_to(project_root).as_posix()


def _unexpected_writes(args: argparse.Namespace, task: dict[str, Any]) -> list[str]:
    project_root, okf_root, meta_root, _ = _paths(args)
    ref = task.get("snapshot")
    if not isinstance(ref, str):
        raise ValueError("任务缺少事务快照")
    snapshot = _load(_resolve(project_root, ref))
    baseline = snapshot.get("baseline") if isinstance(snapshot.get("baseline"), dict) else {}
    current = _wiki_manifest(okf_root, meta_root)
    allowed = set(snapshot.get("files", {}))
    changed = {
        path for path in set(baseline) | set(current)
        if baseline.get(path) != current.get(path)
    }
    return sorted(path for path in changed if path not in allowed)


def _restore_snapshot(args: argparse.Namespace, task: dict[str, Any]) -> None:
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    ref = task.get("snapshot")
    if not isinstance(ref, str) or not ref:
        raise ValueError("没有可验证的事务快照，不能声明回滚完成")
    snapshot_path = _resolve(project_root, ref)
    expected_root = (meta_root / "transactions").resolve()
    if not audit_wiki._within(expected_root, snapshot_path):
        raise ValueError("事务快照越出 _meta/transactions")
    snapshot = _load(snapshot_path)
    unexpected = _unexpected_writes(args, task)
    if unexpected:
        raise ValueError(f"检测到未声明写入，无法自动回滚: {unexpected}")
    files = snapshot.get("files") if isinstance(snapshot.get("files"), dict) else {}
    for raw, saved in files.items():
        candidate = Path(raw).resolve()
        if not (audit_wiki._within(okf_root, candidate) or candidate == coverage_path.resolve()):
            raise ValueError(f"快照包含越界路径: {candidate}")
        if not isinstance(saved, dict):
            raise ValueError("事务快照内容无效")
        if saved.get("existed"):
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_bytes(base64.b64decode(saved.get("content_b64", "")))
        elif candidate.exists():
            if not candidate.is_file():
                raise ValueError(f"拒绝删除非文件目标: {candidate}")
            candidate.unlink()
    snapshot_path.unlink()


def _contains_value(value: Any, needle: str) -> bool:
    if isinstance(value, str):
        return _normalize(value) == needle or needle in value
    if isinstance(value, dict):
        return any(_contains_value(item, needle) for item in value.values())
    if isinstance(value, list):
        return any(_contains_value(item, needle) for item in value)
    return False


@contextmanager
def _lock_queue(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    handle = lock_path.open("a+b")
    try:
        if handle.seek(0, 2) == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as error:
                raise ValueError("ingest queue 正被另一个进程修改") from error
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise ValueError("ingest queue 正被另一个进程修改") from error
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        handle.close()


def _paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    project_root = args.project_root.resolve()
    okf_root = _resolve(project_root, args.okf_root)
    meta_root = _resolve(project_root, args.meta_root) if args.meta_root else okf_root / "_meta"
    return project_root, okf_root, meta_root, meta_root / "coverage.json"


def _queue_path(args: argparse.Namespace) -> Path:
    _, _, meta_root, _ = _paths(args)
    return meta_root / "ingest-queue.json"


def _new_task(path: str, entry: dict[str, Any], *, kind: str = "source") -> dict[str, Any]:
    return {
        "source_path": path,
        "source_sha256": entry.get("sha256"),
        "kind": kind,
        "priority": int(entry.get("priority", 100)),
        "status": "pending",
        "phase": "analyze",
        "attempts": 0,
        "analysis_artifact": None,
        "analysis_sha256": None,
        "targets": [],
        "shared_targets": [],
        "prior_targets": [],
        "committed_sha256": None,
        "last_error": None,
        "updated_at": _now(),
    }


def _stale_source_reviews(queue: dict[str, Any], source: str, reason: str) -> None:
    backlog = queue.get("review_backlog", {}) if isinstance(queue.get("review_backlog"), dict) else {}
    for item in backlog.values():
        if (
            isinstance(item, dict)
            and item.get("source_path") == source
            and item.get("status") == "pending"
        ):
            item["status"] = "stale"
            item["stale_reason"] = reason
            item["stale_at"] = _now()


def _load_queue(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    path = _queue_path(args)
    queue = _load(path)
    if queue.get("version") != QUEUE_VERSION or not isinstance(queue.get("tasks"), dict):
        raise ValueError("ingest queue schema 无效；重新运行 sync")
    return path, queue


def capture(args: argparse.Namespace) -> dict[str, Any]:
    """把对话发现固化成来源文件，并在已有知识库中自动同步到队列。"""
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    kind = str(args.kind).strip()
    summary = str(args.summary).strip()
    scope = str(args.scope).strip()
    reporter = str(args.reporter).strip()
    if kind not in CAPTURE_KINDS:
        return {"error": f"Capture kind 无效: {kind}"}
    if not summary or not scope or not reporter:
        return {"error": "Capture 必须包含非空 summary/scope/reporter"}
    resolves = sorted({str(item).strip() for item in args.resolves if str(item).strip()})
    if kind == "resolution" and not resolves:
        return {"error": "resolution Capture 必须用 --resolves 关联原始 EVD 记录"}
    if kind != "resolution" and resolves:
        return {"error": "只有 resolution Capture 可以使用 --resolves"}
    if any(not CAPTURE_ID.fullmatch(item) for item in resolves):
        return {"error": "--resolves 必须使用完整的 EVD Capture ID"}

    local_now = datetime.now(timezone.utc).astimezone()
    capture_root = _resolve(project_root, args.capture_root)
    if not audit_wiki._within(project_root, capture_root):
        return {"error": "capture-root 必须位于 project-root 内，才能进入 canonical inventory"}
    if capture_root == okf_root or audit_wiki._within(okf_root, capture_root):
        return {"error": "capture-root 不能位于 OKF 输出根内，避免把编译产物当作来源"}
    relative_capture_root = capture_root.relative_to(project_root).as_posix()
    if any(part in audit_wiki.DEFAULT_EXCLUDED_NAMES for part in Path(relative_capture_root).parts):
        return {"error": "capture-root 命中 inventory 默认排除目录，无法保证自动入队"}
    if coverage_path.is_file():
        try:
            existing_coverage = _load(coverage_path)
        except ValueError as error:
            return {"error": str(error)}
        existing_scope = (
            existing_coverage.get("scope")
            if isinstance(existing_coverage.get("scope"), dict)
            else {}
        )
        excluded = {
            _normalize(str(item)) for item in existing_scope.get("user_excluded_dirs", [])
        }
        protected = {
            _normalize(str(item)) for item in existing_scope.get("authoritative_roots", [])
        }
        day_rel = f"{relative_capture_root}/{local_now:%Y-%m-%d}"
        if audit_wiki._is_explicitly_excluded(day_rel, excluded) and not audit_wiki._is_protected(
            day_rel, protected
        ):
            return {"error": "capture-root 命中当前 coverage 的 user_excluded_dirs，无法自动入队"}
    if kind == "resolution":
        existing_ids = {path.stem for path in capture_root.rglob("EVD-*.json")}
        missing = sorted(set(resolves) - existing_ids)
        if missing:
            return {"error": f"resolution 引用的原始 Capture 不存在: {', '.join(missing)}"}

    related_paths: list[str] = []
    for raw in args.related_path:
        value = _normalize(str(raw))
        candidate = _resolve(project_root, value)
        if not audit_wiki._within(project_root, candidate):
            return {"error": f"related-path 越出 project-root: {raw}"}
        related_paths.append(value)
    captured_at = local_now.isoformat(timespec="microseconds")
    seed = json.dumps(
        {"captured_at": captured_at, "kind": kind, "scope": scope, "summary": summary},
        ensure_ascii=False,
        sort_keys=True,
    )
    suffix = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8].upper()
    capture_id = f"EVD-{local_now:%Y%m%d-%H%M%S}-{suffix}"
    payload = {
        "schema": CAPTURE_SCHEMA,
        "id": capture_id,
        "status": "pending",
        "captured_at": captured_at,
        "kind": kind,
        "reporter": reporter,
        "scope": scope,
        "summary": summary,
        "details": str(args.details).strip(),
        "context": {
            "conversation_ref": str(args.conversation_ref).strip() or None,
            "related_paths": sorted(set(related_paths)),
        },
        "evidence_refs": sorted(
            {str(item).strip() for item in args.evidence_ref if str(item).strip()}
        ),
        "requested_action": str(args.requested_action).strip() or None,
        "resolves": resolves,
        "epistemic": {
            "authority": "normative-within-scope" if kind == "user-decision" else "reporter-only",
            "allowed_assertion_type": "normative" if kind == "user-decision" else "reported",
            "fact_eligible": False,
            "normative_eligible": kind == "user-decision",
            "operational_eligible": False,
            "verification_required": kind != "user-decision",
        },
    }
    day_root = capture_root / local_now.strftime("%Y-%m-%d")
    day_root.mkdir(parents=True, exist_ok=True)
    capture_path = day_root / f"{capture_id}.json"
    try:
        with capture_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        return {"error": f"Capture ID 冲突，未覆盖现有记录: {capture_id}"}
    source = capture_path.relative_to(project_root).as_posix()
    source_sha256 = _sha256(capture_path)
    registry_path = meta_root / "capture-registry.json"
    try:
        with _lock_queue(registry_path):
            registry = _load(registry_path) if registry_path.is_file() else {"version": 1, "entries": {}}
            if registry.get("version") != 1 or not isinstance(registry.get("entries"), dict):
                return {"error": "Capture 已保存，但 capture-registry schema 无效"}
            registry["entries"][source] = {
                "schema": CAPTURE_SCHEMA,
                "id": capture_id,
                "kind": kind,
                "scope": scope,
                "assertion_type": payload["epistemic"]["allowed_assertion_type"],
                "fact_eligible": False,
                "normative_eligible": kind == "user-decision",
                "operational_eligible": False,
                "verification_required": kind != "user-decision",
                "source_sha256": source_sha256,
            }
            registry["updated_at"] = _now()
            _save(registry_path, registry)
    except ValueError as error:
        return {"error": f"Capture 已保存，但 registry 更新失败: {error}"}
    result: dict[str, Any] = {
        "capture_id": capture_id,
        "source": source,
        "sha256": source_sha256,
        "assertion_type": payload["epistemic"]["allowed_assertion_type"],
        "fact_eligible": False,
        "normative_eligible": payload["epistemic"]["normative_eligible"],
        "operational_eligible": False,
        "queue_status": "awaiting_inventory",
        "error": None,
    }
    if not coverage_path.is_file():
        return result
    try:
        state = _load(_state_path(args))
        if state.get("phase") != "growing" or not _queue_path(args).is_file():
            return result
        coverage = _load(coverage_path)
        scope_data = coverage.get("scope") if isinstance(coverage.get("scope"), dict) else {}
        inventory_result = audit_wiki.inventory(
            argparse.Namespace(
                project_root=project_root,
                wiki_root=str(okf_root),
                meta_root=str(meta_root),
                authoritative_root=scope_data.get("authoritative_roots", []),
                exclude_dir=scope_data.get("user_excluded_dirs", []),
                profile=scope_data.get("profile"),
            )
        )
        if inventory_result.get("error"):
            result["error"] = f"Capture 已保存，但 inventory 同步失败: {inventory_result['error']}"
            return result
        queue_result = sync(args)
        if queue_result.get("error"):
            result["error"] = f"Capture 已进入 coverage，但 queue 同步失败: {queue_result['error']}"
            return result
        task = _load(_queue_path(args)).get("tasks", {}).get(source)
        if not isinstance(task, dict):
            result["queue_status"] = "not_registered"
            result["error"] = "Capture 已保存但未进入 ingest queue；检查 inventory 排除与来源范围"
            return result
        result["queue_status"] = task.get("status")
        result["task"] = task
        return result
    except ValueError as error:
        result["error"] = f"Capture 已保存，但自动同步失败: {error}"
        return result


def sync(args: argparse.Namespace) -> dict[str, Any]:
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    state_path, state = _validate_design(args)
    coverage = _load(coverage_path)
    scope = coverage.get("scope") if isinstance(coverage.get("scope"), dict) else {}
    profile = scope.get("profile")
    if profile not in {"personal", "project", "product"}:
        return {"error": "coverage 必须使用 personal/project/product profile"}
    entries = coverage.get("files") if isinstance(coverage.get("files"), dict) else {}
    queue_path = meta_root / "ingest-queue.json"
    queue_existed = queue_path.is_file()
    if queue_existed:
        queue = _load(queue_path)
    else:
        queue = {}
    if queue_existed and (
        queue.get("version") != QUEUE_VERSION
        or queue.get("profile") != profile
        or not isinstance(queue.get("tasks"), dict)
        or not isinstance(queue.get("review_backlog"), dict)
    ):
        raise ValueError("现有 ingest queue schema/profile 无效；拒绝静默重建，请先备份并迁移")
    if not queue_existed:
        queue = {
            "version": QUEUE_VERSION,
            "profile": profile,
            "project_root": str(project_root),
            "okf_root": str(okf_root),
            "created_at": _now(),
            "tasks": {},
            "review_backlog": {},
            "cycle": {"open": True, "completed_sources": 0},
        }
    tasks = queue["tasks"]
    reset = 0
    added = 0
    blocked = 0
    for source_path, raw_entry in sorted(entries.items()):
        if not isinstance(raw_entry, dict):
            continue
        source_path = _normalize(source_path)
        current_hash = raw_entry.get("sha256")
        task = tasks.get(source_path)
        if not isinstance(task, dict):
            tasks[source_path] = _new_task(source_path, raw_entry)
            added += 1
            continue
        old_hash = task.get("source_sha256")
        task["priority"] = int(raw_entry.get("priority", task.get("priority", 100)))
        if old_hash != current_hash:
            if task.get("status") == "in_progress" and task.get("phase") in {"write", "validate"}:
                task["status"] = "blocked"
                task["last_error"] = "来源在写入事务中发生变化；先检查并回滚受影响页面"
                blocked += 1
            else:
                _stale_source_reviews(queue, source_path, "source fingerprint changed")
                task.update(_new_task(source_path, raw_entry))
                reset += 1
        elif task.get("status") == "in_progress":
            if task.get("phase") == "analyze":
                task["status"] = "pending"
                task["last_error"] = "上次分析中断，已安全重新排队"
                reset += 1
            else:
                task["status"] = "blocked"
                task["last_error"] = "上次写入事务中断；先检查并回滚受影响页面"
                blocked += 1
        task["updated_at"] = _now()

    removed = coverage.get("changes", {}).get("removed", []) if isinstance(coverage.get("changes"), dict) else []
    for raw_path in removed if isinstance(removed, list) else []:
        source_path = _normalize(str(raw_path))
        previous = tasks.get(source_path)
        if not isinstance(previous, dict) or previous.get("kind") != "cleanup" or previous.get("status") == "done":
            _stale_source_reviews(queue, source_path, "source removed or moved")
            entry = {"sha256": previous.get("committed_sha256") if isinstance(previous, dict) else None, "priority": 0}
            cleanup_task = _new_task(source_path, entry, kind="cleanup")
            cleanup_task["prior_targets"] = sorted(
                _normalize(item) for item in (previous.get("targets", []) if isinstance(previous, dict) else [])
            )
            tasks[source_path] = cleanup_task
            added += 1

    milestones = queue.get("milestones") if isinstance(queue.get("milestones"), dict) else {}
    for milestone in milestones.values():
        if not isinstance(milestone, dict) or milestone.get("status") != "operational":
            continue
        artifact_ref = milestone.get("artifact")
        artifact_path = _resolve(project_root, artifact_ref) if isinstance(artifact_ref, str) else None
        if (
            artifact_path is None
            or not artifact_path.is_file()
            or _sha256(artifact_path) != milestone.get("artifact_sha256")
        ):
            milestone["status"] = "stale"
            milestone["stale_at"] = _now()
            milestone["stale_reason"] = "milestone artifact changed"
            continue
        review_binding = milestone.get("review_evidence") if isinstance(milestone.get("review_evidence"), dict) else {}
        review_path = _resolve(project_root, review_binding.get("path", ""))
        if not review_path.is_file() or _sha256(review_path) != review_binding.get("sha256"):
            milestone["status"] = "stale"
            milestone["stale_at"] = _now()
            milestone["stale_reason"] = "review evidence changed"
            continue
        retrieval_stale = False
        for evidence in milestone.get("retrieval_evidence", []):
            evidence_path = _resolve(project_root, evidence.get("path", "")) if isinstance(evidence, dict) else None
            if evidence_path is None or not evidence_path.is_file() or _sha256(evidence_path) != evidence.get("sha256"):
                retrieval_stale = True
                break
        if retrieval_stale:
            milestone["status"] = "stale"
            milestone["stale_at"] = _now()
            milestone["stale_reason"] = "retrieval evidence changed"
            continue
        for bound in milestone.get("sources", []):
            task = tasks.get(bound.get("path")) if isinstance(bound, dict) else None
            if not isinstance(task, dict) or task.get("status") != "done" or task.get("committed_sha256") != bound.get("sha256"):
                milestone["status"] = "stale"
                milestone["stale_at"] = _now()
                milestone["stale_reason"] = "bound source is no longer committed at the reviewed fingerprint"
                break
            if task.get("analysis_sha256") != bound.get("analysis_sha256"):
                milestone["status"] = "stale"
                milestone["stale_at"] = _now()
                milestone["stale_reason"] = "bound analysis artifact changed"
                break
            try:
                _, current_artifact = _artifact(args, task, str(bound.get("path")))
            except ValueError:
                milestone["status"] = "stale"
                milestone["stale_at"] = _now()
                milestone["stale_reason"] = "bound analysis artifact is missing or tampered"
                break
            coverage_entry = coverage.get("files", {}).get(bound.get("path"))
            if not isinstance(coverage_entry, dict) or _json_sha256(coverage_entry) != bound.get("coverage_entry_sha256"):
                milestone["status"] = "stale"
                milestone["stale_at"] = _now()
                milestone["stale_reason"] = "bound coverage entry changed"
                break
            for target in bound.get("targets", []):
                target_path = _resolve(okf_root, target.get("path", "")) if isinstance(target, dict) else None
                if (
                    target_path is None
                    or not target_path.is_file()
                    or _sha256(target_path) != target.get("sha256")
                ):
                    milestone["status"] = "stale"
                    milestone["stale_at"] = _now()
                    milestone["stale_reason"] = "bound target page changed"
                    break
            if milestone.get("status") == "stale":
                break
    queue["milestones"] = milestones

    queue["updated_at"] = _now()
    state["phase"] = "growing"
    state["updated_at"] = _now()
    _save(queue_path, queue)
    _save(state_path, state)
    counts = Counter(str(task.get("status")) for task in tasks.values() if isinstance(task, dict))
    return {
        "queue_file": str(queue_path),
        "task_total": len(tasks),
        "added": added,
        "reset": reset,
        "blocked": blocked,
        "status_counts": dict(sorted(counts.items())),
        "error": None,
    }


def status(args: argparse.Namespace) -> dict[str, Any]:
    path, queue = _load_queue(args)
    tasks = queue["tasks"]
    counts = Counter(str(task.get("status")) for task in tasks.values() if isinstance(task, dict))
    phases = Counter(str(task.get("phase")) for task in tasks.values() if isinstance(task, dict))
    backlog = queue.get("review_backlog", {}) if isinstance(queue.get("review_backlog"), dict) else {}
    pending_reviews = [item for item in backlog.values() if isinstance(item, dict) and item.get("status") == "pending"]
    pending_blockers = [item for item in pending_reviews if item.get("severity") == "blocker"]
    return {
        "queue_file": str(path),
        "task_total": len(tasks),
        "status_counts": dict(sorted(counts.items())),
        "phase_counts": dict(sorted(phases.items())),
        "pending_reviews": len(pending_reviews),
        "pending_review_blockers": len(pending_blockers),
        "queue_healthy": (
            counts.get("blocked", 0) == 0
            and counts.get("not_verified", 0) == 0
            and len(pending_blockers) == 0
        ),
    }


def next_task(args: argparse.Namespace) -> dict[str, Any]:
    path, queue = _load_queue(args)
    candidates = [
        task for task in queue["tasks"].values()
        if isinstance(task, dict) and task.get("status") == "pending"
    ]
    candidates.sort(key=lambda task: (int(task.get("priority", 100)), str(task.get("source_path", ""))))
    return {"queue_file": str(path), "task": candidates[0] if candidates else None}


def _task(args: argparse.Namespace) -> tuple[Path, dict[str, Any], str, dict[str, Any]]:
    path, queue = _load_queue(args)
    source = _normalize(args.source)
    task = queue["tasks"].get(source)
    if not isinstance(task, dict):
        raise ValueError(f"来源不在队列: {source}")
    return path, queue, source, task


def claim(args: argparse.Namespace) -> dict[str, Any]:
    path, queue, source, task = _task(args)
    if task.get("status") != "pending":
        return {"error": f"只能 claim pending 任务，当前为 {task.get('status')}"}
    active = [
        item.get("source_path")
        for item in queue["tasks"].values()
        if isinstance(item, dict) and item.get("status") == "in_progress"
    ]
    if active:
        return {"error": f"已有 in_progress 来源，单写者队列不能并发 claim: {active[0]}"}
    blocked = [
        item.get("source_path")
        for item in queue["tasks"].values()
        if isinstance(item, dict) and item.get("status") == "blocked"
    ]
    if blocked:
        return {"error": f"先恢复 blocked 写入事务再继续队列: {blocked[0]}"}
    cycle = queue.get("cycle") if isinstance(queue.get("cycle"), dict) else {}
    if not cycle.get("open", True):
        return {"error": "本轮单来源事务已完成；仅在用户下一次明确要求继续后运行 continue"}
    pending = [
        item for item in queue["tasks"].values()
        if isinstance(item, dict) and item.get("status") == "pending"
    ]
    pending.sort(key=lambda item: (int(item.get("priority", 100)), str(item.get("source_path", ""))))
    if pending and pending[0].get("source_path") != source:
        return {"error": f"必须处理队首来源: {pending[0].get('source_path')}"}
    task["status"] = "in_progress"
    task["phase"] = "analyze"
    task["attempts"] = int(task.get("attempts", 0)) + 1
    task["last_error"] = None
    task["updated_at"] = _now()
    _save(path, queue)
    return {"source": source, "task": task, "error": None}


def record_analysis(args: argparse.Namespace) -> dict[str, Any]:
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    path, queue, source, task = _task(args)
    if task.get("status") != "in_progress" or task.get("phase") != "analyze":
        return {"error": "record-analysis 只接受 in_progress/analyze 任务"}
    artifact_path = _resolve(project_root, args.artifact)
    if not audit_wiki._within((meta_root / "ingest").resolve(), artifact_path):
        return {"error": "analysis artifact 必须位于 _meta/ingest"}
    artifact = _load(artifact_path)
    required = {
        "source_path": source,
        "source_sha256": task.get("source_sha256"),
    }
    for field, expected in required.items():
        if artifact.get(field) != expected:
            return {"error": f"analysis artifact 的 {field} 与队列不一致"}
    if not isinstance(artifact.get("summary"), str) or not artifact["summary"].strip():
        return {"error": "analysis artifact 缺少 summary"}
    if artifact.get("disposition") not in DISPOSITIONS:
        return {"error": "analysis artifact disposition 无效"}
    for field in ("claims", "proposed_targets", "shared_targets", "review_items"):
        if not isinstance(artifact.get(field), list):
            return {"error": f"analysis artifact 缺少列表 {field}"}
    for claim in artifact["claims"]:
        if not isinstance(claim, dict) or not all(
            isinstance(claim.get(field), str) and claim[field].strip()
            for field in ("text", "evidence", "target")
        ):
            return {"error": "claims 每项必须包含非空 text/evidence/target"}
        if not audit_wiki._valid_evidence_locator(
            project_root, source, claim["evidence"], task.get("source_sha256")
        ):
            return {"error": f"claim evidence 不是当前来源的有效 locator: {claim['evidence']}"}
    coverage = _load(coverage_path)
    source_entry = coverage.get("files", {}).get(source)
    capture_meta = source_entry.get("capture") if isinstance(source_entry, dict) else None
    if isinstance(capture_meta, dict):
        if capture_meta.get("valid") is not True:
            return {"error": "Capture schema 无效，不能记录 analysis"}
        if artifact.get("disposition") in {"ignored", "unsupported"}:
            return {"error": "用户明确创建的 Capture 不能以 ignored/unsupported 静默丢弃"}
        if artifact.get("disposition") == "sensitive" and not any(
            isinstance(item, dict)
            and item.get("severity") == "blocker"
            and isinstance(item.get("summary"), str)
            and item["summary"].strip()
            for item in artifact.get("review_items", [])
        ):
            return {"error": "sensitive Capture 必须创建 blocker review item，不能无痕完成"}
        expected_assertion = capture_meta.get("assertion_type")
        for claim in artifact["claims"]:
            if claim.get("assertion_type") != expected_assertion:
                return {
                    "error": f"Capture claim assertion_type 必须是 {expected_assertion}；不能把报告提升成技术事实"
                }
    proposed_targets = sorted(_normalize(item) for item in artifact["proposed_targets"] if isinstance(item, str))
    if len(proposed_targets) != len(artifact["proposed_targets"]):
        return {"error": "proposed_targets 每项必须是路径字符串"}
    claim_targets = sorted({_normalize(item["target"]) for item in artifact["claims"]})
    if task.get("kind") != "cleanup" and claim_targets != proposed_targets:
        return {"error": "claims.target 集合必须与 proposed_targets 一致"}
    shared_targets = sorted(_normalize(item) for item in artifact["shared_targets"] if isinstance(item, str))
    if len(shared_targets) != len(artifact["shared_targets"]):
        return {"error": "shared_targets 每项必须是路径字符串"}
    if task.get("kind") == "cleanup" and not set(task.get("prior_targets", [])).issubset(proposed_targets):
        return {"error": "cleanup proposed_targets 必须覆盖旧事务的全部 targets"}
    _stale_source_reviews(queue, source, "superseded by a new analysis attempt")
    review_ids: list[str] = []
    for item in artifact["review_items"]:
        if not isinstance(item, dict):
            return {"error": "review_items 每项必须是对象"}
        if not all(isinstance(item.get(field), str) and item[field].strip() for field in ("id", "type", "severity", "summary", "evidence")):
            return {"error": "review item 缺少 id/type/severity/summary/evidence"}
        if item["severity"] not in {"blocker", "warning"}:
            return {"error": "review item severity 必须是 blocker 或 warning"}
        review_id = item["id"].strip()
        existing_review = queue["review_backlog"].get(review_id)
        if (
            isinstance(existing_review, dict)
            and existing_review.get("source_path") != source
            and existing_review.get("status") == "pending"
        ):
            return {"error": f"review item ID 已被另一来源使用: {review_id}"}
        queue["review_backlog"][review_id] = {
            **item,
            "id": review_id,
            "source_path": source,
            "source_sha256": task.get("source_sha256"),
            "status": "pending",
            "created_at": _now(),
        }
        review_ids.append(review_id)
    try:
        artifact_ref = artifact_path.relative_to(project_root).as_posix()
    except ValueError:
        artifact_ref = str(artifact_path)
    task["analysis_artifact"] = artifact_ref
    task["analysis_sha256"] = _sha256(artifact_path)
    task["snapshot"] = _create_snapshot(args, source, sorted(set(proposed_targets + shared_targets)))
    task["shared_targets"] = shared_targets
    task["review_ids"] = review_ids
    task["phase"] = "write"
    task["updated_at"] = _now()
    _save(path, queue)
    return {"source": source, "task": task, "error": None}


def record_write(args: argparse.Namespace) -> dict[str, Any]:
    _, _, _, coverage_path = _paths(args)
    path, queue, source, task = _task(args)
    if task.get("status") != "in_progress" or task.get("phase") != "write":
        return {"error": "record-write 只接受 in_progress/write 任务"}
    try:
        _, artifact = _artifact(args, task, source)
        unexpected = _unexpected_writes(args, task)
    except ValueError as error:
        return {"error": str(error)}
    if unexpected:
        return {"error": f"检测到 analysis artifact 未声明的写入目标: {unexpected}"}
    coverage = _load(coverage_path)
    if task.get("kind") == "cleanup":
        expected_targets = sorted(_normalize(target) for target in artifact["proposed_targets"])
    else:
        entry = coverage.get("files", {}).get(source)
        if not isinstance(entry, dict) or entry.get("status") not in DISPOSITIONS:
            return {"error": "coverage 来源尚未写入最终 disposition"}
        if entry.get("status") != artifact.get("disposition"):
            return {"error": "coverage disposition 与 analysis artifact 不一致"}
        expected_targets = sorted(
            _normalize(target) for target in entry.get("targets", []) if isinstance(target, str)
        )
        artifact_targets = sorted(_normalize(target) for target in artifact["proposed_targets"])
        if expected_targets != artifact_targets:
            return {"error": "coverage targets 与 analysis artifact 不一致"}
        if entry.get("claims") != artifact.get("claims"):
            return {"error": "coverage claims 与 analysis artifact 不一致"}
    targets = sorted(_normalize(target) for target in args.target)
    if targets != expected_targets:
        return {"error": f"写入目标与 coverage 不一致: {targets} != {expected_targets}"}
    shared_targets = sorted(_normalize(target) for target in getattr(args, "shared_target", []))
    expected_shared = sorted(_normalize(target) for target in artifact.get("shared_targets", []))
    if shared_targets != expected_shared:
        return {"error": f"共享写入目标与 analysis artifact 不一致: {shared_targets} != {expected_shared}"}
    task["targets"] = targets
    task["shared_targets"] = shared_targets
    task["phase"] = "validate"
    task["updated_at"] = _now()
    _save(path, queue)
    return {"source": source, "task": task, "error": None}


def finish(args: argparse.Namespace) -> dict[str, Any]:
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    path, queue, source, task = _task(args)
    if task.get("status") != "in_progress" or task.get("phase") != "validate":
        return {"error": "finish 只接受 in_progress/validate 任务"}
    try:
        _, artifact = _artifact(args, task, source)
        unexpected = _unexpected_writes(args, task)
    except ValueError as error:
        return {"error": str(error)}
    if unexpected:
        return {"error": f"验证前检测到未声明写入目标: {unexpected}"}
    current_source = (project_root / source).resolve()
    if task.get("kind") != "cleanup":
        if not current_source.is_file() or _sha256(current_source) != task.get("source_sha256"):
            return {"error": "来源内容已变化；重新 inventory/sync 后再处理"}
        coverage_now = _load(coverage_path)
        entry = coverage_now.get("files", {}).get(source)
        if not isinstance(entry, dict):
            return {"error": "coverage 缺少当前来源"}
        if entry.get("status") != artifact.get("disposition") or entry.get("claims") != artifact.get("claims"):
            return {"error": "提交时 coverage 与 analysis artifact 不一致"}
        if sorted(_normalize(item) for item in entry.get("targets", [])) != sorted(
            _normalize(item) for item in artifact.get("proposed_targets", [])
        ):
            return {"error": "提交时 targets 与 analysis artifact 不一致"}
    if task.get("kind") == "cleanup":
        coverage = _load(coverage_path)
        removed = coverage.get("changes", {}).get("removed", []) if isinstance(coverage.get("changes"), dict) else []
        removed_paths = {
            _normalize(str(item)) for item in (removed if isinstance(removed, list) else [])
        }
        if source in removed_paths:
            return {"error": "cleanup 尚未完成：来源仍在 changes.removed"}
        if source in coverage.get("files", {}):
            return {"error": "cleanup 尚未完成：coverage 仍保留来源条目"}
        if _contains_value(coverage.get("objects", {}), source) or _contains_value(coverage.get("pages", {}), source):
            return {"error": "cleanup 尚未完成：coverage objects/pages 仍引用已删除来源"}
        stale_pages = []
        for page in okf_root.rglob("*.md"):
            relative = page.relative_to(okf_root).as_posix()
            if relative.startswith("_meta/") or relative in {"log.md", "INSTRUCTIONS.md"}:
                continue
            try:
                if source in page.read_text(encoding="utf-8"):
                    stale_pages.append(relative)
            except (OSError, UnicodeError):
                stale_pages.append(relative)
        if stale_pages:
            return {"error": f"cleanup 尚未完成：Wiki 页面仍引用来源: {stale_pages}"}
        for target in task.get("prior_targets", []):
            page = _resolve(okf_root, target)
            if not page.exists():
                continue
            try:
                text_value = page.read_text(encoding="utf-8")
                match = audit_wiki.FRONTMATTER.match(text_value)
                metadata = audit_wiki.yaml.safe_load(match.group(1)) if match and audit_wiki.yaml else None
            except Exception as error:
                return {"error": f"cleanup 无法验证旧目标页 {target}: {error}"}
            sources = metadata.get("sources") if isinstance(metadata, dict) else None
            state = metadata.get("state") if isinstance(metadata, dict) else None
            if state == "active" and (not isinstance(sources, list) or not sources):
                return {"error": f"cleanup 留下无来源的 active 孤儿页: {target}"}
            if state == "active":
                for replacement in sources:
                    if not isinstance(replacement, str) or replacement.startswith(("http://", "https://")):
                        return {"error": f"cleanup 的 active 旧页缺少可提交的本地替代来源: {target}"}
                    source_match = audit_wiki.SOURCE_WITH_SYMBOL.match(replacement)
                    raw_source = source_match.group(1) if source_match else replacement
                    replacement_path = (
                        (page.parent / raw_source).resolve()
                        if raw_source.startswith(("./", "../"))
                        else (project_root / raw_source.lstrip("/")).resolve()
                    )
                    if not audit_wiki._within(project_root, replacement_path) or not replacement_path.is_file():
                        return {"error": f"cleanup 替代来源不存在: {replacement}"}
                    replacement_rel = replacement_path.relative_to(project_root).as_posix()
                    replacement_entry = coverage.get("files", {}).get(replacement_rel)
                    replacement_task = queue.get("tasks", {}).get(replacement_rel)
                    if (
                        not isinstance(replacement_entry, dict)
                        or target not in replacement_entry.get("targets", [])
                        or not isinstance(replacement_task, dict)
                        or replacement_task.get("status") != "done"
                        or replacement_task.get("committed_sha256") != replacement_entry.get("sha256")
                    ):
                        return {"error": f"cleanup 替代来源未以当前指纹提交到旧页: {replacement_rel}"}
                    replacement_validation = audit_wiki.validate(
                        argparse.Namespace(
                            project_root=project_root,
                            wiki_root=str(okf_root),
                            meta_root=str(meta_root),
                            profile=queue.get("profile"),
                            source=replacement_rel,
                        )
                    )
                    if not replacement_validation.get("valid"):
                        return {"error": f"cleanup 替代来源校验失败: {replacement_rel}", "validation": replacement_validation}
        validation = {"valid": True, "errors": [], "source_filter": source}
    else:
        validation = audit_wiki.validate(
            argparse.Namespace(
                project_root=project_root,
                wiki_root=str(okf_root),
                meta_root=str(meta_root),
                profile=queue.get("profile"),
                source=source,
            )
        )
        if not validation.get("valid"):
            task["last_error"] = "来源级校验失败"
            task["updated_at"] = _now()
            _save(path, queue)
            return {"error": "来源级校验失败", "validation": validation}
    pending_blockers = _pending_source_blockers(queue, source, task.get("source_sha256"))
    task["status"] = "not_verified" if pending_blockers else "done"
    task["phase"] = "review" if pending_blockers else "done"
    task["committed_sha256"] = task.get("source_sha256")
    task["last_error"] = None
    task["updated_at"] = _now()
    snapshot_ref = task.get("snapshot")
    if isinstance(snapshot_ref, str):
        snapshot_file = _resolve(project_root, snapshot_ref)
        if snapshot_file.is_file():
            snapshot_file.unlink()
    task["snapshot"] = None
    cycle = queue.get("cycle") if isinstance(queue.get("cycle"), dict) else {}
    cycle["open"] = False
    cycle["completed_sources"] = int(cycle.get("completed_sources", 0)) + 1
    cycle["closed_at"] = _now()
    queue["cycle"] = cycle
    _save(path, queue)
    return {
        "source": source,
        "task": task,
        "pending_review_blockers": pending_blockers,
        "validation": validation,
        "error": None,
    }


def fail(args: argparse.Namespace) -> dict[str, Any]:
    path, queue, source, task = _task(args)
    if task.get("status") != "in_progress":
        return {"error": "fail 只接受 in_progress 任务"}
    phase = task.get("phase")
    if phase == "analyze":
        task["status"] = "pending"
        task["phase"] = "analyze"
    elif args.rollback:
        try:
            _restore_snapshot(args, task)
        except (ValueError, OSError, base64.binascii.Error) as error:
            task["status"] = "blocked"
            task["last_error"] = f"回滚失败: {error}"
            task["updated_at"] = _now()
            _save(path, queue)
            return {"error": task["last_error"], "task": task}
        _stale_source_reviews(queue, source, "transaction rolled back")
        task.update({
            "status": "pending",
            "phase": "analyze",
            "analysis_artifact": None,
            "analysis_sha256": None,
            "snapshot": None,
            "review_ids": [],
            "targets": [],
            "shared_targets": [],
        })
    else:
        task["status"] = "blocked"
    task["last_error"] = args.error
    task["updated_at"] = _now()
    _save(path, queue)
    return {"source": source, "task": task, "error": None}


def resolve_review(args: argparse.Namespace) -> dict[str, Any]:
    path, queue = _load_queue(args)
    backlog = queue.get("review_backlog", {}) if isinstance(queue.get("review_backlog"), dict) else {}
    item = backlog.get(args.review_id)
    if not isinstance(item, dict):
        return {"error": f"review item 不存在: {args.review_id}"}
    if item.get("status") != "pending":
        return {"error": f"review item 已是 {item.get('status')}"}
    project_root, okf_root, meta_root, coverage_path = _paths(args)
    coverage = _load(coverage_path)
    source = str(item.get("source_path", ""))
    source_entry = coverage.get("files", {}).get(source)
    source_path = (project_root / source).resolve()
    if (
        not isinstance(source_entry, dict)
        or not source_path.is_file()
        or _sha256(source_path) != source_entry.get("sha256")
        or not audit_wiki._valid_evidence_locator(
        project_root,
        source,
        args.evidence,
        source_entry.get("sha256"),
        )
    ):
        return {"error": "resolution evidence 不是当前来源的有效 locator"}
    task = queue.get("tasks", {}).get(source)
    if not isinstance(task, dict) or task.get("status") != "not_verified":
        return {"error": "review 对应来源不在 not_verified 状态"}
    if task.get("source_sha256") != source_entry.get("sha256") or item.get("source_sha256") != task.get("source_sha256"):
        return {"error": "review、任务与当前来源指纹不一致"}
    try:
        _, artifact = _artifact(args, task, source)
    except ValueError as error:
        return {"error": str(error)}
    if (
        source_entry.get("status") != artifact.get("disposition")
        or source_entry.get("claims") != artifact.get("claims")
        or sorted(_normalize(value) for value in source_entry.get("targets", []))
        != sorted(_normalize(value) for value in artifact.get("proposed_targets", []))
    ):
        return {"error": "review 复核时 coverage 与 analysis artifact 不一致"}
    item["status"] = "resolved"
    item["resolution"] = args.resolution
    item["resolution_evidence"] = args.evidence
    item["resolved_at"] = _now()
    if isinstance(task, dict) and task.get("status") == "not_verified":
        pending_blockers = _pending_source_blockers(queue, source, task.get("source_sha256"))
        if not pending_blockers:
            validation = audit_wiki.validate(
                argparse.Namespace(
                    project_root=project_root,
                    wiki_root=str(okf_root),
                    meta_root=str(meta_root),
                    profile=queue.get("profile"),
                    source=source,
                )
            )
            if not validation.get("valid"):
                item["status"] = "pending"
                item.pop("resolution", None)
                item.pop("resolution_evidence", None)
                item.pop("resolved_at", None)
                return {"error": "复核后来源级校验失败", "validation": validation}
            task["status"] = "done"
            task["phase"] = "done"
            task["updated_at"] = _now()
    queue["updated_at"] = _now()
    _save(path, queue)
    return {"review_id": args.review_id, "item": item, "task": task, "error": None}


def continue_cycle(args: argparse.Namespace) -> dict[str, Any]:
    path, queue = _load_queue(args)
    cycle = queue.get("cycle") if isinstance(queue.get("cycle"), dict) else {}
    if cycle.get("open", True):
        return {"error": "当前单来源轮次尚未关闭"}
    active = [
        item.get("source_path") for item in queue["tasks"].values()
        if isinstance(item, dict) and item.get("status") in {"in_progress", "blocked", "not_verified"}
    ]
    if active:
        return {"error": f"先解决未闭合事务: {active[0]}"}
    cycle["open"] = True
    cycle["opened_at"] = _now()
    queue["cycle"] = cycle
    queue["updated_at"] = _now()
    _save(path, queue)
    return {"cycle": cycle, "error": None}


def validate_milestone(args: argparse.Namespace) -> dict[str, Any]:
    project_root, okf_root, meta_root, _ = _paths(args)
    path, queue = _load_queue(args)
    milestone_path = _resolve(project_root, args.milestone)
    milestone_root = (meta_root / "milestones").resolve()
    if not audit_wiki._within(milestone_root, milestone_path) or not milestone_path.is_file():
        return {"error": "milestone 必须位于 _meta/milestones"}
    milestone = _load(milestone_path)
    for field in ("id", "title"):
        if not isinstance(milestone.get(field), str) or not milestone[field].strip():
            return {"error": f"milestone 缺少 {field}"}
    if not isinstance(milestone.get("questions"), list) or not milestone["questions"]:
        return {"error": "milestone 缺少 questions"}
    sources = milestone.get("sources")
    if not isinstance(sources, list) or not sources:
        return {"error": "milestone 缺少 sources"}
    retrieval = milestone.get("retrieval_tests")
    if not isinstance(retrieval, list) or not retrieval:
        return {"error": "milestone 缺少 retrieval_tests"}
    retrieval_bindings: list[dict[str, str]] = []
    for index, item in enumerate(retrieval):
        if not isinstance(item, dict) or item.get("passed") is not True or not all(
            isinstance(item.get(field), str) and item[field].strip()
            for field in ("query", "expected", "result", "evidence")
        ):
            return {"error": f"retrieval_tests[{index}] 必须含 query/expected/result/evidence 且 passed=true"}
        evidence_file = _resolve_evidence_file(project_root, okf_root, item["evidence"])
        if evidence_file is None:
            return {"error": f"retrieval_tests[{index}] evidence 不存在"}
        retrieval_bindings.append({
            "path": evidence_file.relative_to(project_root).as_posix(),
            "sha256": _sha256(evidence_file),
        })
    review = milestone.get("review") if isinstance(milestone.get("review"), dict) else {}
    builder = milestone.get("builder")
    if (
        review.get("status") != "passed"
        or not isinstance(builder, str)
        or not builder.strip()
        or not review.get("reviewer")
        or review.get("reviewer") == builder
        or not review.get("evidence")
    ):
        return {"error": "milestone 缺少 builder 与不同 reviewer 的 passed/evidence"}
    review_evidence = _resolve(project_root, str(review["evidence"]))
    if not audit_wiki._within(project_root, review_evidence) or not review_evidence.is_file():
        return {"error": "milestone review evidence 必须是项目内存在的文件"}
    if review.get("artifact_sha256") and _sha256(review_evidence) != review.get("artifact_sha256"):
        return {"error": "milestone review evidence 指纹不一致"}
    normalized_sources: list[dict[str, str]] = []
    validations: list[dict[str, Any]] = []
    for bound in sources:
        if not isinstance(bound, dict) or not isinstance(bound.get("path"), str) or not isinstance(bound.get("sha256"), str):
            return {"error": "milestone sources 每项必须包含 path/sha256"}
        source = _normalize(bound["path"])
        task = queue["tasks"].get(source)
        coverage_entry = _load(meta_root / "coverage.json").get("files", {}).get(source)
        capture_meta = coverage_entry.get("capture") if isinstance(coverage_entry, dict) else None
        if isinstance(capture_meta, dict) and capture_meta.get("fact_eligible") is not True:
            return {"error": f"milestone 不能把待验证 Capture 当作 operational 事实来源: {source}"}
        source_path = (project_root / source).resolve()
        if (
            not isinstance(task, dict)
            or task.get("status") != "done"
            or task.get("committed_sha256") != bound["sha256"]
            or not source_path.is_file()
            or _sha256(source_path) != bound["sha256"]
        ):
            return {"error": f"milestone 来源未在绑定指纹上完成: {source}"}
        try:
            _, analysis_artifact = _artifact(args, task, source)
        except ValueError as error:
            return {"error": f"milestone analysis artifact 无效: {source}: {error}"}
        validation = audit_wiki.validate(
            argparse.Namespace(
                project_root=project_root,
                wiki_root=str(okf_root),
                meta_root=str(meta_root),
                profile=queue.get("profile"),
                source=source,
            )
        )
        if not validation.get("valid"):
            return {"error": f"milestone 来源校验失败: {source}", "validation": validation}
        target_bindings = []
        for target in task.get("targets", []):
            target_path = _resolve(okf_root, target)
            if not target_path.is_file():
                return {"error": f"milestone 目标页不存在: {target}"}
            target_bindings.append({"path": target, "sha256": _sha256(target_path)})
        normalized_sources.append({
            "path": source,
            "sha256": bound["sha256"],
            "analysis_sha256": task.get("analysis_sha256"),
            "coverage_entry_sha256": _json_sha256(
                _load(meta_root / "coverage.json").get("files", {}).get(source)
            ),
            "targets": target_bindings,
        })
        validations.append({"source": source, "coverage_sha256": validation.get("coverage_sha256"), "wiki_sha256": validation.get("wiki_sha256")})
    milestone_id = milestone["id"].strip()
    queue.setdefault("milestones", {})[milestone_id] = {
        "status": "operational",
        "title": milestone["title"].strip(),
        "sources": normalized_sources,
        "validated_at": _now(),
        "validations": validations,
        "artifact": milestone_path.relative_to(project_root).as_posix(),
        "artifact_sha256": _sha256(milestone_path),
        "review_evidence": {
            "path": review_evidence.relative_to(project_root).as_posix(),
            "sha256": _sha256(review_evidence),
        },
        "retrieval_evidence": retrieval_bindings,
    }
    queue["updated_at"] = _now()
    _save(path, queue)
    return {"milestone_id": milestone_id, "status": "operational", "sources": normalized_sources, "error": None}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="管理 OKF 单来源摄入队列")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("capture", "sync", "status", "next", "claim", "record-analysis", "record-write", "finish", "fail", "resolve-review", "continue", "validate-milestone"):
        child = subparsers.add_parser(command)
        child.add_argument("--project-root", type=Path, required=True)
        child.add_argument("--okf-root", required=True)
        child.add_argument("--meta-root", default=None)
        if command == "capture":
            child.add_argument("--kind", choices=sorted(CAPTURE_KINDS), required=True)
            child.add_argument("--summary", required=True)
            child.add_argument("--scope", required=True)
            child.add_argument("--details", default="")
            child.add_argument("--reporter", default="user")
            child.add_argument("--conversation-ref", default="")
            child.add_argument("--related-path", action="append", default=[])
            child.add_argument("--evidence-ref", action="append", default=[])
            child.add_argument("--requested-action", default="")
            child.add_argument("--resolves", action="append", default=[])
            child.add_argument("--capture-root", default="knowledge-sources/captures")
        if command in {"claim", "record-analysis", "record-write", "finish", "fail"}:
            child.add_argument("--source", required=True)
        if command == "record-analysis":
            child.add_argument("--artifact", required=True)
        if command == "record-write":
            child.add_argument("--target", action="append", default=[])
            child.add_argument("--shared-target", action="append", default=[])
        if command == "fail":
            child.add_argument("--error", required=True)
            child.add_argument("--rollback", action="store_true")
        if command == "resolve-review":
            child.add_argument("--review-id", required=True)
            child.add_argument("--resolution", required=True)
            child.add_argument("--evidence", required=True)
        if command == "validate-milestone":
            child.add_argument("--milestone", required=True)
    args = parser.parse_args()
    handlers = {
        "capture": capture,
        "sync": sync,
        "status": status,
        "next": next_task,
        "claim": claim,
        "record-analysis": record_analysis,
        "record-write": record_write,
        "finish": finish,
        "fail": fail,
        "resolve-review": resolve_review,
        "continue": continue_cycle,
        "validate-milestone": validate_milestone,
    }
    try:
        if args.command == "capture" and not _queue_path(args).is_file():
            result = handlers[args.command](args)
        elif args.command in {"capture", "sync", "claim", "record-analysis", "record-write", "finish", "fail", "resolve-review", "continue", "validate-milestone"}:
            with _lock_queue(_queue_path(args)):
                result = handlers[args.command](args)
        else:
            result = handlers[args.command](args)
    except ValueError as error:
        result = {"error": str(error)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
