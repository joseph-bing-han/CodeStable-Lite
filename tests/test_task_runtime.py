from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RUNTIME_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "cs"
    / "scripts"
    / "codestable_task_runtime.py"
)
INITIALIZER_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "cs"
    / "scripts"
    / "init_codestable.py"
)


def load_task_runtime():
    specification = importlib.util.spec_from_file_location("codestable_task_runtime", RUNTIME_PATH)
    assert specification and specification.loader
    task_runtime = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = task_runtime
    specification.loader.exec_module(task_runtime)
    return task_runtime


task_runtime = load_task_runtime()


def load_initializer():
    specification = importlib.util.spec_from_file_location("init_codestable", INITIALIZER_PATH)
    assert specification and specification.loader
    initializer = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = initializer
    specification.loader.exec_module(initializer)
    return initializer


initializer = load_initializer()


def snapshot_directory_tree(directory: Path) -> dict[str, tuple[str, bytes | None]]:
    snapshot: dict[str, tuple[str, bytes | None]] = {}
    if not directory.exists():
        return snapshot

    for directory_entry in sorted(directory.rglob("*")):
        relative_path = directory_entry.relative_to(directory).as_posix()
        if directory_entry.is_dir():
            snapshot[relative_path] = ("directory", None)
        elif directory_entry.is_file():
            snapshot[relative_path] = ("file", directory_entry.read_bytes())
        else:
            snapshot[relative_path] = ("other", None)
    return snapshot


class TaskRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def create_task(self, task: str, goal: str = "Deliver a traceable change") -> Path:
        return task_runtime.create_task(
            root=self.root,
            task=task,
            goal=goal,
            workflow="feature",
            owner="cs",
            steps=["Inspect current behavior", "Implement and verify"],
            related_docs=["src/example.py"],
            current_date="2026-07-29",
        )

    def finish_all_steps(self, task: str) -> Path:
        active_path = self.root.resolve() / f"codestable/tasks/active/{task}.md"
        return task_runtime.update_task(
            root=self.root,
            task=task,
            expected_sha256=task_runtime.calculate_sha256(active_path),
            replacements={
                "- [ ] Inspect current behavior": "- [x] Inspect current behavior",
                "- [ ] Implement and verify": "- [x] Implement and verify",
                "### 1. Inspect current behavior\n\n- 状态：pending": (
                    "### 1. Inspect current behavior\n\n- 状态：done"
                ),
                "### 2. Implement and verify\n\n- 状态：pending": (
                    "### 2. Implement and verify\n\n- 状态：done"
                ),
            },
            progress_record="Completed all planned steps and verification gates.",
            current_date="2026-07-29",
        )

    def complete_task(self, task: str) -> Path:
        active_path = self.finish_all_steps(task)
        return task_runtime.complete_task(
            root=self.root,
            task=task,
            expected_sha256=task_runtime.calculate_sha256(active_path),
            current_date="2026-07-29",
        )

    def test_create_task_writes_only_active_and_archived_workspace_directories(self) -> None:
        active_path = self.create_task("traceable-change")

        task_root = self.root.resolve() / "codestable/tasks"
        task_text = active_path.read_text(encoding="utf-8")
        self.assertEqual(active_path, task_root / "active/traceable-change.md")
        self.assertEqual(
            sorted(path.name for path in task_root.iterdir() if path.is_dir()),
            ["active", "archived"],
        )
        self.assertIn("status: active", task_text)
        self.assertIn("- [ ] Inspect current behavior", task_text)

    def test_task_lifecycle_never_changes_the_issue_workspace(self) -> None:
        issues_root = self.root / "codestable/issues"
        explore_root = issues_root / "003-o-current-path"
        explore_root.mkdir(parents=True)
        (issues_root / "001-o-ordinary.md").write_text("ordinary issue\n", encoding="utf-8")
        (issues_root / "002-o-ff-small-fix.md").write_text("fast fix\n", encoding="utf-8")
        (explore_root / "index.md").write_text("explore issue\n", encoding="utf-8")
        issue_workspace_before_task = snapshot_directory_tree(issues_root)

        active_path = self.create_task("issue-workspace-isolation")
        self.complete_task("issue-workspace-isolation")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="issue-workspace-isolation",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        cleanup_findings = task_runtime.cleanup_task(self.root, "issue-workspace-isolation")
        scan_result = task_runtime.scan_tasks(self.root)

        self.assertTrue((self.root / archive_result.archived_path).is_file())
        self.assertEqual(cleanup_findings, [])
        self.assertEqual(scan_result.findings, ())
        self.assertEqual(snapshot_directory_tree(issues_root), issue_workspace_before_task)

    def test_initializer_preserves_existing_issues_and_creates_no_issue_artifacts(self) -> None:
        issues_root = self.root / "codestable/issues"
        explore_root = issues_root / "003-o-current-path"
        explore_root.mkdir(parents=True)
        (issues_root / "001-o-ordinary.md").write_text("ordinary issue\n", encoding="utf-8")
        (issues_root / "002-o-ff-small-fix.md").write_text("fast fix\n", encoding="utf-8")
        (explore_root / "index.md").write_text("explore issue\n", encoding="utf-8")
        issue_workspace_before_initialization = snapshot_directory_tree(issues_root)

        initialization_output = io.StringIO()
        with contextlib.redirect_stdout(initialization_output):
            initialization_result = initializer.init_codestable(
                project=self.root,
                force=False,
                migrate_legacy=False,
            )

        self.assertEqual(initialization_result, 0)
        self.assertIn("Initialized CodeStable workspace", initialization_output.getvalue())
        self.assertEqual(
            snapshot_directory_tree(issues_root),
            issue_workspace_before_initialization,
        )

    def test_create_task_rejects_an_empty_plan(self) -> None:
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "at least one committed step"):
            task_runtime.create_task(
                root=self.root,
                task="empty-plan",
                goal="Reject empty plans",
                workflow="feature",
                owner="cs",
                steps=[],
                related_docs=[],
                current_date="2026-07-29",
            )

    def test_create_task_rejects_archive_as_a_work_step(self) -> None:
        lifecycle_step_titles = (
            "归档",
            "执行归档",
            "将 Task 归档",
            "归档当前 Task",
            "归档并清理 Task",
            "Archive",
            "Archive Task",
            "Archive evidence",
            "Move task to archive",
            "Finalize Task archival",
        )
        for step_index, lifecycle_step_title in enumerate(lifecycle_step_titles):
            with self.subTest(lifecycle_step_title=lifecycle_step_title):
                with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "archive lifecycle"):
                    task_runtime.create_task(
                        root=self.root,
                        task=f"archive-step-{step_index}",
                        goal="Reject lifecycle-only work",
                        workflow="feature",
                        owner="cs",
                        steps=[lifecycle_step_title],
                        related_docs=[],
                        current_date="2026-07-29",
                    )

        analytical_task_path = task_runtime.create_task(
            root=self.root,
            task="analyze-archive-policy",
            goal="Analyze historical archive policy",
            workflow="explore",
            owner="cs",
            steps=[
                "分析历史归档策略",
                "Analyze archive recovery behavior",
                "Archive strategy analysis",
            ],
            related_docs=[],
            current_date="2026-07-29",
        )
        self.assertTrue(analytical_task_path.is_file())

    def test_task_validation_rejects_duplicate_frontmatter_fields(self) -> None:
        active_path = self.create_task("duplicate-field")
        invalid_content = active_path.read_text(encoding="utf-8").replace(
            "status: active",
            "status: active\nstatus: blocked",
            1,
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "duplicate field"):
            task_runtime.validate_task_document(invalid_content, "duplicate-field")

    def test_write_active_requires_matching_content_hash(self) -> None:
        active_path = self.create_task("compare-and-swap")
        expected_sha256 = task_runtime.calculate_sha256(active_path)
        candidate_path = self.root / "candidate.md"
        candidate_path.write_text(
            active_path.read_text(encoding="utf-8").replace(
                "goal: Deliver a traceable change",
                "goal: Deliver an updated traceable change",
                1,
            ),
            encoding="utf-8",
        )

        task_runtime.write_active_task(
            root=self.root,
            task="compare-and-swap",
            content_path=candidate_path,
            expected_sha256=expected_sha256,
        )
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "content changed"):
            task_runtime.write_active_task(
                root=self.root,
                task="compare-and-swap",
                content_path=candidate_path,
                expected_sha256=expected_sha256,
            )

    def test_create_never_overwrites_a_target_that_appears_during_publication(self) -> None:
        active_path = self.root.resolve() / "codestable/tasks/active/exclusive-create.md"
        original_publish = task_runtime.publish_active_task_without_overwrite

        def create_conflict_before_publish(source_path: Path, destination_path: Path) -> None:
            destination_path.write_text("concurrent active evidence", encoding="utf-8")
            original_publish(source_path, destination_path)

        task_runtime.publish_active_task_without_overwrite = create_conflict_before_publish
        try:
            with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "evidence was preserved"):
                task_runtime.create_task(
                    root=self.root,
                    task="exclusive-create",
                    goal="Preserve concurrent Task evidence",
                    workflow="feature",
                    owner="cs",
                    steps=["Implement and verify"],
                    related_docs=[],
                    current_date="2026-07-29",
                )
        finally:
            task_runtime.publish_active_task_without_overwrite = original_publish

        self.assertEqual(
            active_path.read_text(encoding="utf-8"),
            "concurrent active evidence",
        )

    def test_update_records_progress_and_preserves_the_plan(self) -> None:
        active_path = self.create_task("progress-update")

        task_runtime.update_task(
            root=self.root,
            task="progress-update",
            expected_sha256=task_runtime.calculate_sha256(active_path),
            replacements={
                "- [ ] Inspect current behavior": "- [x] Inspect current behavior",
                "### 1. Inspect current behavior\n\n- 状态：pending": (
                    "### 1. Inspect current behavior\n\n- 状态：done"
                ),
            },
            progress_record="Completed the inspection batch.",
            current_date="2026-07-29",
        )

        updated_content = active_path.read_text(encoding="utf-8")
        self.assertIn("- [x] Inspect current behavior", updated_content)
        self.assertIn("Completed the inspection batch.", updated_content)

    def test_update_supports_a_record_only_evidence_batch(self) -> None:
        active_path = self.create_task("record-only-update")

        task_runtime.update_task(
            root=self.root,
            task="record-only-update",
            expected_sha256=task_runtime.calculate_sha256(active_path),
            replacements={},
            progress_record="Completed an evidence-only review batch.",
            current_date="2026-07-29",
        )

        updated_content = active_path.read_text(encoding="utf-8")
        self.assertIn("Completed an evidence-only review batch.", updated_content)
        self.assertIn("- [ ] Inspect current behavior", updated_content)

    def test_write_active_rejects_removing_committed_steps(self) -> None:
        active_path = self.create_task("preserve-plan")
        candidate_content = active_path.read_text(encoding="utf-8").replace(
            "- [ ] Implement and verify\n",
            "",
            1,
        ).replace(
            "\n\n### 2. Implement and verify\n\n- 状态：pending",
            "",
            1,
        )
        candidate_path = self.root / "candidate.md"
        candidate_path.write_text(candidate_content, encoding="utf-8")

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "cannot remove"):
            task_runtime.write_active_task(
                root=self.root,
                task="preserve-plan",
                content_path=candidate_path,
                expected_sha256=task_runtime.calculate_sha256(active_path),
            )

    def test_task_validation_rejects_unrecognized_execution_status(self) -> None:
        active_path = self.create_task("invalid-step-status")
        invalid_content = active_path.read_text(encoding="utf-8").replace(
            "- 状态：pending",
            "- 状态：skipped",
            1,
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "status is invalid"):
            task_runtime.validate_task_document(invalid_content, "invalid-step-status")

    def test_task_validation_rejects_mismatched_plan_views(self) -> None:
        active_path = self.create_task("mismatched-plan")
        invalid_content = active_path.read_text(encoding="utf-8").replace(
            "### 2. Implement and verify",
            "### 2. Verify only",
            1,
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "titles must match"):
            task_runtime.validate_task_document(invalid_content, "mismatched-plan")

    def test_task_validation_rejects_body_status_drift(self) -> None:
        active_path = self.create_task("body-status-drift")
        invalid_content = active_path.read_text(encoding="utf-8").replace(
            "## 2. 当前状态\n\nactive",
            "## 2. 当前状态\n\ncompleted",
            1,
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "current status section"):
            task_runtime.validate_task_document(invalid_content, "body-status-drift")

    def test_task_validation_rejects_invalid_owner_and_dates(self) -> None:
        active_path = self.create_task("invalid-schema")
        valid_content = active_path.read_text(encoding="utf-8")
        invalid_documents = (
            (valid_content.replace("owner_skill: cs", "owner_skill: another-skill", 1), "owner_skill"),
            (valid_content.replace("created: 2026-07-29", "created: not-a-date", 1), "Invalid date"),
            (valid_content.replace("updated: 2026-07-29", "updated: 2026-99-99", 1), "Invalid date"),
        )
        for invalid_content, expected_error in invalid_documents:
            with self.subTest(expected_error=expected_error):
                with self.assertRaisesRegex(task_runtime.TaskRuntimeError, expected_error):
                    task_runtime.validate_task_document(invalid_content, "invalid-schema")

    def test_task_validation_rejects_unknown_fields_and_progress_drift(self) -> None:
        active_path = self.create_task("closed-schema")
        valid_content = active_path.read_text(encoding="utf-8")
        unknown_field_content = valid_content.replace(
            "goal: Deliver a traceable change",
            "goal: Deliver a traceable change\nunknown_field: forbidden",
            1,
        )
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "unknown fields"):
            task_runtime.validate_task_document(unknown_field_content, "closed-schema")

        progress_drift_content = valid_content.replace(
            "- [ ] Inspect current behavior",
            "- [x] Inspect current behavior",
            1,
        )
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "status must agree"):
            task_runtime.validate_task_document(progress_drift_content, "closed-schema")

    def test_task_validation_rejects_duplicate_fixed_sections(self) -> None:
        active_path = self.create_task("duplicate-section")
        invalid_content = active_path.read_text(encoding="utf-8").replace(
            "## 7. 完成与归档记录",
            "## 1. 任务目标\n\nDuplicate.\n\n## 7. 完成与归档记录",
            1,
        )
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "duplicate section"):
            task_runtime.validate_task_document(invalid_content, "duplicate-section")

    def test_task_validation_rejects_extra_or_reordered_sections(self) -> None:
        active_path = self.create_task("fixed-section-order")
        valid_content = active_path.read_text(encoding="utf-8")
        extra_section_content = valid_content.replace(
            "## 7. 完成与归档记录",
            "## 8. Hidden state\n\nForbidden.\n\n## 7. 完成与归档记录",
            1,
        )
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "exactly match"):
            task_runtime.validate_task_document(extra_section_content, "fixed-section-order")

        first_section_start = valid_content.index("## 1. 任务目标")
        second_section_start = valid_content.index("## 2. 当前状态")
        first_section = valid_content[first_section_start:second_section_start]
        reordered_content = (
            valid_content[:first_section_start]
            + valid_content[second_section_start:]
            + "\n"
            + first_section
        )
        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "exactly match"):
            task_runtime.validate_task_document(reordered_content, "fixed-section-order")

    def test_complete_rejects_unfinished_work(self) -> None:
        active_path = self.create_task("pending-completion")

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "unfinished work"):
            task_runtime.complete_task(
                root=self.root,
                task="pending-completion",
                expected_sha256=task_runtime.calculate_sha256(active_path),
                current_date="2026-07-29",
            )

    def test_completed_task_is_frozen_until_archive(self) -> None:
        active_path = self.create_task("terminal-freeze")
        self.complete_task("terminal-freeze")
        candidate_path = self.root / "candidate.md"
        candidate_path.write_text(
            active_path.read_text(encoding="utf-8").replace(
                "Deliver a traceable change",
                "Rewrite completed evidence",
                1,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "frozen"):
            task_runtime.write_active_task(
                root=self.root,
                task="terminal-freeze",
                content_path=candidate_path,
                expected_sha256=task_runtime.calculate_sha256(active_path),
            )

    def test_duplicate_active_and_archived_state_blocks_all_active_mutations(self) -> None:
        active_path = self.create_task("duplicate-mutation")
        self.complete_task("duplicate-mutation")
        completed_content = active_path.read_text(encoding="utf-8")
        archive_path = self.root / "codestable/tasks/archived/2026-07-29-001-duplicate-mutation.md"
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(
            task_runtime.render_archived_task_content(completed_content, "2026-07-29"),
            encoding="utf-8",
        )
        active_path.write_text(completed_content, encoding="utf-8")

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "both active and archived"):
            task_runtime.update_task(
                root=self.root,
                task="duplicate-mutation",
                expected_sha256=task_runtime.calculate_sha256(active_path),
                replacements={"Completed all planned steps": "Completed all planned work"},
                progress_record="Must be rejected.",
                current_date="2026-07-29",
            )

    def test_explicit_status_command_enforces_block_and_resume_transitions(self) -> None:
        active_path = self.create_task("status-command")

        task_runtime.set_task_status(
            root=self.root,
            task="status-command",
            target_status="blocked",
            expected_sha256=task_runtime.calculate_sha256(active_path),
            reason="External service is temporarily unavailable.",
            current_date="2026-07-29",
        )
        task_runtime.set_task_status(
            root=self.root,
            task="status-command",
            target_status="active",
            expected_sha256=task_runtime.calculate_sha256(active_path),
            reason="A local equivalent verification became available.",
            current_date="2026-07-29",
        )
        self.assertIn("status: active", active_path.read_text(encoding="utf-8"))

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "must change"):
            task_runtime.set_task_status(
                root=self.root,
                task="status-command",
                target_status="active",
                expected_sha256=task_runtime.calculate_sha256(active_path),
                reason="A repeated status command must fail closed.",
                current_date="2026-07-29",
            )

    def test_archive_requires_the_completed_source_hash(self) -> None:
        active_path = self.create_task("archive-cas")
        self.complete_task("archive-cas")

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "changed after it was read"):
            task_runtime.archive_task(
                root=self.root,
                task="archive-cas",
                archive_date="2026-07-29",
                expected_sha256="0" * 64,
            )
        self.assertTrue(active_path.exists())

    def test_archive_atomically_moves_completed_task(self) -> None:
        active_path = self.create_task("archive-closure")
        self.complete_task("archive-closure")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="archive-closure",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )

        archived_path = self.root / archive_result.archived_path
        self.assertFalse(active_path.exists())
        self.assertTrue(archived_path.is_file())
        self.assertIn("status: archived", archived_path.read_text(encoding="utf-8"))
        self.assertEqual(task_runtime.cleanup_task(self.root, "archive-closure"), [])

        replay_result = task_runtime.archive_task(
            root=self.root,
            task="archive-closure",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )
        self.assertEqual(replay_result, archive_result)

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "expected retry snapshot"):
            task_runtime.archive_task(
                root=self.root,
                task="archive-closure",
                archive_date="2026-07-29",
                expected_sha256="0" * 64,
            )

    def test_archive_assigns_incrementing_daily_sequences(self) -> None:
        first_active_path = self.create_task("first-daily-task")
        self.complete_task("first-daily-task")
        first_result = task_runtime.archive_task(
            root=self.root,
            task="first-daily-task",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(first_active_path),
        )

        second_active_path = self.create_task("second-daily-task")
        self.complete_task("second-daily-task")
        second_result = task_runtime.archive_task(
            root=self.root,
            task="second-daily-task",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(second_active_path),
        )

        third_active_path = self.create_task("third-daily-task")
        self.complete_task("third-daily-task")
        third_result = task_runtime.archive_task(
            root=self.root,
            task="third-daily-task",
            archive_date="2026-07-30",
            expected_sha256=task_runtime.calculate_sha256(third_active_path),
        )

        self.assertEqual(
            first_result.archived_path,
            "codestable/tasks/archived/2026-07-29-001-first-daily-task.md",
        )
        self.assertEqual(
            second_result.archived_path,
            "codestable/tasks/archived/2026-07-29-002-second-daily-task.md",
        )
        self.assertEqual(
            third_result.archived_path,
            "codestable/tasks/archived/2026-07-30-001-third-daily-task.md",
        )

    def test_scan_reports_noncanonical_archive_and_cleanup_preserves_active(self) -> None:
        active_path = self.create_task("legacy-archive-evidence")
        self.complete_task("legacy-archive-evidence")
        archived_root = self.root / "codestable/tasks/archived"
        legacy_archive_path = archived_root / "2026-07-29-legacy-archive-evidence.md"
        legacy_archive_path.write_text(
            task_runtime.render_archived_task_content(
                active_path.read_text(encoding="utf-8"),
                "2026-07-29",
            ),
            encoding="utf-8",
        )

        scan_result = task_runtime.scan_tasks(self.root)
        cleanup_findings = task_runtime.cleanup_task(
            self.root,
            "legacy-archive-evidence",
        )

        self.assertIn(
            "invalid-archived-task",
            {finding.code for finding in scan_result.findings},
        )
        self.assertIn(
            "invalid-archived-task",
            {finding.code for finding in cleanup_findings},
        )
        self.assertTrue(active_path.exists())

    def test_cleanup_preserves_active_when_archived_contains_a_symlink(self) -> None:
        active_path = self.create_task("symlink-archive-evidence")
        self.complete_task("symlink-archive-evidence")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="symlink-archive-evidence",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        archived_path = self.root / archive_result.archived_path
        active_path.write_bytes(archived_path.read_bytes())
        (archived_path.parent / "unexpected-archive-link.md").symlink_to(archived_path)

        findings = task_runtime.cleanup_task(self.root, "symlink-archive-evidence")

        self.assertIn("invalid-archived-task", {finding.code for finding in findings})
        self.assertTrue(active_path.exists())

    def test_cleanup_reports_unexpected_active_workspace_entry(self) -> None:
        active_path = self.create_task("unexpected-active-entry")
        self.complete_task("unexpected-active-entry")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="unexpected-active-entry",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        unexpected_entry = self.root / "codestable/tasks/active/runtime-residue.tmp"
        unexpected_entry.write_text("runtime residue", encoding="utf-8")

        findings = task_runtime.cleanup_task(self.root, "unexpected-active-entry")

        self.assertIn("unexpected-active-entry", {finding.code for finding in findings})
        self.assertTrue((self.root / archive_result.archived_path).exists())

    def test_migrate_archive_filenames_migrates_an_unambiguous_legacy_archive(self) -> None:
        active_path = self.create_task("migrate-legacy-archive")
        self.complete_task("migrate-legacy-archive")
        archived_root = self.root / "codestable/tasks/archived"
        legacy_path = archived_root / "2026-07-29-migrate-legacy-archive.md"
        legacy_path.write_text(
            task_runtime.render_archived_task_content(
                active_path.read_text(encoding="utf-8"),
                "2026-07-29",
            ),
            encoding="utf-8",
        )
        active_path.unlink()

        migration_result = task_runtime.migrate_legacy_archive_filenames(self.root)

        self.assertEqual(
            migration_result,
            [
                {
                    "from": "codestable/tasks/archived/2026-07-29-migrate-legacy-archive.md",
                    "to": "codestable/tasks/archived/2026-07-29-001-migrate-legacy-archive.md",
                }
            ],
        )
        self.assertFalse(legacy_path.exists())
        self.assertFalse(task_runtime.scan_tasks(self.root).findings)

    def test_migrate_archive_filenames_disambiguates_numeric_task_slug(self) -> None:
        active_path = self.create_task("001-numeric-task")
        self.complete_task("001-numeric-task")
        archived_root = self.root / "codestable/tasks/archived"
        legacy_path = archived_root / "2026-07-29-001-numeric-task.md"
        legacy_path.write_text(
            task_runtime.render_archived_task_content(
                active_path.read_text(encoding="utf-8"),
                "2026-07-29",
            ),
            encoding="utf-8",
        )
        active_path.unlink()

        migration_result = task_runtime.migrate_legacy_archive_filenames(self.root)

        self.assertEqual(
            migration_result[0]["to"],
            "codestable/tasks/archived/2026-07-29-001-001-numeric-task.md",
        )
        self.assertFalse(task_runtime.scan_tasks(self.root).findings)

    def test_migrate_archive_filenames_rejects_ambiguous_legacy_archive_order(self) -> None:
        archived_root = self.root / "codestable/tasks/archived"
        archived_root.mkdir(parents=True, exist_ok=True)
        completed_active_paths = []
        for task in ("legacy-first", "legacy-second"):
            active_path = self.create_task(task)
            self.complete_task(task)
            completed_active_paths.append((task, active_path))
        for task, active_path in completed_active_paths:
            legacy_path = archived_root / f"2026-07-29-{task}.md"
            legacy_path.write_text(
                task_runtime.render_archived_task_content(
                    active_path.read_text(encoding="utf-8"),
                    "2026-07-29",
                ),
                encoding="utf-8",
            )
            active_path.unlink()

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "cannot infer completion order"):
            task_runtime.migrate_legacy_archive_filenames(self.root)

    def test_scan_reports_duplicate_and_noncontiguous_daily_sequences(self) -> None:
        first_active_path = self.create_task("duplicate-sequence-a")
        self.complete_task("duplicate-sequence-a")
        first_result = task_runtime.archive_task(
            root=self.root,
            task="duplicate-sequence-a",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(first_active_path),
        )
        second_active_path = self.create_task("duplicate-sequence-b")
        self.complete_task("duplicate-sequence-b")
        second_result = task_runtime.archive_task(
            root=self.root,
            task="duplicate-sequence-b",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(second_active_path),
        )
        second_archived_path = self.root / second_result.archived_path
        duplicate_sequence_path = second_archived_path.with_name(
            "2026-07-29-001-duplicate-sequence-b.md"
        )
        second_archived_path.rename(duplicate_sequence_path)

        duplicate_scan_result = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "duplicate-daily-archive-sequence",
            {finding.code for finding in duplicate_scan_result.findings},
        )

        first_archived_path = self.root / first_result.archived_path
        first_archived_path.rename(
            first_archived_path.with_name("2026-07-29-003-duplicate-sequence-a.md")
        )
        noncontiguous_scan_result = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "noncontiguous-daily-archive-sequence",
            {finding.code for finding in noncontiguous_scan_result.findings},
        )

    def test_archive_rejects_a_noncontiguous_daily_sequence_workspace(self) -> None:
        active_path = self.create_task("blocked-by-sequence-gap")
        self.complete_task("blocked-by-sequence-gap")
        archived_root = self.root / "codestable/tasks/archived"
        archived_root.mkdir(parents=True, exist_ok=True)
        (archived_root / "2026-07-29-002-existing-task.md").write_text(
            "reserved archive evidence",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "contiguous sequences"):
            task_runtime.archive_task(
                root=self.root,
                task="blocked-by-sequence-gap",
                archive_date="2026-07-29",
                expected_sha256=task_runtime.calculate_sha256(active_path),
            )

    def test_archive_rejects_daily_sequence_overflow(self) -> None:
        archived_root = self.root / "codestable/tasks/archived"
        archived_root.mkdir(parents=True, exist_ok=True)
        original_maximum_sequence = task_runtime.MAX_DAILY_ARCHIVE_SEQUENCE
        task_runtime.MAX_DAILY_ARCHIVE_SEQUENCE = 2
        try:
            for sequence in (1, 2):
                (archived_root / f"2026-07-29-{sequence:03d}-existing-{sequence}.md").write_text(
                    "reserved archive evidence",
                    encoding="utf-8",
                )
            task_paths = task_runtime.build_task_paths(self.root, "overflow-task")
            with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "maximum 2 Tasks"):
                task_runtime.allocate_daily_archive_path(task_paths, "2026-07-29")
        finally:
            task_runtime.MAX_DAILY_ARCHIVE_SEQUENCE = original_maximum_sequence

    def test_cleanup_removes_recreated_source_when_archive_proves_its_hash(self) -> None:
        active_path = self.create_task("cleanup-recreated-source")
        self.complete_task("cleanup-recreated-source")
        completed_source_content = active_path.read_text(encoding="utf-8")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-recreated-source",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )

        active_path.write_text(completed_source_content, encoding="utf-8")

        self.assertEqual(task_runtime.cleanup_task(self.root, "cleanup-recreated-source"), [])
        self.assertFalse(active_path.exists())
        self.assertTrue((self.root / archive_result.archived_path).exists())
        self.assertFalse(task_runtime.scan_tasks(self.root).findings)

    def test_cleanup_preserves_divergent_active_evidence(self) -> None:
        active_path = self.create_task("cleanup-divergent-source")
        self.complete_task("cleanup-divergent-source")
        completed_source_content = active_path.read_text(encoding="utf-8")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-divergent-source",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )
        archived_path = self.root / archive_result.archived_path

        active_path.write_text(
            completed_source_content.replace(
                "Deliver a traceable change",
                "Divergent active evidence",
                1,
            ),
            encoding="utf-8",
        )

        findings = task_runtime.cleanup_task(self.root, "cleanup-divergent-source")

        self.assertEqual(
            {finding.code for finding in findings},
            {"duplicate-task-state"},
        )
        self.assertTrue(active_path.exists())
        self.assertTrue(archived_path.exists())

    def test_cleanup_removes_recreated_archived_content(self) -> None:
        active_path = self.create_task("cleanup-archived-content")
        self.complete_task("cleanup-archived-content")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-archived-content",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        archived_path = self.root / archive_result.archived_path
        active_path.write_bytes(archived_path.read_bytes())

        self.assertEqual(task_runtime.cleanup_task(self.root, "cleanup-archived-content"), [])
        self.assertFalse(active_path.exists())
        self.assertTrue(archived_path.exists())

    def test_cleanup_preserves_active_when_archive_is_invalid(self) -> None:
        active_path = self.create_task("cleanup-invalid-archive")
        self.complete_task("cleanup-invalid-archive")
        completed_source_content = active_path.read_text(encoding="utf-8")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-invalid-archive",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        archived_path = self.root / archive_result.archived_path
        archived_path.write_text("invalid archived content", encoding="utf-8")

        findings = task_runtime.cleanup_task(self.root, "cleanup-invalid-archive")

        self.assertIn("invalid-archived-task", {finding.code for finding in findings})
        self.assertIn("duplicate-task-state", {finding.code for finding in findings})
        self.assertTrue(active_path.exists())

    def test_cleanup_preserves_active_when_multiple_archives_exist(self) -> None:
        active_path = self.create_task("cleanup-multiple-archives")
        self.complete_task("cleanup-multiple-archives")
        completed_source_content = active_path.read_text(encoding="utf-8")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-multiple-archives",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        archived_path = self.root / archive_result.archived_path
        second_archived_path = archived_path.with_name(
            "2026-07-30-001-cleanup-multiple-archives.md"
        )
        second_archived_path.write_text(
            archived_path.read_text(encoding="utf-8").replace(
                "updated: 2026-07-29",
                "updated: 2026-07-30",
                1,
            ).replace(
                "archived: 2026-07-29",
                "archived: 2026-07-30",
                1,
            ),
            encoding="utf-8",
        )

        findings = task_runtime.cleanup_task(self.root, "cleanup-multiple-archives")

        self.assertIn("multiple-archives", {finding.code for finding in findings})
        self.assertIn("duplicate-task-state", {finding.code for finding in findings})
        self.assertTrue(active_path.exists())

    def test_cleanup_preserves_a_new_active_written_during_cleanup(self) -> None:
        active_path = self.create_task("cleanup-concurrent-active")
        self.complete_task("cleanup-concurrent-active")
        completed_source_content = active_path.read_text(encoding="utf-8")
        task_runtime.archive_task(
            root=self.root,
            task="cleanup-concurrent-active",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        original_move_to_quarantine = task_runtime.move_active_task_to_quarantine

        def replace_active_after_quarantine(task_paths):
            quarantine_path = original_move_to_quarantine(task_paths)
            active_path.write_text("new divergent active evidence", encoding="utf-8")
            return quarantine_path

        task_runtime.move_active_task_to_quarantine = replace_active_after_quarantine
        try:
            findings = task_runtime.cleanup_task(self.root, "cleanup-concurrent-active")
        finally:
            task_runtime.move_active_task_to_quarantine = original_move_to_quarantine

        self.assertIn("duplicate-task-state", {finding.code for finding in findings})
        self.assertEqual(
            active_path.read_text(encoding="utf-8"),
            "new divergent active evidence",
        )

    def test_cleanup_restores_active_when_archive_changes_during_cleanup(self) -> None:
        active_path = self.create_task("cleanup-concurrent-archive")
        self.complete_task("cleanup-concurrent-archive")
        completed_source_content = active_path.read_text(encoding="utf-8")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-concurrent-archive",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        archived_path = self.root / archive_result.archived_path
        original_move_to_quarantine = task_runtime.move_active_task_to_quarantine

        def invalidate_archive_after_quarantine(task_paths):
            quarantine_path = original_move_to_quarantine(task_paths)
            archived_path.write_text("invalid archived content", encoding="utf-8")
            return quarantine_path

        task_runtime.move_active_task_to_quarantine = invalidate_archive_after_quarantine
        try:
            findings = task_runtime.cleanup_task(self.root, "cleanup-concurrent-archive")
        finally:
            task_runtime.move_active_task_to_quarantine = original_move_to_quarantine

        self.assertIn("duplicate-task-state", {finding.code for finding in findings})
        self.assertEqual(active_path.read_text(encoding="utf-8"), completed_source_content)

    def test_cleanup_preserves_replaced_quarantine_evidence(self) -> None:
        active_path = self.create_task("cleanup-replaced-quarantine")
        self.complete_task("cleanup-replaced-quarantine")
        completed_source_content = active_path.read_text(encoding="utf-8")
        task_runtime.archive_task(
            root=self.root,
            task="cleanup-replaced-quarantine",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        original_unlink_if_current = task_runtime.unlink_file_if_snapshot_is_current

        def replace_quarantine_before_unlink(path, expected_identity, expected_sha256):
            task_runtime.atomic_write_text(path, "new divergent quarantine evidence")
            return original_unlink_if_current(path, expected_identity, expected_sha256)

        task_runtime.unlink_file_if_snapshot_is_current = replace_quarantine_before_unlink
        try:
            findings = task_runtime.cleanup_task(self.root, "cleanup-replaced-quarantine")
        finally:
            task_runtime.unlink_file_if_snapshot_is_current = original_unlink_if_current

        self.assertIn("duplicate-task-state", {finding.code for finding in findings})
        self.assertEqual(
            active_path.read_text(encoding="utf-8"),
            "new divergent quarantine evidence",
        )

    def test_cleanup_preserves_active_when_a_second_archive_appears(self) -> None:
        active_path = self.create_task("cleanup-concurrent-second-archive")
        self.complete_task("cleanup-concurrent-second-archive")
        completed_source_content = active_path.read_text(encoding="utf-8")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="cleanup-concurrent-second-archive",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        archived_path = self.root / archive_result.archived_path
        second_archived_path = archived_path.with_name(
            "2026-07-30-001-cleanup-concurrent-second-archive.md"
        )
        original_move_to_quarantine = task_runtime.move_active_task_to_quarantine

        def add_second_archive_after_quarantine(task_paths):
            quarantine_path = original_move_to_quarantine(task_paths)
            second_archived_path.write_bytes(archived_path.read_bytes())
            return quarantine_path

        task_runtime.move_active_task_to_quarantine = add_second_archive_after_quarantine
        try:
            findings = task_runtime.cleanup_task(
                self.root,
                "cleanup-concurrent-second-archive",
            )
        finally:
            task_runtime.move_active_task_to_quarantine = original_move_to_quarantine

        self.assertIn("duplicate-task-state", {finding.code for finding in findings})
        self.assertEqual(active_path.read_text(encoding="utf-8"), completed_source_content)

    def test_quarantine_move_failure_removes_empty_placeholder(self) -> None:
        active_path = self.create_task("cleanup-move-failure")
        task_paths = task_runtime.build_task_paths(self.root, "cleanup-move-failure")
        original_replace = task_runtime.os.replace

        def reject_quarantine_move(source_path, destination_path):
            raise PermissionError("simulated move failure")

        task_runtime.os.replace = reject_quarantine_move
        try:
            with self.assertRaisesRegex(PermissionError, "simulated move failure"):
                task_runtime.move_active_task_to_quarantine(task_paths)
        finally:
            task_runtime.os.replace = original_replace

        self.assertEqual(list(task_paths.active_root.iterdir()), [active_path])

    def test_archive_replay_removes_a_recreated_proven_source(self) -> None:
        active_path = self.create_task("replay-recreated-source")
        self.complete_task("replay-recreated-source")
        completed_source_content = active_path.read_text(encoding="utf-8")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="replay-recreated-source",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )
        active_path.write_text(completed_source_content, encoding="utf-8")

        replay_result = task_runtime.archive_task(
            root=self.root,
            task="replay-recreated-source",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )

        self.assertEqual(replay_result, archive_result)
        self.assertFalse(active_path.exists())
        self.assertFalse(task_runtime.scan_tasks(self.root).findings)

    def test_archive_replay_preserves_a_new_active_written_during_cleanup(self) -> None:
        active_path = self.create_task("replay-concurrent-active")
        self.complete_task("replay-concurrent-active")
        completed_source_content = active_path.read_text(encoding="utf-8")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        task_runtime.archive_task(
            root=self.root,
            task="replay-concurrent-active",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        original_move_to_quarantine = task_runtime.move_active_task_to_quarantine

        def replace_active_after_quarantine(task_paths):
            quarantine_path = original_move_to_quarantine(task_paths)
            active_path.write_text("new divergent active evidence", encoding="utf-8")
            return quarantine_path

        task_runtime.move_active_task_to_quarantine = replace_active_after_quarantine
        try:
            with self.assertRaisesRegex(
                task_runtime.TaskRuntimeError,
                "both active and archived",
            ):
                task_runtime.archive_task(
                    root=self.root,
                    task="replay-concurrent-active",
                    archive_date="2026-07-29",
                    expected_sha256=completed_source_sha256,
                )
        finally:
            task_runtime.move_active_task_to_quarantine = original_move_to_quarantine

        self.assertEqual(
            active_path.read_text(encoding="utf-8"),
            "new divergent active evidence",
        )

    def test_archive_replay_preserves_active_when_archive_is_invalid(self) -> None:
        active_path = self.create_task("replay-invalid-archive")
        self.complete_task("replay-invalid-archive")
        completed_source_content = active_path.read_text(encoding="utf-8")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="replay-invalid-archive",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        archived_path = self.root / archive_result.archived_path
        archived_path.write_text("invalid archived content", encoding="utf-8")

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "missing YAML"):
            task_runtime.archive_task(
                root=self.root,
                task="replay-invalid-archive",
                archive_date="2026-07-29",
                expected_sha256=completed_source_sha256,
            )

        self.assertEqual(active_path.read_text(encoding="utf-8"), completed_source_content)

    def test_archive_replay_preserves_active_when_multiple_archives_exist(self) -> None:
        active_path = self.create_task("replay-multiple-archives")
        self.complete_task("replay-multiple-archives")
        completed_source_content = active_path.read_text(encoding="utf-8")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="replay-multiple-archives",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )
        active_path.write_text(completed_source_content, encoding="utf-8")
        archived_path = self.root / archive_result.archived_path
        second_archived_path = archived_path.with_name(
            "2026-07-30-001-replay-multiple-archives.md"
        )
        second_archived_path.write_bytes(archived_path.read_bytes())

        with self.assertRaisesRegex(
            task_runtime.TaskRuntimeError,
            "more than one archived document",
        ):
            task_runtime.archive_task(
                root=self.root,
                task="replay-multiple-archives",
                archive_date="2026-07-29",
                expected_sha256=completed_source_sha256,
            )

        self.assertEqual(active_path.read_text(encoding="utf-8"), completed_source_content)

    def test_initial_archive_preserves_active_created_after_publication(self) -> None:
        active_path = self.create_task("archive-concurrent-active")
        self.complete_task("archive-concurrent-active")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        original_publish = task_runtime.publish_archive_without_overwrite

        def publish_then_create_new_active(source_path: Path, destination_path: Path) -> None:
            original_publish(source_path, destination_path)
            active_path.write_text("new divergent active evidence", encoding="utf-8")

        task_runtime.publish_archive_without_overwrite = publish_then_create_new_active
        try:
            with self.assertRaisesRegex(
                task_runtime.TaskRuntimeError,
                "archive cleanup failed",
            ):
                task_runtime.archive_task(
                    root=self.root,
                    task="archive-concurrent-active",
                    archive_date="2026-07-29",
                    expected_sha256=completed_source_sha256,
                )
        finally:
            task_runtime.publish_archive_without_overwrite = original_publish

        self.assertEqual(
            active_path.read_text(encoding="utf-8"),
            "new divergent active evidence",
        )
        self.assertTrue(
            (self.root / "codestable/tasks/archived/2026-07-29-001-archive-concurrent-active.md")
            .is_file()
        )

    def test_archive_retry_ignores_forged_source_hash_markers(self) -> None:
        active_path = self.create_task("forged-archive-source")
        task_runtime.update_task(
            root=self.root,
            task="forged-archive-source",
            expected_sha256=task_runtime.calculate_sha256(active_path),
            replacements={},
            progress_record=f"Untrusted marker: 源快照 SHA-256：{'0' * 64}",
            current_date="2026-07-29",
        )
        self.complete_task("forged-archive-source")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        task_runtime.archive_task(
            root=self.root,
            task="forged-archive-source",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )

        with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "expected retry snapshot"):
            task_runtime.archive_task(
                root=self.root,
                task="forged-archive-source",
                archive_date="2026-07-29",
                expected_sha256="0" * 64,
            )

    def test_scan_reports_missing_or_symlink_task_workspace(self) -> None:
        missing_scan = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "missing-task-workspace",
            {finding.code for finding in missing_scan.findings},
        )

        task_root = self.root / "codestable/tasks"
        task_root.mkdir(parents=True)
        external_root = self.root / "external-tasks"
        external_root.mkdir()
        (task_root / "active").symlink_to(external_root, target_is_directory=True)
        (task_root / "archived").mkdir()
        symlink_scan = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "unsafe-task-workspace",
            {finding.code for finding in symlink_scan.findings},
        )

    def test_scan_and_initializer_reject_ancestor_workspace_symlinks(self) -> None:
        project_root = self.root / "project"
        project_root.mkdir()
        external_workspace = self.root / "external-workspace"
        (external_workspace / "tasks/active").mkdir(parents=True)
        (external_workspace / "tasks/archived").mkdir()
        (project_root / "codestable").symlink_to(external_workspace, target_is_directory=True)

        scan_result = task_runtime.scan_tasks(project_root)
        self.assertIn(
            "unsafe-task-workspace",
            {finding.code for finding in scan_result.findings},
        )
        with self.assertRaisesRegex(ValueError, "contains a symlink"):
            initializer.init_codestable(project_root, force=False, migrate_legacy=False)

    def test_scan_rejects_unexpected_workspace_entries(self) -> None:
        self.create_task("strict-workspace")
        task_root = self.root.resolve() / "codestable/tasks"
        (task_root / "locks").mkdir()
        (task_root / "active/hidden-task.txt").write_text("hidden", encoding="utf-8")
        (task_root / "archived/nested").mkdir()

        scan_result = task_runtime.scan_tasks(self.root)
        finding_codes = {finding.code for finding in scan_result.findings}
        self.assertIn("unexpected-task-workspace-entry", finding_codes)
        self.assertIn("unexpected-active-entry", finding_codes)
        self.assertIn("unexpected-archived-entry", finding_codes)

    def test_initializer_rejects_non_file_canonical_indexes(self) -> None:
        project_root = self.root / "invalid-index-project"
        (project_root / "codestable/vision/index.md").mkdir(parents=True)
        (project_root / "codestable/spec/index.md").mkdir(parents=True)

        with self.assertRaisesRegex(ValueError, "not a regular file"):
            initializer.init_codestable(project_root, force=False, migrate_legacy=False)

    def test_scan_cli_fails_on_findings_and_create_reports_unattended_mode(self) -> None:
        empty_root = self.root / "empty-project"
        empty_root.mkdir()
        failed_scan = subprocess.run(
            ["python3", str(RUNTIME_PATH), "--root", str(empty_root), "scan"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(failed_scan.returncode, 1)
        self.assertTrue(json.loads(failed_scan.stdout)["findings"])

        created_root = self.root / "created-project"
        created_root.mkdir()
        create_result = subprocess.run(
            [
                "python3",
                str(RUNTIME_PATH),
                "--root",
                str(created_root),
                "create",
                "--task",
                "unattended-create",
                "--goal",
                "Continue without another question",
                "--workflow",
                "feature",
                "--step",
                "Implement and verify",
                "--date",
                "2026-07-29",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(create_result.returncode, 0)
        create_payload = json.loads(create_result.stdout)
        self.assertTrue(create_payload["plan_committed"])
        self.assertEqual(create_payload["execution_mode"], "unattended")
        self.assertFalse(create_payload["ordinary_questions_allowed"])
        self.assertTrue(create_payload["necessary_clarification_or_authorization_allowed"])

        update_result = subprocess.run(
            [
                "python3",
                str(RUNTIME_PATH),
                "--root",
                str(created_root),
                "update",
                "--task",
                "unattended-create",
                "--expected-sha256",
                task_runtime.calculate_sha256(
                    created_root / "codestable/tasks/active/unattended-create.md"
                ),
                "--record",
                "Recorded a progress-only batch without replacements.",
                "--date",
                "2026-07-29",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(update_result.returncode, 0)

        successful_scan = subprocess.run(
            ["python3", str(RUNTIME_PATH), "--root", str(created_root), "scan"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(successful_scan.returncode, 0)

    def test_archive_recovers_content_prepared_before_an_interrupted_move(self) -> None:
        active_path = self.create_task("resume-archive")
        self.complete_task("resume-archive")
        prepared_content = task_runtime.render_archived_task_content(
            active_path.read_text(encoding="utf-8"),
            "2026-07-29",
        )
        task_runtime.atomic_write_text(active_path, prepared_content)

        scan_before_recovery = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "archive-pending-move",
            {finding.code for finding in scan_before_recovery.findings},
        )
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="resume-archive",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )

        self.assertFalse(active_path.exists())
        self.assertTrue((self.root / archive_result.archived_path).is_file())

    def test_archive_recovers_after_exclusive_publication_before_active_cleanup(self) -> None:
        active_path = self.create_task("resume-published-archive")
        self.complete_task("resume-published-archive")
        task_runtime.atomic_write_text(
            active_path,
            task_runtime.render_archived_task_content(
                active_path.read_text(encoding="utf-8"),
                "2026-07-29",
            ),
        )
        archived_path = self.root / (
            "codestable/tasks/archived/2026-07-29-001-resume-published-archive.md"
        )
        os.link(active_path, archived_path)

        archive_result = task_runtime.archive_task(
            root=self.root,
            task="resume-published-archive",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )

        self.assertFalse(active_path.exists())
        self.assertEqual(self.root / archive_result.archived_path, archived_path)

    def test_archive_recovers_quarantine_before_archive_publication(self) -> None:
        active_path = self.create_task("resume-quarantine-before-publication")
        self.complete_task("resume-quarantine-before-publication")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        task_paths = task_runtime.build_task_paths(
            self.root,
            "resume-quarantine-before-publication",
        )
        task_runtime.atomic_write_text(
            active_path,
            task_runtime.render_archived_task_content(
                active_path.read_text(encoding="utf-8"),
                "2026-07-29",
                source_sha256=completed_source_sha256,
            ),
        )
        quarantine_path = task_runtime.move_active_task_to_quarantine(task_paths)
        self.assertIsNotNone(quarantine_path)

        archive_result = task_runtime.archive_task(
            root=self.root,
            task="resume-quarantine-before-publication",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )

        self.assertFalse(active_path.exists())
        self.assertFalse(quarantine_path.exists())
        self.assertTrue((self.root / archive_result.archived_path).is_file())

    def test_archive_recovers_quarantine_after_archive_publication(self) -> None:
        active_path = self.create_task("resume-quarantine-after-publication")
        self.complete_task("resume-quarantine-after-publication")
        completed_source_sha256 = task_runtime.calculate_sha256(active_path)
        task_paths = task_runtime.build_task_paths(
            self.root,
            "resume-quarantine-after-publication",
        )
        task_runtime.atomic_write_text(
            active_path,
            task_runtime.render_archived_task_content(
                active_path.read_text(encoding="utf-8"),
                "2026-07-29",
                source_sha256=completed_source_sha256,
            ),
        )
        quarantine_path = task_runtime.move_active_task_to_quarantine(task_paths)
        self.assertIsNotNone(quarantine_path)
        archived_path = self.root / (
            "codestable/tasks/archived/"
            "2026-07-29-001-resume-quarantine-after-publication.md"
        )
        os.link(quarantine_path, archived_path)

        archive_result = task_runtime.archive_task(
            root=self.root,
            task="resume-quarantine-after-publication",
            archive_date="2026-07-29",
            expected_sha256=completed_source_sha256,
        )

        self.assertFalse(active_path.exists())
        self.assertFalse(quarantine_path.exists())
        self.assertEqual(self.root / archive_result.archived_path, archived_path)

    def test_archive_never_overwrites_a_target_that_appears_during_publication(self) -> None:
        active_path = self.create_task("exclusive-archive")
        self.complete_task("exclusive-archive")
        archived_path = self.root / (
            "codestable/tasks/archived/2026-07-29-001-exclusive-archive.md"
        )
        original_publish = task_runtime.publish_archive_without_overwrite

        def create_conflict_before_publish(source_path: Path, destination_path: Path) -> None:
            destination_path.write_text("concurrent archive evidence", encoding="utf-8")
            original_publish(source_path, destination_path)

        task_runtime.publish_archive_without_overwrite = create_conflict_before_publish
        try:
            with self.assertRaisesRegex(task_runtime.TaskRuntimeError, "evidence was preserved"):
                task_runtime.archive_task(
                    root=self.root,
                    task="exclusive-archive",
                    archive_date="2026-07-29",
                    expected_sha256=task_runtime.calculate_sha256(active_path),
                )
        finally:
            task_runtime.publish_archive_without_overwrite = original_publish

        self.assertEqual(
            archived_path.read_text(encoding="utf-8"),
            "concurrent archive evidence",
        )
        self.assertTrue(active_path.exists())

    def test_scan_reports_duplicate_active_and_archived_state_without_deleting_evidence(self) -> None:
        active_path = self.create_task("duplicate-state")
        self.complete_task("duplicate-state")
        completed_content = active_path.read_text(encoding="utf-8")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="duplicate-state",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        active_path.write_text(completed_content, encoding="utf-8")

        scan_result = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "duplicate-task-state",
            {finding.code for finding in scan_result.findings},
        )
        self.assertTrue(active_path.exists())
        self.assertTrue((self.root / archive_result.archived_path).exists())

    def test_scan_reports_an_invalid_archived_document(self) -> None:
        active_path = self.create_task("invalid-archive")
        self.complete_task("invalid-archive")
        archive_result = task_runtime.archive_task(
            root=self.root,
            task="invalid-archive",
            archive_date="2026-07-29",
            expected_sha256=task_runtime.calculate_sha256(active_path),
        )
        archived_path = self.root / archive_result.archived_path
        archived_path.write_text("invalid archived content", encoding="utf-8")

        scan_result = task_runtime.scan_tasks(self.root)
        self.assertIn(
            "invalid-archived-task",
            {finding.code for finding in scan_result.findings},
        )


if __name__ == "__main__":
    unittest.main()
