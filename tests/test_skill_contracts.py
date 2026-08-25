from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "cs"
POSTURE_REFERENCES = (
    "onboard.md",
    "talk.md",
    "vision.md",
    "spec.md",
    "explore.md",
    "complain.md",
    "design.md",
    "fast.md",
    "do.md",
    "close.md",
    "code-design.md",
    "note.md",
    "maketools.md",
)


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class SkillContractTests(unittest.TestCase):
    def test_repository_keeps_exactly_one_skill_entry(self) -> None:
        skill_directories = sorted(
            path.name for path in (ROOT / "skills").iterdir() if path.is_dir()
        )
        self.assertEqual(skill_directories, ["cs"])

    def test_task_assets_are_inside_the_single_cs_skill(self) -> None:
        required_paths = (
            SKILL_ROOT / "references" / "task.md",
            SKILL_ROOT / "references" / "autonomy.md",
            SKILL_ROOT / "scripts" / "codestable_task_runtime.py",
            SKILL_ROOT / "templates" / "entities" / "task.md",
        )
        self.assertTrue(all(path.is_file() for path in required_paths))

    def test_issue_artifact_contract_defines_distinct_physical_shapes(self) -> None:
        skill_text = read_text("skills/cs/SKILL.md")
        agent_prompt = read_text("skills/cs/agents/openai.yaml")
        issue_template = read_text("skills/cs/templates/entities/issue.md")
        fast_fix_template = read_text("skills/cs/templates/entities/ff-issue.md")
        explore_template = read_text("skills/cs/templates/entities/explore-index.md")

        self.assertIn("Task 与 Issue 的命名空间必须隔离", skill_text)
        self.assertIn(r"`codestable/issues/{NNN}-o\|x-{名}.md`", skill_text)
        self.assertIn(r"`{NNN}-o\|x-ff-{名}.md`", skill_text)
        self.assertIn(r"`{NNN}-o\|x-{名}/index.md`", skill_text)
        self.assertIn("Keep Task archive naming isolated", agent_prompt)
        self.assertIn("普通 Issue 不使用日期或 Task 目录", issue_template)
        self.assertIn(
            "不得另建 fix-note、report、analysis 或其他补充修复记录",
            fast_fix_template,
        )
        self.assertIn("本模板只用于 {NNN}-o|x-{name}/index.md", explore_template)

    def test_root_skill_defines_question_gate_and_issue_task_lifecycle(self) -> None:
        skill_text = read_text("skills/cs/SKILL.md")
        required_markers = (
            "Issue 姿态进入 Task 主线",
            "简单 Question 直接回答，不创建 Task",
            "无法识别是 Question 还是 Issue 时，必须在创建 Task 前用 AskQuestion 确认",
            "创建或恢复 Task",
            "每个可观察批次",
            "标记 completed",
            "原子归档",
            "active 同名文件不存在",
            "只在对话回答”若确实是 Question，则不创建 Task",
        )
        for required_marker in required_markers:
            with self.subTest(required_marker=required_marker):
                self.assertIn(required_marker, skill_text)

    def test_every_posture_reference_inherits_the_task_contract(self) -> None:
        for reference_name in POSTURE_REFERENCES:
            with self.subTest(reference_name=reference_name):
                reference_text = (SKILL_ROOT / "references" / reference_name).read_text(
                    encoding="utf-8"
                )
                self.assertIn("[Task 主线](task.md)", reference_text)

    def test_task_reference_defines_source_of_truth_and_terminal_archive(self) -> None:
        task_text = read_text("skills/cs/references/task.md")
        required_markers = (
            "Issue，不是 Question",
            "简单的 **Question** 是直接问答，不创建 Task",
            "必须在创建 Task 前调用 `AskQuestion`",
            "Question 路径不扫描或恢复 Task",
            "Task List 是 source of truth",
            "codestable/tasks/active/",
            "codestable/tasks/archived/",
            "陈旧快照保护",
            "单写者模型",
            "archive-pending-move",
            "duplicate-task-state",
            "`completed` 不是最终状态",
            "Issue 可以属于接入、讨论整理、愿景、规格",
        )
        for required_marker in required_markers:
            with self.subTest(required_marker=required_marker):
                self.assertIn(required_marker, task_text)

    def test_autonomy_reference_forbids_questions_after_plan_commitment(self) -> None:
        autonomy_text = read_text("skills/cs/references/autonomy.md")
        required_markers = (
            "简单 Question 直接回答，不创建 Task",
            "无法可靠判断是 Question 还是 Issue，必须在 Task 创建前使用 AskQuestion",
            "计划确定前",
            "计划确定后",
            "禁止再次调用 AskQuestion",
            "自动选择推荐方向",
            "可逆性",
            "契约一致性",
            "总成本",
            "持续执行直到",
        )
        for required_marker in required_markers:
            with self.subTest(required_marker=required_marker):
                self.assertIn(required_marker, autonomy_text)

    def test_fast_and_read_only_workflows_cannot_skip_task_traceability(self) -> None:
        fast_text = read_text("skills/cs/references/fast.md")
        explore_text = read_text("skills/cs/references/explore.md")
        review_text = read_text("skills/cs/references/code-design.md")
        self.assertIn("Task 不可豁免", fast_text)
        self.assertIn("需要形成可复用调查结论的 Explore Issue", explore_text)
        self.assertIn("只读 Review 也必须创建、更新、完成并归档 Task", review_text)

    def test_posture_references_distinguish_direct_questions_from_issues(self) -> None:
        expected_markers = {
            "talk.md": "简单 Question 直接回答且不创建 Task",
            "vision.md": "简单 Question 直接回答且不创建 Task",
            "spec.md": "询问现有规格时直接回答且不创建 Task",
            "explore.md": "简单现状 Question 直接说明且不创建 Task",
            "complain.md": "仅询问问题原因时直接回答且不创建 Task",
            "design.md": "仅询问方案差异时直接回答且不创建 Task",
            "fast.md": "简单改法询问直接回答且不创建 Task",
            "do.md": "仅询问实现方式时直接回答且不创建 Task",
            "close.md": "询问关闭规则时直接回答且不创建 Task",
            "code-design.md": "仅询问设计原则时直接回答且不创建 Task",
            "note.md": "询问已有知识时直接回答且不创建 Task",
            "maketools.md": "询问流程用法时直接回答且不创建 Task",
            "onboard.md": "询问接入方法时直接回答且不创建 Task",
        }
        for reference_name, marker in expected_markers.items():
            with self.subTest(reference_name=reference_name):
                reference_text = (SKILL_ROOT / "references" / reference_name).read_text(
                    encoding="utf-8"
                )
                self.assertIn(marker, reference_text)

    def test_initialization_and_public_docs_include_task_workspace(self) -> None:
        initialization_text = read_text("skills/cs/scripts/init_codestable.py")
        agent_text = read_text("skills/cs/agents/openai.yaml")
        for readme_name in ("README.md", "README.en.md"):
            with self.subTest(readme_name=readme_name):
                self.assertIn("tasks/", read_text(readme_name))
        self.assertIn("codestable/tasks/active", initialization_text)
        self.assertIn("codestable/tasks/archived", initialization_text)
        for removed_directory in ("tombstones", "staging", "conflicts", "locks"):
            with self.subTest(removed_directory=removed_directory):
                self.assertNotIn(f"codestable/tasks/{removed_directory}", initialization_text)
        self.assertIn("Task", agent_text)
        self.assertIn("unattended", agent_text)

    def test_public_contracts_explain_question_without_task(self) -> None:
        chinese_readme = read_text("README.md")
        english_readme = read_text("README.en.md")
        agent_prompt = read_text("skills/cs/agents/openai.yaml")
        self.assertIn("Question 不创建 Task", chinese_readme)
        self.assertIn("Questions create no Task", english_readme)
        self.assertIn("First distinguish a simple Question from an Issue", agent_prompt)

    def test_public_installation_docs_target_the_modified_repository(self) -> None:
        modified_repository_url = "https://github.com/joseph-bing-han/CodeStable-Lite"
        required_install_commands = (
            "npx skills add joseph-bing-han/CodeStable-Lite",
            "npx skills add joseph-bing-han/CodeStable-Lite -g",
        )
        original_install_command = "npx skills add codestable/CodeStable-Lite"
        for readme_name in ("README.md", "README.en.md"):
            with self.subTest(readme_name=readme_name):
                readme_text = read_text(readme_name)
                documented_lines = {line.strip() for line in readme_text.splitlines()}
                self.assertIn(modified_repository_url, readme_text)
                for install_command in required_install_commands:
                    with self.subTest(install_command=install_command):
                        self.assertIn(install_command, documented_lines)
                self.assertNotIn(original_install_command, readme_text)

    def test_plan_committed_artifacts_do_not_reopen_human_checkpoints(self) -> None:
        forbidden_phrases = {
            "skills/cs/references/do.md": ["用户确认先通", "不通就停下等待用户"],
            "skills/cs/templates/entities/ff-issue.md": ["待用户确认是否写入"],
            "skills/cs/templates/entities/issue.md": ["须二次确认", "需要用户确认："],
            "README.md": ["则停止并回到 Design、Talk 或新的事项"],
        }
        for relative_path, phrases in forbidden_phrases.items():
            file_text = read_text(relative_path)
            for phrase in phrases:
                with self.subTest(relative_path=relative_path, phrase=phrase):
                    self.assertNotIn(phrase, file_text)

    def test_runtime_contract_documents_completion_and_recovery_gates(self) -> None:
        task_text = read_text("skills/cs/references/task.md")
        for marker in (
            "set-status",
            "checklist 全部勾选",
            "进入 `completed / cancelled` 后正文冻结",
            "--expected-sha256 {sha256}",
            "archive-pending-move",
            "duplicate-task-state",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, task_text)

    def test_archive_is_a_lifecycle_action_not_a_task_plan_item(self) -> None:
        task_text = read_text("skills/cs/references/task.md")
        template_text = read_text("skills/cs/templates/entities/task.md")
        self.assertIn("归档不是 Task 计划步骤", task_text)
        self.assertNotRegex(template_text, r"(?m)^- \[[ x]\].*(归档|archive)")

    def test_runtime_uses_only_the_single_writer_active_and_archived_model(self) -> None:
        runtime_text = read_text("skills/cs/scripts/codestable_task_runtime.py")
        for obsolete_marker in (
            "import fcntl",
            "tombstone_root",
            "staging_root",
            "conflict_root",
            "lock_root",
        ):
            with self.subTest(obsolete_marker=obsolete_marker):
                self.assertNotIn(obsolete_marker, runtime_text)
        for required_marker in (
            "validate_plan_preserved",
            "Completed or cancelled Tasks are frozen",
            "archive-pending-move",
            "duplicate-task-state",
            "publish_archive_without_overwrite",
        ):
            with self.subTest(required_marker=required_marker):
                self.assertIn(required_marker, runtime_text)


if __name__ == "__main__":
    unittest.main()
