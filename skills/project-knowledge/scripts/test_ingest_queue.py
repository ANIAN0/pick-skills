#!/usr/bin/env python3
"""Regression tests for the persistent single-source ingest queue."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

import audit_wiki
import ingest_queue


class IngestQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project = Path(self.temp_dir.name)
        self.source = self.project / "docs" / "a.md"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("# Requirement\n\nStable requirement body.\n", encoding="utf-8")
        other = self.project / "docs" / "b.md"
        other.write_text("# Other\n\nQueued for later.\n", encoding="utf-8")
        self.okf = self.project / "project-kb"
        (self.okf / "_meta" / "ingest").mkdir(parents=True)
        (self.okf / "index.md").write_text(
            '---\nokf_version: "0.1"\n---\n\n# Knowledge Base\n', encoding="utf-8"
        )
        (self.okf / "INSTRUCTIONS.md").write_text(
            "# Instructions\n\nRead state, coverage, queue, schema, then only committed sources.\n",
            encoding="utf-8",
        )
        (self.okf / "purpose.md").write_text(
            "# Purpose\n\nThis knowledge base answers maintainer questions from the docs authority root.\n",
            encoding="utf-8",
        )
        (self.okf / "log.md").write_text("# Log\n", encoding="utf-8")
        (self.okf / "_meta" / "schema.md").write_text(
            "# Schema\n\nRequirement pages use stable IDs, active or draft state, and precise sources.\n",
            encoding="utf-8",
        )
        (self.okf / "_meta" / "state.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "phase": "design",
                    "design": {
                        "readers": ["maintainer"],
                        "questions": ["What?", "Why?", "How?"],
                        "boundaries": ["docs"],
                        "source_priorities": ["docs first"],
                        "operational_conditions": ["retrieval and review pass"],
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
                authoritative_root=["docs"],
                exclude_dir=[],
                profile="project",
            )
        )
        self.args = dict(
            project_root=self.project,
            okf_root="project-kb",
            meta_root=None,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def map_first_source(self) -> None:
        target = self.okf / "requirements" / "REQ-001.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "---\n"
            "type: Project Requirement\n"
            "title: Requirement\n"
            "description: Stable requirement.\n"
            "state: active\n"
            "updated_at: 2026-07-16\n"
            "sources: [docs/a.md]\n"
            "---\n\n# Requirement\n\nStable requirement body.\n",
            encoding="utf-8",
        )
        coverage_path = self.okf / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["files"]["docs/a.md"].update(
            {
                "status": "mapped",
                "targets": ["requirements/REQ-001.md"],
                "evidence": ["docs/a.md#Requirement"],
                "claims": [
                    {
                        "evidence": "docs/a.md#Requirement",
                        "target": "requirements/REQ-001.md",
                        "text": "Stable requirement body.",
                    }
                ],
            }
        )
        coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")

    def prepare_write_phase(
        self,
        review_items: list[dict] | None = None,
        shared_targets: list[str] | None = None,
    ) -> Path:
        ingest_queue.sync(argparse.Namespace(**self.args))
        claimed = ingest_queue.claim(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertIsNone(claimed["error"])
        artifact = self.okf / "_meta" / "ingest" / "docs-a.json"
        artifact.write_text(
            json.dumps(
                {
                    "source_path": "docs/a.md",
                    "source_sha256": claimed["task"]["source_sha256"],
                    "summary": "The source defines one stable requirement.",
                    "disposition": "mapped",
                    "claims": [
                        {
                            "evidence": "docs/a.md#Requirement",
                            "target": "requirements/REQ-001.md",
                            "text": "Stable requirement body.",
                        }
                    ],
                    "proposed_targets": ["requirements/REQ-001.md"],
                    "shared_targets": shared_targets or [],
                    "review_items": review_items or [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        analyzed = ingest_queue.record_analysis(
            argparse.Namespace(**self.args, source="docs/a.md", artifact=str(artifact))
        )
        self.assertIsNone(analyzed["error"])
        return artifact

    def test_single_source_transaction_finishes_while_other_source_is_pending(self) -> None:
        self.map_first_source()
        self.prepare_write_phase()
        written = ingest_queue.record_write(
            argparse.Namespace(
                **self.args,
                source="docs/a.md",
                target=["requirements/REQ-001.md"],
            )
        )
        self.assertIsNone(written["error"])
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertIsNone(finished["error"], finished)
        self.assertEqual(finished["task"]["status"], "done")
        summary = ingest_queue.status(argparse.Namespace(**self.args))
        self.assertEqual(summary["status_counts"], {"done": 1, "pending": 1})

    def test_sync_blocks_interrupted_write_transaction(self) -> None:
        self.map_first_source()
        self.prepare_write_phase()
        synced = ingest_queue.sync(argparse.Namespace(**self.args))
        self.assertEqual(synced["blocked"], 1)
        queue = json.loads((self.okf / "_meta" / "ingest-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["tasks"]["docs/a.md"]["status"], "blocked")

    def test_blocking_review_keeps_source_not_verified_until_resolution(self) -> None:
        self.map_first_source()
        self.prepare_write_phase(
            [
                {
                    "id": "REV-001",
                    "type": "contradiction",
                    "severity": "blocker",
                    "summary": "Conflicting requirement status.",
                    "evidence": "docs/a.md#Requirement",
                }
            ]
        )
        ingest_queue.record_write(
            argparse.Namespace(
                **self.args,
                source="docs/a.md",
                target=["requirements/REQ-001.md"],
            )
        )
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertEqual(finished["task"]["status"], "not_verified")
        resolved = ingest_queue.resolve_review(
            argparse.Namespace(
                **self.args,
                review_id="REV-001",
                resolution="Confirmed against the current contract.",
                evidence="docs/a.md#Requirement",
            )
        )
        self.assertIsNone(resolved["error"])
        self.assertEqual(resolved["task"]["status"], "done")

    def test_content_change_requeues_committed_source(self) -> None:
        self.map_first_source()
        self.prepare_write_phase()
        ingest_queue.record_write(
            argparse.Namespace(
                **self.args,
                source="docs/a.md",
                target=["requirements/REQ-001.md"],
            )
        )
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertIsNone(finished["error"])
        self.source.write_text("# Requirement\n\nChanged requirement body.\n", encoding="utf-8")
        audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="project-kb",
                meta_root=None,
                authoritative_root=["docs"],
                exclude_dir=[],
                profile="project",
            )
        )
        synced = ingest_queue.sync(argparse.Namespace(**self.args))
        self.assertGreaterEqual(synced["reset"], 1)
        queue = json.loads((self.okf / "_meta" / "ingest-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["tasks"]["docs/a.md"]["status"], "pending")

    def test_tampered_analysis_artifact_cannot_finish(self) -> None:
        self.map_first_source()
        artifact = self.prepare_write_phase()
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        artifact.write_text("{}", encoding="utf-8")
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertIn("artifact", finished["error"])

    def test_every_claim_must_appear_in_its_target(self) -> None:
        self.map_first_source()
        coverage_path = self.okf / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        second = {
            "evidence": "docs/a.md#Requirement",
            "target": "requirements/REQ-001.md",
            "text": "A second conclusion absent from the target page.",
        }
        coverage["files"]["docs/a.md"]["claims"].append(second)
        coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
        ingest_queue.sync(argparse.Namespace(**self.args))
        claimed = ingest_queue.claim(argparse.Namespace(**self.args, source="docs/a.md"))
        artifact = self.okf / "_meta" / "ingest" / "multi-claim.json"
        artifact.write_text(
            json.dumps(
                {
                    "source_path": "docs/a.md",
                    "source_sha256": claimed["task"]["source_sha256"],
                    "summary": "Two conclusions.",
                    "disposition": "mapped",
                    "claims": coverage["files"]["docs/a.md"]["claims"],
                    "proposed_targets": ["requirements/REQ-001.md"],
                    "shared_targets": [],
                    "review_items": [],
                }
            ),
            encoding="utf-8",
        )
        self.assertIsNone(ingest_queue.record_analysis(
            argparse.Namespace(**self.args, source="docs/a.md", artifact=str(artifact))
        )["error"])
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertIn("来源级校验失败", finished["error"])

    def test_rollback_restores_declared_shared_write_set(self) -> None:
        self.map_first_source()
        original_index = (self.okf / "index.md").read_text(encoding="utf-8")
        original_target = (self.okf / "requirements" / "REQ-001.md").read_text(encoding="utf-8")
        self.prepare_write_phase(shared_targets=["index.md"])
        (self.okf / "index.md").write_text("PARTIAL SHARED WRITE", encoding="utf-8")
        (self.okf / "requirements" / "REQ-001.md").write_text("PARTIAL TARGET WRITE", encoding="utf-8")
        failed = ingest_queue.fail(
            argparse.Namespace(**self.args, source="docs/a.md", error="rollback", rollback=True)
        )
        self.assertIsNone(failed["error"])
        self.assertEqual((self.okf / "index.md").read_text(encoding="utf-8"), original_index)
        self.assertEqual(
            (self.okf / "requirements" / "REQ-001.md").read_text(encoding="utf-8"),
            original_target,
        )

    def test_rollback_refuses_undeclared_shared_write(self) -> None:
        self.map_first_source()
        self.prepare_write_phase()
        (self.okf / "index.md").write_text("UNDECLARED WRITE", encoding="utf-8")
        failed = ingest_queue.fail(
            argparse.Namespace(**self.args, source="docs/a.md", error="rollback", rollback=True)
        )
        self.assertIsNotNone(failed["error"])
        self.assertEqual(failed["task"]["status"], "blocked")

    def test_corrupt_queue_is_not_silently_rebuilt(self) -> None:
        ingest_queue.sync(argparse.Namespace(**self.args))
        queue_path = self.okf / "_meta" / "ingest-queue.json"
        queue_path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            ingest_queue.sync(argparse.Namespace(**self.args))

    def test_rollback_stales_old_blocker_before_retry(self) -> None:
        self.map_first_source()
        self.prepare_write_phase(
            [{
                "id": "REV-OLD",
                "type": "contradiction",
                "severity": "blocker",
                "summary": "Old blocker.",
                "evidence": "docs/a.md#Requirement",
            }]
        )
        failed = ingest_queue.fail(
            argparse.Namespace(**self.args, source="docs/a.md", error="retry", rollback=True)
        )
        self.assertIsNone(failed["error"])
        self.prepare_write_phase()
        queue = json.loads((self.okf / "_meta" / "ingest-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["review_backlog"]["REV-OLD"]["status"], "stale")

    def test_review_resolution_rejects_changed_source(self) -> None:
        self.map_first_source()
        self.prepare_write_phase(
            [{
                "id": "REV-STALE",
                "type": "contradiction",
                "severity": "blocker",
                "summary": "Needs confirmation.",
                "evidence": "docs/a.md#Requirement",
            }]
        )
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.source.write_text("# Requirement\n\nChanged.\n", encoding="utf-8")
        resolved = ingest_queue.resolve_review(
            argparse.Namespace(
                **self.args,
                review_id="REV-STALE",
                resolution="confirmed",
                evidence="docs/a.md#Requirement",
            )
        )
        self.assertIsNotNone(resolved["error"])

    def test_claim_requires_queue_head_and_new_cycle(self) -> None:
        ingest_queue.sync(argparse.Namespace(**self.args))
        wrong = ingest_queue.claim(argparse.Namespace(**self.args, source="docs/b.md"))
        self.assertIn("队首", wrong["error"])
        self.map_first_source()
        self.prepare_write_phase()
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        closed = ingest_queue.claim(argparse.Namespace(**self.args, source="docs/b.md"))
        self.assertIn("continue", closed["error"])
        continued = ingest_queue.continue_cycle(argparse.Namespace(**self.args))
        self.assertIsNone(continued["error"])
        claimed = ingest_queue.claim(argparse.Namespace(**self.args, source="docs/b.md"))
        self.assertIsNone(claimed["error"])

    def test_incomplete_design_blocks_queue_creation(self) -> None:
        state_path = self.okf / "_meta" / "state.json"
        state_path.write_text(
            json.dumps({"version": 1, "phase": "design", "design": {}}), encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            ingest_queue.sync(argparse.Namespace(**self.args))

    def test_milestone_binds_done_source_and_becomes_stale(self) -> None:
        self.map_first_source()
        self.prepare_write_phase()
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        source_hash = finished["task"]["committed_sha256"]
        milestone = self.okf / "_meta" / "milestones" / "REQ.json"
        milestone.parent.mkdir(parents=True)
        review_evidence = self.project / "review" / "REQ.md"
        review_evidence.parent.mkdir()
        review_evidence.write_text("# Independent review\n\nPassed.\n", encoding="utf-8")
        milestone.write_text(
            json.dumps(
                {
                    "id": "REQ",
                    "title": "Requirement scope",
                    "builder": "ingest-agent",
                    "questions": ["What is required?"],
                    "sources": [{"path": "docs/a.md", "sha256": source_hash}],
                    "object_ids": [],
                    "outside_pending": ["docs/b.md"],
                    "retrieval_tests": [{
                        "query": "requirement",
                        "expected": "Stable requirement body.",
                        "result": "Stable requirement body.",
                        "evidence": "project-kb/requirements/REQ-001.md#Requirement",
                        "passed": True,
                    }],
                    "review": {"status": "passed", "reviewer": "fresh-agent", "evidence": "review/REQ.md"},
                }
            ),
            encoding="utf-8",
        )
        analysis_artifact = self.okf / "_meta" / "ingest" / "docs-a.json"
        original_artifact = analysis_artifact.read_text(encoding="utf-8")
        analysis_artifact.write_text("{}", encoding="utf-8")
        rejected = ingest_queue.validate_milestone(
            argparse.Namespace(**self.args, milestone=str(milestone))
        )
        self.assertIn("analysis artifact", rejected["error"])
        analysis_artifact.write_text(original_artifact, encoding="utf-8")
        validated = ingest_queue.validate_milestone(
            argparse.Namespace(**self.args, milestone=str(milestone))
        )
        self.assertEqual(validated["status"], "operational")
        review_evidence.write_text("# Independent review\n\nRETRACTED.\n", encoding="utf-8")
        ingest_queue.sync(argparse.Namespace(**self.args))
        queue = json.loads((self.okf / "_meta" / "ingest-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["milestones"]["REQ"]["status"], "stale")

    def test_cleanup_rejects_active_page_reassigned_to_pending_source(self) -> None:
        self.map_first_source()
        self.prepare_write_phase()
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.source.unlink()
        audit_wiki.inventory(
            argparse.Namespace(
                project_root=self.project,
                wiki_root="project-kb",
                meta_root=None,
                authoritative_root=["docs"],
                exclude_dir=[],
                profile="project",
            )
        )
        ingest_queue.sync(argparse.Namespace(**self.args))
        ingest_queue.continue_cycle(argparse.Namespace(**self.args))
        claimed = ingest_queue.claim(argparse.Namespace(**self.args, source="docs/a.md"))
        artifact = self.okf / "_meta" / "ingest" / "cleanup-a.json"
        artifact.write_text(
            json.dumps(
                {
                    "source_path": "docs/a.md",
                    "source_sha256": claimed["task"]["source_sha256"],
                    "summary": "Remove stale contribution.",
                    "disposition": "mapped",
                    "claims": [],
                    "proposed_targets": ["requirements/REQ-001.md"],
                    "shared_targets": [],
                    "review_items": [],
                }
            ),
            encoding="utf-8",
        )
        ingest_queue.record_analysis(
            argparse.Namespace(**self.args, source="docs/a.md", artifact=str(artifact))
        )
        coverage_path = self.okf / "_meta" / "coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage["changes"]["removed"] = []
        coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
        ingest_queue.record_write(
            argparse.Namespace(**self.args, source="docs/a.md", target=["requirements/REQ-001.md"])
        )
        target = self.okf / "requirements" / "REQ-001.md"
        target.write_text(
            target.read_text(encoding="utf-8").replace("sources: [docs/a.md]", "sources: [docs/b.md]"),
            encoding="utf-8",
        )
        finished = ingest_queue.finish(argparse.Namespace(**self.args, source="docs/a.md"))
        self.assertIn("替代来源未以当前指纹提交", finished["error"])


if __name__ == "__main__":
    unittest.main()
