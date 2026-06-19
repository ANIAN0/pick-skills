from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import yaml


NODE_TYPES = {
    "user-story",
    "requirement",
    "capability",
    "verification",
    "research-task",
    "ui-spec",
    "prototype",
    "technical-decision",
    "change-contract",
    "review-finding",
    "root-cause",
    "task",
    "acceptance",
    "evidence",
    "workflow-run",
}
STATUSES = {
    "draft",
    "confirmed",
    "ready",
    "in_progress",
    "blocked",
    "done",
    "stale",
    "superseded",
}
RELATION_SCOPES = {
    "depends-on": {"project"},
    "verifies": {"project"},
    "implements": {"project"},
    "researches": {"project"},
    "uses-knowledge": {"knowledge"},
    "specifies": {"project"},
    "prototypes": {"project"},
    "evidences": {"project"},
    "supersedes": {"project"},
    "references": {"project", "knowledge"},
}
REQUIRED_FIELDS = {"type", "id", "node_type", "title", "status", "revision"}
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
HASH_EXCLUDED_FIELDS = {
    "confirmation",
    "status",
    "backlinks",
    "children",
    "computed_impact",
    "last_indexed_at",
}


class DuplicateKeyError(ValueError):
    def __init__(self, key: object) -> None:
        super().__init__(f"duplicate YAML key: {key}")
        self.key = str(key)


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(key)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    file: str
    node_id: str | None
    field: str | None
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "file": self.file,
            "node_id": self.node_id,
            "field": self.field,
            "message": self.message,
        }


@dataclass
class Node:
    path: Path
    relative_path: str
    data: dict[str, Any]
    body: str

    @property
    def id(self) -> str | None:
        value = self.data.get("id")
        return value if isinstance(value, str) and value else None

    @property
    def node_type(self) -> str | None:
        value = self.data.get("node_type")
        return value if isinstance(value, str) else None


@dataclass
class Graph:
    root: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    all_nodes: list[Node] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    edge_count: int = 0
    children: dict[str, list[str]] = field(default_factory=dict)
    forward_edges: dict[str, list[tuple[str, str, str]]] = field(default_factory=dict)
    reverse_edges: dict[str, list[tuple[str, str, str]]] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.issues

    def result(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "node_count": len(self.all_nodes),
            "edge_count": self.edge_count,
            "issues": [issue.as_dict() for issue in self.issues],
        }


def _issue(
    graph: Graph,
    code: str,
    node: Node | None,
    field_name: str | None,
    message: str,
    *,
    file_name: str | None = None,
    node_id: str | None = None,
) -> None:
    graph.issues.append(
        ValidationIssue(
            code=code,
            file=file_name or (node.relative_path if node else ""),
            node_id=node_id if node_id is not None else (node.id if node else None),
            field=field_name,
            message=message,
        )
    )


def _node_files(root: Path) -> list[Path]:
    source = root / "nodes" if (root / "nodes").is_dir() else root
    return sorted(path for path in source.rglob("*.md") if path.is_file())


def _load_node(path: Path, root: Path, graph: Graph) -> Node | None:
    relative = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _issue(graph, "FILE_READ_ERROR", None, None, str(exc), file_name=relative)
        return None
    match = FRONTMATTER_RE.match(text)
    if not match:
        _issue(
            graph,
            "FRONTMATTER_MISSING",
            None,
            None,
            "Markdown file must start with YAML Frontmatter",
            file_name=relative,
        )
        return None
    try:
        data = yaml.load(match.group(1), Loader=UniqueKeyLoader)
    except DuplicateKeyError as exc:
        _issue(
            graph,
            "YAML_DUPLICATE_KEY",
            None,
            exc.key,
            str(exc),
            file_name=relative,
        )
        return None
    except yaml.YAMLError as exc:
        _issue(graph, "YAML_INVALID", None, None, str(exc), file_name=relative)
        return None
    if not isinstance(data, dict):
        _issue(
            graph,
            "FRONTMATTER_TYPE",
            None,
            None,
            "Frontmatter must be a mapping",
            file_name=relative,
        )
        return None
    return Node(path=path, relative_path=relative, data=data, body=text[match.end() :])


def _json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def normalize_body(body: str) -> str:
    normalized = body.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip(" \t") for line in normalized.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def semantic_hash(node: Node) -> str:
    semantic = {
        key: _json_value(value)
        for key, value in node.data.items()
        if key not in HASH_EXCLUDED_FIELDS
    }
    encoded = json.dumps(
        semantic,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload = encoded + "\n---body---\n" + normalize_body(node.body)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_schema(graph: Graph, node: Node) -> None:
    for name in sorted(REQUIRED_FIELDS):
        if name not in node.data:
            _issue(graph, "REQUIRED_FIELD", node, name, f"missing required field: {name}")
    if node.data.get("type") != "project-development/node":
        _issue(graph, "TYPE_INVALID", node, "type", "type must be project-development/node")
    if not isinstance(node.data.get("id"), str) or not node.data.get("id", "").strip():
        _issue(graph, "ID_INVALID", node, "id", "id must be a non-empty string")
    if node.data.get("node_type") not in NODE_TYPES:
        _issue(graph, "NODE_TYPE_INVALID", node, "node_type", "unknown node_type")
    if not isinstance(node.data.get("title"), str) or not node.data.get("title", "").strip():
        _issue(graph, "TITLE_INVALID", node, "title", "title must be a non-empty string")
    if node.data.get("status") not in STATUSES:
        _issue(graph, "STATUS_INVALID", node, "status", "unknown v3 lifecycle status")
    revision = node.data.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        _issue(graph, "REVISION_INVALID", node, "revision", "revision must be an integer >= 1")
    parent = node.data.get("parent")
    if parent is not None and (not isinstance(parent, str) or not parent):
        _issue(graph, "PARENT_INVALID", node, "parent", "parent must be a node ID or null")
    relations = node.data.get("relations", [])
    if not isinstance(relations, list):
        _issue(graph, "RELATIONS_INVALID", node, "relations", "relations must be a list")
    if node.node_type == "task":
        task_fields = {
            "criticality": {"core", "supporting"},
            "risk": {"high", "medium", "low"},
            "executor_requirement": {"senior", "standard"},
        }
        for name, allowed in task_fields.items():
            if node.data.get(name) not in allowed:
                _issue(graph, "TASK_FIELD_INVALID", node, name, f"{name} must be one of: {', '.join(sorted(allowed))}")
        if not isinstance(node.data.get("infrastructure"), bool):
            _issue(graph, "TASK_FIELD_INVALID", node, "infrastructure", "infrastructure must be boolean")


def _validate_relations(graph: Graph, node: Node) -> None:
    relations = node.data.get("relations", [])
    if not isinstance(relations, list):
        return
    for index, relation in enumerate(relations):
        field_name = f"relations[{index}]"
        if not isinstance(relation, dict):
            _issue(graph, "RELATION_INVALID", node, field_name, "relation must be a mapping")
            continue
        relation_type = relation.get("type")
        target = relation.get("target")
        scope = relation.get("scope")
        if relation_type not in RELATION_SCOPES:
            _issue(graph, "RELATION_TYPE_UNKNOWN", node, f"{field_name}.type", "unknown relation type")
            continue
        if not isinstance(target, str) or not target:
            _issue(graph, "RELATION_TARGET_INVALID", node, f"{field_name}.target", "target must be an ID")
        if scope not in RELATION_SCOPES[relation_type]:
            _issue(
                graph,
                "RELATION_SCOPE_INVALID",
                node,
                f"{field_name}.scope",
                f"invalid scope for {relation_type}",
            )
        if scope == "project" and isinstance(target, str) and target not in graph.nodes:
            _issue(
                graph,
                "RELATION_TARGET_MISSING",
                node,
                f"{field_name}.target",
                f"project target does not exist: {target}",
            )
        target_node = graph.nodes.get(target) if scope == "project" and isinstance(target, str) else None
        direction_rules: dict[str, tuple[set[str], set[str]]] = {
            "verifies": ({"verification"}, {"capability", "requirement"}),
            "implements": ({"task", "change-contract"}, set(NODE_TYPES)),
            "researches": ({"research-task"}, set(NODE_TYPES)),
            "specifies": ({"ui-spec"}, {"capability"}),
            "prototypes": ({"prototype"}, {"ui-spec"}),
            "evidences": ({"evidence"}, {"verification", "task"}),
        }
        if relation_type in direction_rules:
            source_types, target_types = direction_rules[relation_type]
            if node.node_type not in source_types:
                _issue(
                    graph,
                    "RELATION_SOURCE_TYPE",
                    node,
                    f"{field_name}.type",
                    f"{relation_type} is not allowed from {node.node_type}",
                )
            if target_node and target_node.node_type not in target_types:
                _issue(
                    graph,
                    "RELATION_TARGET_TYPE",
                    node,
                    f"{field_name}.target",
                    f"{relation_type} cannot target {target_node.node_type}",
                )


def _validate_parents(graph: Graph) -> None:
    for node in graph.all_nodes:
        parent = node.data.get("parent")
        if isinstance(parent, str):
            if parent == node.id:
                _issue(graph, "PARENT_SELF", node, "parent", "node cannot be its own parent")
            elif parent not in graph.nodes:
                _issue(graph, "PARENT_MISSING", node, "parent", f"parent does not exist: {parent}")

    state: dict[str, int] = {}

    def visit(node_id: str, trail: list[str]) -> None:
        if state.get(node_id) == 2:
            return
        if state.get(node_id) == 1:
            cycle = trail[trail.index(node_id) :]
            node = graph.nodes[node_id]
            _issue(graph, "PARENT_CYCLE", node, "parent", "parent cycle: " + " -> ".join(cycle))
            return
        state[node_id] = 1
        parent = graph.nodes[node_id].data.get("parent")
        if isinstance(parent, str) and parent in graph.nodes:
            visit(parent, trail + [parent])
        state[node_id] = 2

    for node_id in graph.nodes:
        if state.get(node_id, 0) == 0:
            visit(node_id, [node_id])


def _validate_confirmation(graph: Graph, node: Node) -> None:
    confirmation = node.data.get("confirmation")
    if confirmation is None:
        return
    if not isinstance(confirmation, dict):
        _issue(graph, "CONFIRMATION_INVALID", node, "confirmation", "confirmation must be a mapping or null")
        return
    stored = confirmation.get("content_hash")
    if not isinstance(stored, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", stored):
        _issue(graph, "CONFIRMATION_HASH_INVALID", node, "confirmation.content_hash", "invalid SHA-256 hash")
        return
    if "confirmed_at" not in confirmation:
        _issue(graph, "CONFIRMATION_TIME_MISSING", node, "confirmation.confirmed_at", "confirmed_at is required")
    current = semantic_hash(node)
    if stored != current:
        _issue(
            graph,
            "CONFIRMATION_STALE",
            node,
            "confirmation.content_hash",
            f"confirmation hash mismatch: stored={stored} current={current}",
        )


def _relations(node: Node, relation_type: str) -> Iterable[dict[str, Any]]:
    relations = node.data.get("relations", [])
    if not isinstance(relations, list):
        return ()
    return (
        relation
        for relation in relations
        if isinstance(relation, dict) and relation.get("type") == relation_type
    )


def _approved(node: Node) -> bool:
    approval = node.data.get("approval")
    return (
        isinstance(approval, dict)
        and approval.get("approved") is True
        and isinstance(approval.get("approved_by"), str)
        and bool(approval["approved_by"].strip())
        and "approved_at" in approval
    )


def _validate_executor_gate(graph: Graph, node: Node) -> None:
    if node.node_type != "task" or node.data.get("status") not in {"in_progress", "done"}:
        return
    guarded = node.data.get("criticality") == "core" or node.data.get("infrastructure") is True
    if not guarded:
        return
    senior = node.data.get("executor_profile") == "senior"
    if not senior and not _approved(node):
        _issue(
            graph,
            "EXECUTOR_GATE",
            node,
            "executor_profile",
            "core or infrastructure task requires senior executor_profile or explicit approval",
        )


def _evidence_for(graph: Graph, target_id: str) -> list[Node]:
    matches: list[Node] = []
    for candidate in graph.all_nodes:
        if candidate.node_type != "evidence":
            continue
        if any(relation.get("target") == target_id for relation in _relations(candidate, "evidences")):
            matches.append(candidate)
    return matches


def _valid_passed_evidence(node: Node) -> bool:
    data = node.data
    exit_code = data.get("exit_code")
    timestamp = data.get("timestamp")
    return (
        data.get("result") == "passed"
        and isinstance(data.get("command"), str)
        and bool(data["command"].strip())
        and (
            exit_code is None
            or (isinstance(exit_code, int) and not isinstance(exit_code, bool) and exit_code == 0)
        )
        and (
            isinstance(timestamp, (datetime, date))
            or (isinstance(timestamp, str) and bool(timestamp.strip()))
        )
        and isinstance(data.get("artifact_paths"), list)
        and bool(data["artifact_paths"])
        and isinstance(data.get("executor"), str)
        and bool(data["executor"].strip())
    )


def _validate_evidence_node(graph: Graph, node: Node) -> None:
    if node.node_type != "evidence":
        return
    for name in ("result", "command", "exit_code", "stdout", "stderr", "timestamp", "artifact_paths", "executor"):
        if name not in node.data:
            _issue(graph, "EVIDENCE_FIELD_MISSING", node, name, f"evidence field is required: {name}")
    if node.data.get("result") not in {"passed", "failed", "blocked", "not_verified"}:
        _issue(graph, "EVIDENCE_RESULT_INVALID", node, "result", "unknown evidence result")
    links = list(_relations(node, "evidences"))
    if not links:
        _issue(graph, "EVIDENCE_TARGET_MISSING", node, "relations", "evidence must target a Verification or Task")
    for relation in links:
        target = graph.nodes.get(relation.get("target"))
        if target and target.node_type not in {"verification", "task"}:
            _issue(graph, "EVIDENCE_TARGET_TYPE", node, "relations", "evidences target must be Verification or Task")
    if node.data.get("result") == "passed" and not _valid_passed_evidence(node):
        _issue(graph, "EVIDENCE_PASSED_INVALID", node, "result", "passed evidence lacks real command, success result, or artifact path")


def _validate_done_gates(graph: Graph, node: Node) -> None:
    if node.data.get("status") != "done" or not node.id:
        return
    if node.node_type == "capability":
        matching = []
        for verification in graph.all_nodes:
            if verification.node_type != "verification" or verification.data.get("parent") != node.data.get("parent"):
                continue
            if any(relation.get("target") == node.id for relation in _relations(verification, "verifies")):
                matching.append(verification)
        if not matching:
            _issue(
                graph,
                "CAPABILITY_VERIFICATION_GATE",
                node,
                "status",
                "done capability requires a same-parent Verification linked by verifies",
            )
    if node.node_type == "task":
        verification_targets = [
            graph.nodes.get(relation.get("target"))
            for relation in _relations(node, "depends-on")
        ]
        if not any(target and target.node_type == "verification" for target in verification_targets):
            _issue(
                graph,
                "TASK_VERIFICATION_GATE",
                node,
                "relations",
                "done task requires a depends-on relation to a Verification",
            )
    if node.node_type in {"task", "verification"}:
        evidence = _evidence_for(graph, node.id)
        if not any(_valid_passed_evidence(item) for item in evidence):
            _issue(
                graph,
                "DONE_EVIDENCE_GATE",
                node,
                "status",
                "done node requires linked passed Evidence with real execution fields",
            )
    if node.node_type in {"acceptance", "workflow-run"}:
        targets = [
            graph.nodes.get(relation.get("target"))
            for relation in _relations(node, "depends-on")
        ]
        verifiable = [target for target in targets if target and target.node_type in {"verification", "task"}]
        if not verifiable:
            _issue(
                graph,
                "DONE_SCOPE_GATE",
                node,
                "relations",
                "done Acceptance or Workflow Run requires depends-on targets for Verification or Task",
            )
        for target in verifiable:
            if target.id and not any(_valid_passed_evidence(item) for item in _evidence_for(graph, target.id)):
                _issue(
                    graph,
                    "DONE_EVIDENCE_GATE",
                    node,
                    "status",
                    f"done Acceptance or Workflow Run target lacks passed Evidence: {target.id}",
                )


def load_graph(root: Path | str) -> Graph:
    root_path = Path(root).resolve()
    graph = Graph(root=root_path)
    if not root_path.is_dir():
        _issue(graph, "GRAPH_ROOT_INVALID", None, None, "graph root must be an existing directory", file_name=str(root_path))
        return graph

    for path in _node_files(root_path):
        node = _load_node(path, root_path, graph)
        if node is None:
            continue
        graph.all_nodes.append(node)
        _validate_schema(graph, node)
        if node.id:
            if node.id in graph.nodes:
                _issue(graph, "DUPLICATE_ID", node, "id", f"duplicate node ID: {node.id}")
                original = graph.nodes[node.id]
                _issue(graph, "DUPLICATE_ID", original, "id", f"duplicate node ID: {node.id}")
            else:
                graph.nodes[node.id] = node

    for node in graph.all_nodes:
        relations = node.data.get("relations", [])
        if isinstance(relations, list):
            graph.edge_count += sum(1 for relation in relations if isinstance(relation, dict))
        _validate_relations(graph, node)
        _validate_confirmation(graph, node)
        _validate_executor_gate(graph, node)
        _validate_evidence_node(graph, node)
    _validate_parents(graph)
    for node in graph.all_nodes:
        _validate_done_gates(graph, node)
    for node in graph.all_nodes:
        if not node.id:
            continue
        parent = node.data.get("parent")
        if isinstance(parent, str) and parent in graph.nodes:
            graph.children.setdefault(parent, []).append(node.id)
        relations = node.data.get("relations", [])
        if not isinstance(relations, list):
            continue
        for relation in relations:
            if not isinstance(relation, dict):
                continue
            relation_type = relation.get("type")
            target = relation.get("target")
            scope = relation.get("scope")
            if not all(isinstance(value, str) for value in (relation_type, target, scope)):
                continue
            edge = (relation_type, target, scope)
            graph.forward_edges.setdefault(node.id, []).append(edge)
            graph.reverse_edges.setdefault(target, []).append((relation_type, node.id, scope))
    for adjacency in (graph.children, graph.forward_edges, graph.reverse_edges):
        for key in adjacency:
            adjacency[key].sort()
    return graph
