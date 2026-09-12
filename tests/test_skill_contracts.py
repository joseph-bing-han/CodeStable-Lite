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
    def assert_markers_follow_order(self, text: str, markers: tuple[str, ...]) -> None:
        for marker in markers:
            self.assertIn(marker, text)
        marker_positions = [text.index(marker) for marker in markers]
        self.assertEqual(
            marker_positions,
            sorted(marker_positions),
            "Development lifecycle phases are out of order",
        )

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
            "自动回写与沉淀",
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
            "不询问普通推进，只询问必要澄清与授权",
            "自动选择推荐方向",
            "可逆性",
            "契约一致性",
            "总成本",
            "持续执行直到",
            "用户中途纠正优先于旧计划",
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

    def test_retention_contract_has_explicit_graduation_and_auxiliary_triggers(self) -> None:
        retention_text = read_text("skills/cs/references/retention.md")
        required_markers = (
            "独立 Issue / 无业务 Issue",
            "Epic 内 Issue / 直接切片",
            "Epic 经用户确认关闭",
            "讨论收束：自动捕获 Talk",
            "验证之后：自动提炼 Note",
            "重复流程：有证据才生成 Tool",
            "无增量原因",
        )
        for required_marker in required_markers:
            with self.subTest(required_marker=required_marker):
                self.assertIn(required_marker, retention_text)

    def test_host_adaptation_does_not_infer_tools_from_model_name(self) -> None:
        adaptation_text = read_text("skills/cs/references/runtime-adaptation.md")
        self.assertIn("检查当前宿主实际提供的工具 schema", adaptation_text)
        self.assertIn("不能从模型名称推导工具可用", read_text("skills/cs/SKILL.md"))

    def test_graduation_does_not_turn_task_completion_into_business_closure(self) -> None:
        retention_text = read_text("skills/cs/references/retention.md")
        self.assertIn("实现完成不自动关闭常规 Issue", retention_text)
        self.assertIn("未关闭 Epic 的成果不得提前毕业到 Project Spec", retention_text)
        self.assertIn("若 Epic 已满足关闭条件，主动呈现具体毕业候选", retention_text)

    def test_reusable_artifact_rules_reject_unverified_or_one_off_outputs(self) -> None:
        retention_text = read_text("skills/cs/references/retention.md")
        self.assertIn("普通测试通过、代码已直说的行为、一次性进度和尚未验证的猜测不生成 Note", retention_text)
        self.assertIn("仅一次探索、仍需人判断的流程、超出当前范围的大型自动化", retention_text)
        self.assertIn("验证不了就不能标“稳定工具”", retention_text)

    def test_archive_is_a_lifecycle_action_not_a_task_plan_item(self) -> None:
        task_text = read_text("skills/cs/references/task.md")
        template_text = read_text("skills/cs/templates/entities/task.md")
        self.assertIn("归档不是 Task 计划步骤", task_text)
        self.assertNotRegex(template_text, r"(?m)^- \[[ x]\].*(归档|archive)")

    def test_documented_spines_keep_business_context_before_task_and_writeback_after_archive(self) -> None:
        workflow_contracts = (
            (
                "skills/cs/references/task.md",
                "## 6. 全流程 spine",
                (
                    "有界分析讨论 / 必要澄清，形成结论",
                    "创建或更新相关 Issue / Spec 等前置文档",
                    "创建或恢复 active Task",
                    "实施修改或交付一个可观察批次",
                    "-> 更新 Task",
                    "测试 / 必要 Review（失败 -> 修改 -> 更新 Task -> 复测）",
                    "Task 标记 completed",
                    "立即原子归档",
                    "更新所有相关 Issue / Spec 等文档的结果、最终状态和链接",
                    "最终答复",
                ),
            ),
            (
                "README.md",
                "### Issue 共享同一条 Task 留痕主线，Question 不创建 Task",
                (
                    "分析讨论并形成结论",
                    "创建或更新相关 Issue / Spec 等前置文档",
                    "创建或恢复 Task",
                    "实施一个可观察批次",
                    "-> 更新 Task",
                    "测试 / 必要 Review（失败则返回修改、更新 Task 与复测）",
                    "标记 completed",
                    "原子归档并确认 active 无同名残留",
                    "更新所有相关 Issue / Spec 等文档的结果、最终状态和链接",
                    "回读确认后结束",
                ),
            ),
            (
                "README.en.md",
                "### Give Issues the same traceable Task spine; Questions create no Task",
                (
                    "analyze and discuss until a conclusion is clear",
                    "create or update relevant Issue / Spec and other prerequisite documents",
                    "create or resume Task",
                    "implement one observable batch",
                    "-> update Task",
                    "test / required review (failure returns to implementation, Task updates, and retesting)",
                    "mark completed",
                    "archive atomically and verify no matching active Task remains",
                    "update all related business documents with results, final status, and links",
                    "read back and finish",
                ),
            ),
        )
        for relative_path, section_heading, ordered_phases in workflow_contracts:
            with self.subTest(relative_path=relative_path):
                section_text = read_text(relative_path).split(section_heading, 1)[1]
                workflow_text = section_text.split("```text\n", 1)[1].split("```", 1)[0]
                self.assert_markers_follow_order(workflow_text, ordered_phases)

    def test_skill_entry_and_host_prompt_preserve_the_same_lifecycle_order(self) -> None:
        skill_text = read_text("skills/cs/SKILL.md")
        entry_text = skill_text.split("### Issue 姿态进入 Task 主线", 1)[1].split("\n---", 1)[0]
        self.assert_markers_follow_order(
            entry_text,
            (
                "1. 分析讨论并形成结论",
                "2. 创建或更新相关 Issue / Spec 等前置文档",
                "3. 前置文档就绪后",
                "4. 实施修改或交付",
                "5. 测试与必要 Review",
                "6. 执行与验证全部完成后",
                "7. Task 归档后更新所有相关 Issue / Spec",
            ),
        )
        startup_text = skill_text.split("## 3. 开工协议", 1)[1].split("## 4.", 1)[0]
        self.assert_markers_follow_order(
            startup_text,
            ("**扫 `codestable/`**", "**按权重深读**", "**前置业务文档**", "**Task gate**"),
        )
        self.assert_markers_follow_order(
            read_text("skills/cs/agents/openai.yaml"),
            (
                "Analyze and discuss the request",
                "Create or update the relevant Issue, ff, Spec",
                "Then create or resume a Task",
                "Implement and update the Task",
                "Test and return to implementation",
                "Complete and atomically archive the Task",
                "After archive and cleanup/scan, write back",
                "then read them back before the final answer",
            ),
        )

    def test_postures_do_not_restore_task_first_or_posthoc_issue_creation(self) -> None:
        forbidden_instructions = (
            "先创建或恢复 Task，再开始读取仓库",
            "代码与验证完成后再写 `ff`",
            "同会话已完成：直接在所属树写",
            "先创建 active Task，再执行 `SKILL.md` 开工协议",
            "先提交 Task 计划再查",
            "创建或恢复 active Task → 有复用价值时落盘 Talk",
            "确认后再写入 Task 并落盘",
            "Before substantive work, create or resume a Task.",
        )
        contract_paths = [SKILL_ROOT / "SKILL.md", SKILL_ROOT / "agents/openai.yaml"]
        contract_paths.extend((SKILL_ROOT / "references").glob("*.md"))
        for contract_path in contract_paths:
            contract_text = contract_path.read_text(encoding="utf-8")
            for forbidden_instruction in forbidden_instructions:
                with self.subTest(path=contract_path.name, instruction=forbidden_instruction):
                    self.assertNotIn(forbidden_instruction, contract_text)

    def test_post_archive_recovery_uses_business_documents_without_reopening_task(self) -> None:
        task_text = read_text("skills/cs/references/task.md")
        template_text = read_text("skills/cs/templates/entities/task.md")
        close_text = read_text("skills/cs/references/close.md")
        self.assertIn("不创建“收尾回写 Task”", task_text)
        self.assertIn("不为修历史链接改写 archive", task_text)
        self.assertIn("Task 已归档，业务回写未完成", task_text)
        self.assertIn("Task 已归档时只继续关联文档的最终回写", template_text)
        self.assertIn("不修改冻结 Task，不为回写另建 Task", template_text)
        self.assertIn("不把未执行提交标成 done", task_text)
        self.assertIn(
            "准备与验证 -> Task 归档 -> 业务回写 -> 已授权提交 -> 最终答复",
            close_text,
        )

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
