from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


COMMON = Path(__file__).resolve().parents[2] / "project-development-v3-common" / "scripts"
if str(COMMON) not in sys.path:
    sys.path.insert(0, str(COMMON))

from confirmation_core import confirmation_covers_document, confirmation_status  # noqa: E402
from document_io import create_document  # noqa: E402


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("slug must contain ASCII letters or digits")
    return slug


def _frontmatter(data: dict[str, Any]) -> str:
    return "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n"


def _requirements_body(title: str, requirements: list[dict[str, str]], acceptance: list[dict[str, str]], features: list[dict[str, str]]) -> str:
    parts = [f"# {title}", "", "## 用户故事（User Story）", ""]
    for item in requirements:
        parts.extend([f"## {item['id']} {item['title']}", "", item.get("description", ""), ""])
    for item in acceptance:
        parts.extend([f"## {item['id']} {item['title']}", "", item.get("description", ""), ""])
    if features:
        parts.extend(["## 独立闭环功能点", ""])
        for item in features:
            parts.extend([f"### {item['id']} {item['title']}", "", item.get("goal", ""), ""])
    return "\n".join(parts).rstrip() + "\n"


def generate_requirements(
    project_root: Path,
    spec: dict[str, Any],
) -> dict[str, Any]:
    story = spec["story"]
    modules = spec.get("modules", [])
    if len(modules) > 3:
        return {"status": "awaiting_decomposition_confirmation", "reason": "module_limit", "count": len(modules)}
    for module in modules:
        if len(module.get("features", [])) > 10:
            return {"status": "awaiting_decomposition_confirmation", "reason": "feature_limit", "module": module["id"], "count": len(module["features"])}

    story_dir = project_root / "graph" / "stories" / f"{story['id']}-{_slug(story['slug'])}"
    story_doc_id = f"DOC-REQ-{story['id']}"
    story_path = story_dir / "requirements.md"
    story_data = {
        "type": "project-development/document-node",
        "id": story_doc_id,
        "document_type": "requirements",
        "title": story["title"],
        "status": "draft",
        "revision": 1,
        "parent": None,
        "scope_ref": {"document": story_doc_id, "item": None},
        "relations": [],
        "deliverable": spec["deliverable"],
        "decomposition_decision": {"modules": [module["id"] for module in modules]},
    }
    story_state = create_document(story_path, story_data, _requirements_body(story["title"], spec.get("requirements", []), spec.get("acceptance", []), []))
    scope_ref = {"document": story_doc_id, "item": None}
    if modules and not confirmation_covers_document(project_root, "G-REQ", scope_ref, story_doc_id):
        return {"status": "awaiting_story_confirmation", "story_document": story_doc_id, "package_document_ids": [story_doc_id], "created": [str(story_path)]}

    created = [str(story_path)]
    document_ids = [story_doc_id]
    for module in modules:
        module_dir = story_dir / "modules" / f"{module['id']}-{_slug(module['slug'])}"
        module_doc_id = f"DOC-REQ-{module['id']}"
        module_data = {
            "type": "project-development/document-node",
            "id": module_doc_id,
            "document_type": "requirements",
            "title": module["title"],
            "status": "draft",
            "revision": 1,
            "parent": story_doc_id,
            "scope_ref": {"document": module_doc_id, "item": None},
            "relations": [],
            "deliverable": spec["deliverable"],
        }
        module_path = module_dir / "requirements.md"
        create_document(module_path, module_data, _requirements_body(module["title"], module.get("requirements", []), module.get("acceptance", []), module.get("features", [])))
        created.append(str(module_path))
        document_ids.append(module_doc_id)

    status = confirmation_status(project_root, "G-REQ", scope_ref, document_ids)
    return {"status": "ready_for_design" if status["valid"] else "awaiting_g_req", "created": created, "documents": document_ids, "package_document_ids": document_ids, "confirmation": status, "deliverable": spec["deliverable"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate adaptive hierarchical requirements documents.")
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    args = parser.parse_args()
    result = generate_requirements(args.project_root, json.loads(args.spec.read_text(encoding="utf-8")))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "ready_for_design" else 2


if __name__ == "__main__":
    raise SystemExit(main())
