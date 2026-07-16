#!/usr/bin/env python3
"""Regression tests for conversation Capture admission and truth boundaries."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import audit_wiki
import ingest_queue


class CaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project = Path(self.temp_dir.name)
        self.capture_root = self.project / "knowledge-sources" / "captures"
        self.capture_root.mkdir(parents=True)
        self.okf = self.project / "project-kb"
        (self.okf / "_meta" / "ingest").mkdir(parents=True)
        (self.okf / "index.md").write_text(
            '---\nokf_version: "0.1"\n---\n\n# Knowledge Base\n', encoding="utf-8"
        )
        (self.okf / "INSTRUCTIONS.md").write_text(
            "# Instructions\n\nUse committed, fact-eligible claims and disclose pending reports.\n",
            encoding="utf-8",
        )
        (self.okf / "purpose.md").write_text(
            "# Purpose\n\nAnswer maintainers from verified sources and preserve reported gaps.\n",
            encoding="utf-8",
        )
        (self.okf / "log.md").write_text("# Log\n", encoding="utf-8")
        (self.okf / "_meta" / "schema.md").write_text(
            "# Schema\n\nIssues, decisions, and evidence use stable identities and source links.\n",
            encoding="utf-8",
        )
        (self.okf / "_meta" / "state.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "phase": "design",
                    "design": {
                        "readers": ["maintainer"],
                        "questions": ["What failed?", "Why?", "What changed?"],
                        "boundaries": ["project and conversation captures"],
                        "source_priorities": ["captures then project evidence"],
                        "operational_conditions": ["source validation and review pass"],
                    },
                }
            ),
            encoding="utf-8",
        )
        audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="project-kb",
                meta_root=None,
                authoritative_root=["knowledge-sources/captures"],
                exclude_dir=[],
                profile="project",
            )
        )
        self.base = dict(project_root=self.project, okf_root="project-kb", meta_root=None)
        synced = ingest_queue.sync(argparse.Namespace(**self.base))
        self.assertIsNone(synced["error"])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def capture(self, kind: str = "problem-report", **overrides: object) -> dict:
        values = {
            **self.base,
            "kind": kind,
            "summary": "The generated Wiki missed project directories.",
            "scope": "project Wiki construction",
            "details": "The report must be verified against the filesystem inventory.",
            "reporter": "user",
            "conversation_ref": "task-test",
            "related_path": ["docs"],
            "evidence_ref": [],
            "requested_action": "investigate and preserve the result",
            "resolves": [],
            "capture_root": "knowledge-sources/captures",
        }
        values.update(overrides)
        return ingest_queue.capture(argparse.Namespace(**values))

    def test_problem_report_is_saved_and_automatically_queued(self) -> None:
        result = self.capture()
        self.assertIsNone(result["error"])
        self.assertEqual(result["queue_status"], "pending")
        self.assertFalse(result["fact_eligible"])
        source_path = self.project / result["source"]
        self.assertTrue(source_path.is_file())
        self.assertFalse(str(source_path).startswith(str(self.okf)))
        coverage = json.loads((self.okf / "_meta" / "coverage.json").read_text(encoding="utf-8"))
        capture = coverage["files"][result["source"]]["capture"]
        self.assertEqual(capture["assertion_type"], "reported")
        self.assertTrue(capture["verification_required"])
        registry = json.loads(
            (self.okf / "_meta" / "capture-registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            registry["entries"][result["source"]]["source_sha256"], result["sha256"]
        )

    def test_capture_does_not_advance_design_phase(self) -> None:
        state_path = self.okf / "_meta" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["phase"] = "design"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        (self.okf / "_meta" / "ingest-queue.json").unlink()
        result = self.capture()
        self.assertIsNone(result["error"])
        self.assertEqual(result["queue_status"], "awaiting_inventory")
        unchanged = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(unchanged["phase"], "design")

    def test_problem_report_cannot_be_promoted_to_verified_fact(self) -> None:
        result = self.capture()
        source = result["source"]
        claimed = ingest_queue.claim(argparse.Namespace(**self.base, source=source))
        self.assertIsNone(claimed["error"])
        artifact = self.okf / "_meta" / "ingest" / "capture.json"
        capture_id = result["capture_id"]
        base_artifact = {
            "source_path": source,
            "source_sha256": result["sha256"],
            "summary": "The user reported incomplete directory coverage.",
            "disposition": "mapped",
            "claims": [
                {
                    "text": "The project scan definitely omitted directories.",
                    "evidence": f"{source}#{capture_id}",
                    "target": "issues/incomplete-scan.md",
                    "assertion_type": "verified",
                }
            ],
            "proposed_targets": ["issues/incomplete-scan.md"],
            "shared_targets": [],
            "review_items": [],
        }
        artifact.write_text(json.dumps(base_artifact), encoding="utf-8")
        rejected = ingest_queue.record_analysis(
            argparse.Namespace(**self.base, source=source, artifact=str(artifact))
        )
        self.assertIn("assertion_type 必须是 reported", rejected["error"])
        base_artifact["claims"][0].update(
            {
                "text": "The user reported that the project scan omitted directories.",
                "assertion_type": "reported",
            }
        )
        artifact.write_text(json.dumps(base_artifact), encoding="utf-8")
        accepted = ingest_queue.record_analysis(
            argparse.Namespace(**self.base, source=source, artifact=str(artifact))
        )
        self.assertIsNone(accepted["error"])

    def test_user_decision_only_allows_normative_claims(self) -> None:
        result = self.capture(
            kind="user-decision",
            summary="Every knowledge contribution must use the OKF ingest queue.",
        )
        self.assertFalse(result["fact_eligible"])
        self.assertTrue(result["normative_eligible"])
        self.assertFalse(result["operational_eligible"])
        coverage = json.loads((self.okf / "_meta" / "coverage.json").read_text(encoding="utf-8"))
        capture = coverage["files"][result["source"]]["capture"]
        self.assertEqual(capture["assertion_type"], "normative")
        self.assertFalse(capture["fact_eligible"])
        self.assertTrue(capture["normative_eligible"])
        self.assertFalse(capture["verification_required"])

    def test_tampered_capture_cannot_lose_truth_boundary(self) -> None:
        result = self.capture()
        source_path = self.project / result["source"]
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        payload.pop("schema")
        source_path.write_text(json.dumps(payload), encoding="utf-8")
        audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="project-kb",
                meta_root=None,
                authoritative_root=["knowledge-sources/captures"],
                exclude_dir=[],
                profile="project",
            )
        )
        coverage = json.loads((self.okf / "_meta" / "coverage.json").read_text(encoding="utf-8"))
        capture = coverage["files"][result["source"]]["capture"]
        self.assertFalse(capture["valid"])
        self.assertTrue(capture["tampered"])
        ingest_queue.sync(argparse.Namespace(**self.base))
        claimed = ingest_queue.claim(argparse.Namespace(**self.base, source=result["source"]))
        artifact = self.okf / "_meta" / "ingest" / "tampered.json"
        artifact.write_text(
            json.dumps(
                {
                    "source_path": result["source"],
                    "source_sha256": claimed["task"]["source_sha256"],
                    "summary": "Attempt to treat a modified report as an ordinary source.",
                    "disposition": "mapped",
                    "claims": [
                        {
                            "text": "The scan definitely omitted directories.",
                            "evidence": f"{result['source']}#{result['capture_id']}",
                            "target": "issues/incomplete-scan.md",
                        }
                    ],
                    "proposed_targets": ["issues/incomplete-scan.md"],
                    "shared_targets": [],
                    "review_items": [],
                }
            ),
            encoding="utf-8",
        )
        rejected = ingest_queue.record_analysis(
            argparse.Namespace(**self.base, source=result["source"], artifact=str(artifact))
        )
        self.assertIn("Capture schema 无效", rejected["error"])

    def test_capture_rejects_current_user_exclusion(self) -> None:
        coverage_path = self.okf / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["scope"]["user_excluded_dirs"] = ["notes"]
        coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
        result = self.capture(capture_root="notes/captures")
        self.assertIn("user_excluded_dirs", result["error"])
        self.assertFalse((self.project / "notes").exists())

    def test_first_inventory_cannot_exclude_registered_capture(self) -> None:
        (self.okf / "_meta" / "coverage.json").unlink()
        (self.okf / "_meta" / "ingest-queue.json").unlink()
        state_path = self.okf / "_meta" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["phase"] = "design"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        result = self.capture()
        self.assertEqual(result["queue_status"], "awaiting_inventory")
        docs = self.project / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "README.md").write_text("# Docs\n", encoding="utf-8")
        inventory = audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="project-kb",
                meta_root=None,
                authoritative_root=["docs"],
                exclude_dir=["knowledge-sources"],
                profile="project",
            )
        )
        self.assertIn("已登记 Capture 被 inventory 排除", inventory["error"])

    def test_sensitive_capture_requires_blocker_review(self) -> None:
        result = self.capture()
        source = result["source"]
        ingest_queue.claim(argparse.Namespace(**self.base, source=source))
        artifact = self.okf / "_meta" / "ingest" / "sensitive.json"
        artifact.write_text(
            json.dumps(
                {
                    "source_path": source,
                    "source_sha256": result["sha256"],
                    "summary": "The Capture contains sensitive material.",
                    "disposition": "sensitive",
                    "claims": [],
                    "proposed_targets": [],
                    "shared_targets": [],
                    "review_items": [],
                }
            ),
            encoding="utf-8",
        )
        rejected = ingest_queue.record_analysis(
            argparse.Namespace(**self.base, source=source, artifact=str(artifact))
        )
        self.assertIn("blocker review item", rejected["error"])

    def test_resolution_requires_original_evidence_id(self) -> None:
        result = self.capture(kind="resolution")
        self.assertIn("必须用 --resolves", result["error"])
        self.assertEqual(list(self.capture_root.rglob("*.json")), [])

    def test_resolution_links_an_existing_capture(self) -> None:
        original = self.capture()
        result = self.capture(
            kind="resolution",
            summary="The directory inventory was rerun and the reported gap was addressed.",
            resolves=[original["capture_id"]],
        )
        self.assertIsNone(result["error"])
        payload = json.loads((self.project / result["source"]).read_text(encoding="utf-8"))
        self.assertEqual(payload["resolves"], [original["capture_id"]])

    def test_capture_root_cannot_be_inside_okf(self) -> None:
        result = self.capture(capture_root="project-kb/inbox")
        self.assertIn("不能位于 OKF", result["error"])


if __name__ == "__main__":
    unittest.main()
