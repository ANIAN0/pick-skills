#!/usr/bin/env python3
"""Regression tests for the strict coverage gate."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import audit_wiki


class AuditWikiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project = Path(self.temp_dir.name)
        self.source = self.project / "docs" / "V0.3.0" / "requirement.md"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("# Requirement\n\nStable requirement body.\n", encoding="utf-8")
        self.wiki = self.project / "internal-wiki"
        (self.wiki / "_meta").mkdir(parents=True)
        (self.wiki / "index.md").write_text(
            '---\nokf_version: "0.1"\n---\n\n# Knowledge Base\n', encoding="utf-8"
        )
        (self.wiki / "purpose.md").write_text("# Purpose\n", encoding="utf-8")
        (self.wiki / "INSTRUCTIONS.md").write_text("# Instructions\n", encoding="utf-8")
        (self.wiki / "log.md").write_text("# Log\n", encoding="utf-8")
        (self.wiki / "_meta" / "schema.md").write_text("# Schema\n", encoding="utf-8")
        (self.wiki / "_meta" / "state.json").write_text(
            '{"version": 1, "phase": "growing", "design": {}}\n', encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def inventory(self, profile: str = "generic") -> dict:
        return audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                authoritative_root=["docs"],
                exclude_dir=[],
                profile=profile,
            )
        )

    def validate(self, profile: str = "generic") -> dict:
        return audit_wiki.validate(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                meta_root=None,
                profile=profile,
            )
        )

    def stamp_review(self, coverage_path: Path, *, profile: str, meta_root: Path) -> None:
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        wiki_sha256 = audit_wiki._tree_sha256(
            self.wiki, meta_root if audit_wiki._within(self.wiki, meta_root) else None
        )
        coverage_sha256 = audit_wiki._coverage_sha256(coverage)
        artifact = {
            "reviewer": "fresh-context-test-reviewer",
            "reviewed_at": "2026-07-16T00:00:00+08:00",
            "fresh_context": True,
            "participated_in_build": False,
            "reviewer_context_id": "review-context",
            "builder_context_id": "builder-context",
            "coverage_sha256": coverage_sha256,
            "wiki_sha256": wiki_sha256,
            "blocker_count": 0,
            "findings": [],
            "coverage_checks": {"filesystem_reconciled": True},
            "retrieval_tests": [
                {"question": f"question-{index}", "result": "pass", "evidence": "test fixture"}
                for index in range(4 if profile != "personal" else 3)
            ],
            "reviewed_none_sources": sorted(
                path
                for path, entry in coverage["files"].items()
                if entry.get("object_disposition") == "none"
            ),
            "reviewed_sensitive_sources": sorted(
                path
                for path, entry in coverage["files"].items()
                if entry.get("status") == "sensitive"
            ),
        }
        artifact_path = meta_root / "review.json"
        artifact_bytes = json.dumps(artifact, ensure_ascii=False, indent=2).encode("utf-8")
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(artifact_bytes)
        try:
            artifact_ref = artifact_path.relative_to(self.project).as_posix()
        except ValueError:
            artifact_ref = str(artifact_path)
        coverage["review"] = {
            "status": "passed",
            "reviewer": "fresh-context-test-reviewer",
            "artifact": artifact_ref,
            "artifact_sha256": audit_wiki.hashlib.sha256(artifact_bytes).hexdigest(),
            "coverage_sha256": coverage_sha256,
            "wiki_sha256": wiki_sha256,
            "blocker_count": 0,
        }
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")

    def map_source(self, target: str = "requirements/REQ-001.md") -> None:
        target_path = self.wiki / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            "---\n"
            "type: Product Requirement\n"
            "id: REQ-001\n"
            "title: Requirement\n"
            "description: Test requirement.\n"
            "state: active\n"
            "updated_at: 2026-07-16\n"
            "sources:\n"
            "  - docs/V0.3.0/requirement.md\n"
            "---\n\n# Requirement\n",
            encoding="utf-8",
        )
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        entry = coverage["files"]["docs/V0.3.0/requirement.md"]
        entry.update(
            {
                "status": "mapped",
                "targets": [target],
                "evidence": ["docs/V0.3.0/requirement.md#Requirement"],
                "claims": [
                    {
                        "evidence": "docs/V0.3.0/requirement.md#Requirement",
                        "target": target,
                        "text": "Requirement",
                    }
                ],
                "reason": "",
            }
        )
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_exact_source_mapping_passes(self) -> None:
        self.inventory()
        self.map_source()
        result = self.validate()
        self.assertTrue(result["valid"], result["errors"])

    def test_source_validation_allows_other_files_to_remain_pending(self) -> None:
        other = self.project / "docs" / "V0.4.0" / "other.md"
        other.parent.mkdir(parents=True)
        other.write_text("# Other\n\nNot processed yet.\n", encoding="utf-8")
        self.inventory("project")
        self.map_source()
        result = audit_wiki.validate(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                meta_root=None,
                profile="project",
                source="docs/V0.3.0/requirement.md",
            )
        )
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["source_filter"], "docs/V0.3.0/requirement.md")

    def test_authoritative_root_overrides_default_directory_exclusion(self) -> None:
        protected = self.project / "docs" / "build" / "historical.md"
        protected.parent.mkdir(parents=True)
        protected.write_text("# Historical requirement\n", encoding="utf-8")
        self.inventory()
        coverage = json.loads((self.wiki / "_meta" / "coverage.json").read_text(encoding="utf-8"))
        self.assertIn("docs/build/historical.md", coverage["files"])

    def test_project_and_product_profiles_require_authoritative_root(self) -> None:
        result = audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                authoritative_root=[],
                exclude_dir=[],
                profile="product",
                meta_root=None,
            )
        )
        self.assertIn("authoritative-root", result["error"])

    def test_validate_rejects_profile_downgrade(self) -> None:
        self.inventory("product")
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["scope"]["profile"] = "generic"
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.validate("product")
        self.assertTrue(any("profile 与期望不一致" in item["message"] for item in result["errors"]))

    def test_personal_profile_rejects_whole_source_exclusion(self) -> None:
        result = audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                meta_root=None,
                authoritative_root=[],
                exclude_dir=["docs"],
                profile="personal",
            )
        )
        self.assertIn("不允许用 --exclude-dir", result["error"])

    def test_personal_manifest_can_live_in_external_knowledge_base(self) -> None:
        with tempfile.TemporaryDirectory() as external_text:
            external = Path(external_text)
            wiki = external / "personal-kb"
            meta = wiki / "_meta" / "sources" / "project-a"
            wiki.mkdir(parents=True)
            result = audit_wiki.inventory(
                argparse.Namespace(
                    project_root=self.project,
                    wiki_root=str(wiki),
                    meta_root=str(meta),
                    authoritative_root=[],
                    exclude_dir=[],
                    profile="personal",
                )
            )
            self.assertIsNone(result["error"])
            self.assertTrue((meta / "coverage.json").is_file())

    def test_document_outside_declared_root_cannot_be_ignored(self) -> None:
        outside = self.project / "other" / "notes.md"
        outside.parent.mkdir(parents=True)
        outside.write_text("# Project documentation\n", encoding="utf-8")
        self.inventory("project")
        self.map_source()
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["other/notes.md"].update(
            {"status": "ignored", "reason": "outside the declared documentation root"}
        )
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.validate("project")
        self.assertTrue(any("文档候选" in item["message"] for item in result["errors"]))

    def test_project_profile_rejects_sidecar_as_okf_substitute(self) -> None:
        control = self.project / "wiki-control"
        result = audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                meta_root="wiki-control",
                profile="project",
                authoritative_root=["docs"],
                exclude_dir=[],
            )
        )
        self.assertIsNone(result["error"])
        legacy = self.wiki / "guide" / "legacy.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("# Legacy guide\n\nExisting site format.\n", encoding="utf-8")
        coverage_path = control / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/V0.3.0/requirement.md"].update(
            {
                "status": "mapped",
                "targets": ["guide/legacy.md"],
                "evidence": ["docs/V0.3.0/requirement.md#Requirement"],
                "claims": [
                    {
                        "evidence": "docs/V0.3.0/requirement.md#Requirement",
                        "target": "guide/legacy.md",
                        "text": "Legacy guide",
                    }
                ],
            }
        )
        coverage["pages"] = {
            "guide/legacy.md": {
                "type": "Guide",
                "title": "Legacy guide",
                "description": "Existing public guide.",
                "state": "active",
                "updated_at": "2026-07-16",
                "sources": ["docs/V0.3.0/requirement.md"],
            }
        }
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stamp_review(coverage_path, profile="project", meta_root=control)
        validated = audit_wiki.validate(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="internal-wiki",
                meta_root="wiki-control",
                profile="project",
            )
        )
        self.assertFalse(validated["valid"])
        self.assertTrue(
            any("sidecar" in item["message"] or "OKF 概念页" in item["message"] for item in validated["errors"]),
            validated["errors"],
        )

    def test_arbitrary_evidence_string_is_rejected(self) -> None:
        self.inventory()
        self.map_source()
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/V0.3.0/requirement.md"]["evidence"] = ["read"]
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.validate()
        self.assertTrue(any("可验证 evidence" in item["message"] for item in result["errors"]))

    def test_duplicate_requires_identical_canonical_source(self) -> None:
        self.inventory("project")
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/V0.3.0/requirement.md"].update(
            {
                "status": "duplicate",
                "reason": "asserted duplicate without canonical source",
                "canonical_source": "docs/missing.md",
            }
        )
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.validate("project")
        self.assertTrue(any("canonical_source" in item["message"] for item in result["errors"]))

    def test_changed_source_invalidates_disposition(self) -> None:
        self.inventory()
        self.map_source()
        self.source.write_text("# Requirement\n\nChanged.\n", encoding="utf-8")
        result = self.validate()
        self.assertFalse(result["valid"])
        self.assertTrue(any("来源内容" in item["message"] for item in result["errors"]))

    def test_removed_source_requires_stale_cleanup(self) -> None:
        self.inventory()
        self.source.unlink()
        self.inventory()
        result = self.validate()
        self.assertFalse(result["valid"])
        self.assertTrue(any("陈旧页面" in item["message"] for item in result["errors"]))

    def test_authoritative_source_cannot_map_only_to_index(self) -> None:
        self.inventory()
        self.map_source("requirements/index.md")
        result = self.validate()
        self.assertFalse(result["valid"])
        self.assertTrue(any("index.md" in item["message"] for item in result["errors"]))

    def test_product_profile_reconciles_stable_objects_both_ways(self) -> None:
        self.inventory("product")
        self.map_source()
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        source_entry = coverage["files"]["docs/V0.3.0/requirement.md"]
        source_entry.update({"object_disposition": "contains", "objects": ["REQ-001"]})
        coverage["objects"] = {
            "REQ-001": {
                "type": "Product Requirement",
                "id": "REQ-001",
                "title": "Requirement",
                "source_paths": ["docs/V0.3.0/requirement.md"],
                "target": "requirements/REQ-001.md",
            }
        }
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stamp_review(coverage_path, profile="product", meta_root=self.wiki / "_meta")
        result = self.validate("product")
        self.assertTrue(result["valid"], result["errors"])
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/V0.3.0/requirement.md"]["reason"] = "changed after review"
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        changed = self.validate("product")
        self.assertTrue(any("coverage 内容已变化" in item["message"] for item in changed["errors"]))

    def test_product_object_identity_must_match_target_page(self) -> None:
        self.inventory("product")
        self.map_source()
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        source_entry = coverage["files"]["docs/V0.3.0/requirement.md"]
        source_entry.update({"object_disposition": "contains", "objects": ["REQ-001"]})
        coverage["objects"] = {
            "REQ-001": {
                "type": "Product Requirement",
                "id": "WRONG-ID",
                "title": "Requirement",
                "source_paths": ["docs/V0.3.0/requirement.md"],
                "target": "requirements/REQ-001.md",
            }
        }
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.validate("product")
        self.assertTrue(any("key 与 id" in item["message"] for item in result["errors"]))

    def test_all_detected_requirement_ids_must_be_reconciled(self) -> None:
        self.source.write_text("# Requirements\n\nREQ-001 and REQ-002.\n", encoding="utf-8")
        self.inventory("product")
        self.map_source()
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/V0.3.0/requirement.md"].update(
            {"object_disposition": "contains", "objects": ["REQ-001"]}
        )
        coverage["objects"] = {
            "REQ-001": {
                "type": "Product Requirement",
                "id": "REQ-001",
                "title": "Requirement",
                "source_paths": ["docs/V0.3.0/requirement.md"],
                "target": "requirements/REQ-001.md",
            }
        }
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.validate("product")
        self.assertTrue(any("REQ-002" in item["message"] for item in result["errors"]))

    def test_product_document_with_object_hints_cannot_self_report_none(self) -> None:
        self.inventory("product")
        self.map_source()
        target = self.wiki / "requirements" / "REQ-001.md"
        target.write_text(
            "---\n"
            "type: Product Source\n"
            "title: Requirement source\n"
            "description: Source summary.\n"
            "state: active\n"
            "updated_at: 2026-07-16\n"
            "sources:\n"
            "  - docs/V0.3.0/requirement.md\n"
            "---\n\n# Source\n",
            encoding="utf-8",
        )
        coverage_path = self.wiki / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/V0.3.0/requirement.md"].update(
            {
                "object_disposition": "none",
                "objects": [],
                "reason": "document contains no stable object",
            }
        )
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stamp_review(coverage_path, profile="product", meta_root=self.wiki / "_meta")
        result = self.validate("product")
        self.assertTrue(any("object_hints" in item["message"] or "提示词" in item["message"] for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
