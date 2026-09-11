#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


@dataclass(frozen=True)
class Finding:
    path: str
    message: str


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_git_ignored(root: Path, path: Path) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", "--", rel(path, root)],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def check_version(root: Path, findings: list[Finding]) -> None:
    version_file = root / "VERSION"
    changelog = root / "CHANGELOG.md"
    if not version_file.is_file():
        findings.append(Finding("VERSION", "file is missing"))
        return

    version = version_file.read_text(encoding="utf-8").strip()
    if not VERSION_RE.match(version):
        findings.append(Finding("VERSION", f"not valid semver: {version!r}"))
    if not changelog.is_file():
        findings.append(Finding("CHANGELOG.md", "file is missing"))
    elif f"## {version}" not in changelog.read_text(encoding="utf-8"):
        findings.append(Finding("CHANGELOG.md", f"missing version section {version}"))


def required_skill_files(root: Path) -> list[Path]:
    skill = root / "skills/cs"
    files = [
        skill / "SKILL.md",
        skill / "agents/openai.yaml",
        skill / "scripts/init_codestable.py",
        skill / "scripts/codestable_task_runtime.py",
    ]
    files.extend(
        skill / "references" / filename
        for filename in [
            "close.md",
            "code-design.md",
            "complain.md",
            "debug.md",
            "design.md",
            "do.md",
            "docs.md",
            "economy.md",
            "explore.md",
            "fast.md",
            "maketools.md",
            "note.md",
            "onboard.md",
            "quality.md",
            "spec.md",
            "talk.md",
            "task.md",
            "autonomy.md",
            "retention.md",
            "runtime-adaptation.md",
            "ui-spec.md",
            "vision.md",
        ]
    )
    files.extend(
        skill / "templates/entities" / filename
        for filename in [
            "epic-spec.md",
            "explore-article.md",
            "explore-index.md",
            "ff-issue.md",
            "issue.md",
            "notes.md",
            "project-spec-index.md",
            "spec-section-index.md",
            "talk.md",
            "task.md",
            "tool.md",
            "vision-index.md",
            "vision-section-index.md",
        ]
    )
    return files


def check_skill_layout(root: Path, findings: list[Finding]) -> None:
    skills = root / "skills"
    if not skills.is_dir():
        findings.append(Finding("skills", "directory is missing"))
        return

    skill_dirs = sorted(path.name for path in skills.iterdir() if path.is_dir())
    if skill_dirs != ["cs"]:
        findings.append(Finding("skills", f"must contain exactly the cs skill, found {skill_dirs!r}"))

    for path in required_skill_files(root):
        if not path.is_file():
            findings.append(Finding(rel(path, root), "required skill file is missing"))
        elif is_git_ignored(root, path):
            findings.append(Finding(rel(path, root), "required skill file is git-ignored"))

    obsolete_facts_template = root / "skills/cs/templates/entities/facts.md"
    if obsolete_facts_template.exists():
        findings.append(Finding(rel(obsolete_facts_template, root), "obsolete facts entity must not exist"))

    for obsolete in ["plugins", ".agents/plugins", ".claude-plugin"]:
        if (root / obsolete).exists():
            findings.append(Finding(obsolete, "obsolete plugin wrapper must not exist"))


def check_quality_contract(root: Path, findings: list[Finding]) -> None:
    skill = root / "skills/cs"
    quality = skill / "references/quality.md"
    if quality.is_file():
        text = quality.read_text(encoding="utf-8")
        for characteristic in [
            "Functional suitability",
            "Performance efficiency",
            "Compatibility",
            "Interaction capability",
            "Reliability",
            "Security",
            "Maintainability",
            "Flexibility",
            "Safety",
        ]:
            if characteristic not in text:
                findings.append(
                    Finding(rel(quality, root), f"missing quality characteristic: {characteristic}")
                )

    skill_md = skill / "SKILL.md"
    if skill_md.is_file() and "(references/quality.md)" not in skill_md.read_text(encoding="utf-8"):
        findings.append(Finding(rel(skill_md, root), "does not route quality.md"))

    templates = skill / "templates/entities"
    issue_template = templates / "issue.md"
    if issue_template.is_file():
        issue_template_text = issue_template.read_text(encoding="utf-8")
        quality_contract_markers = ("## 质量目标\n", "质量承诺")
        if not any(marker in issue_template_text for marker in quality_contract_markers):
            findings.append(Finding(rel(issue_template, root), "missing quality objective contract"))


def check_economy_contract(root: Path, findings: list[Finding]) -> None:
    skill = root / "skills/cs"
    economy = skill / "references/economy.md"
    if economy.is_file():
        text = economy.read_text(encoding="utf-8")
        for marker in ["最小充分变化", "已知上限", "升级触发", "最小有用反馈"]:
            if marker not in text:
                findings.append(Finding(rel(economy, root), f"missing economy contract: {marker}"))

    skill_md = skill / "SKILL.md"
    if skill_md.is_file() and "(references/economy.md)" not in skill_md.read_text(encoding="utf-8"):
        findings.append(Finding(rel(skill_md, root), "does not route economy.md"))

    templates = skill / "templates/entities"
    issue_template = templates / "issue.md"
    if issue_template.is_file():
        issue_template_text = issue_template.read_text(encoding="utf-8")
        bounded_simplification_markers = ("有界简化上限/触发/方向", "有界简化")
        if not any(
            marker in issue_template_text for marker in bounded_simplification_markers
        ):
            findings.append(
                Finding(rel(issue_template, root), "missing bounded simplification contract")
            )


def check_ui_spec_contract(root: Path, findings: list[Finding]) -> None:
    skill = root / "skills/cs"
    ui_spec = skill / "references/ui-spec.md"
    if ui_spec.is_file():
        text = ui_spec.read_text(encoding="utf-8")
        for marker in ["什么时候必须画", "ASCII 线框图", "Mermaid", "当前 / 目标", "不能成为唯一规格"]:
            if marker not in text:
                findings.append(Finding(rel(ui_spec, root), f"missing UI spec contract: {marker}"))

    skill_md = skill / "SKILL.md"
    if skill_md.is_file() and "(references/ui-spec.md)" not in skill_md.read_text(encoding="utf-8"):
        findings.append(Finding(rel(skill_md, root), "does not route ui-spec.md"))

    templates = skill / "templates/entities"
    required_marker_groups = {
        "project-spec-index.md": ("## 界面与交互（按需）", "界面（当前已成立时）"),
        "spec-section-index.md": ("## 界面与交互（按需）", "当前界面（若有）"),
        "epic-spec.md": ("## 界面与交互变化（按需）", "UI 若影响理解"),
        "talk.md": ("## UI 对齐草图（按需）", "UI 草图"),
        "issue.md": ("## UI 变化 / 实际与预期（按需）", "UI 变化（若有）"),
    }
    for filename, marker_group in required_marker_groups.items():
        path = templates / filename
        if not path.is_file():
            continue

        template_text = path.read_text(encoding="utf-8")
        if not any(marker in template_text for marker in marker_group):
            expected_markers = " or ".join(marker_group)
            findings.append(
                Finding(rel(path, root), f"missing UI visual contract: {expected_markers}")
            )


def check_readmes(root: Path, findings: list[Finding]) -> None:
    required = [
        "https://github.com/joseph-bing-han/CodeStable-Lite",
        "npx skills add . --list",
        "npx skills update cs",
    ]
    required_install_commands = [
        "npx skills add joseph-bing-han/CodeStable-Lite",
        "npx skills add joseph-bing-han/CodeStable-Lite -g",
    ]
    required_markers = {
        "README.md": ["ISO/IEC 25010:2023", "## 实现如何保持经济性", "## UI 规格如何使用图"],
        "README.en.md": ["ISO/IEC 25010:2023", "## How implementation stays economical", "## How UI specs use visuals"],
    }
    obsolete = [
        "codex plugin",
        "/plugin ",
        "plugins/codestable-lite",
        ".claude-plugin",
        "marketplace",
    ]
    obsolete_install_commands = ["npx skills add codestable/CodeStable-Lite"]
    for filename in ["README.md", "README.en.md"]:
        path = root / filename
        if not path.is_file():
            findings.append(Finding(filename, "file is missing"))
            continue
        text = path.read_text(encoding="utf-8")
        documented_lines = {line.strip() for line in text.splitlines()}
        for command in required:
            if command not in text:
                findings.append(Finding(filename, f"missing documented command: {command}"))
        for command in required_install_commands:
            if command not in documented_lines:
                findings.append(Finding(filename, f"missing exact install command: {command}"))
        for marker in required_markers[filename]:
            if marker not in text:
                findings.append(Finding(filename, f"missing documented contract: {marker}"))
        for marker in obsolete:
            if marker in text:
                findings.append(Finding(filename, f"obsolete plugin documentation remains: {marker}"))
        for command in obsolete_install_commands:
            if command in text:
                findings.append(Finding(filename, f"obsolete install command remains: {command}"))


def check_task_contract(root: Path, findings: list[Finding]) -> None:
    skill = root / "skills/cs"
    required_markers = {
        "SKILL.md": [
            "Issue 姿态进入 Task 主线",
            "简单 Question 直接回答，不创建 Task",
            "无法识别是 Question 还是 Issue 时，必须在创建 Task 前用 AskQuestion 确认",
            "创建或恢复 Task",
            "每个可观察批次",
            "原子归档",
            "不询问普通推进，只询问必要澄清与授权",
        ],
        "references/task.md": [
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
        ],
        "references/autonomy.md": [
            "简单 Question 直接回答，不创建 Task",
            "无法可靠判断是 Question 还是 Issue，必须在 Task 创建前使用 AskQuestion",
            "计划确定前",
            "计划确定后",
            "不询问普通推进，只询问必要澄清与授权",
            "自动选择推荐方向",
            "可逆性",
            "总成本",
            "用户中途纠正优先于旧计划",
        ],
    }
    for relative_path, markers in required_markers.items():
        path = skill / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                findings.append(
                    Finding(rel(path, root), f"missing mandatory Task contract: {marker}")
                )

    posture_references = [
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
    ]
    for filename in posture_references:
        path = skill / "references" / filename
        if path.is_file() and "[Task 主线](task.md)" not in path.read_text(encoding="utf-8"):
            findings.append(Finding(rel(path, root), "does not inherit the mandatory Task spine"))

    retention_path = skill / "references/retention.md"
    if retention_path.is_file():
        retention_text = retention_path.read_text(encoding="utf-8")
        for marker in [
            "独立 Issue / 无业务 Issue",
            "Epic 内 Issue / 直接切片",
            "Epic 经用户确认关闭",
            "讨论收束：自动捕获 Talk",
            "验证之后：自动提炼 Note",
            "重复流程：有证据才生成 Tool",
            "无增量原因",
        ]:
            if marker not in retention_text:
                findings.append(Finding(rel(retention_path, root), f"missing retention contract: {marker}"))

    adaptation_path = skill / "references/runtime-adaptation.md"
    if adaptation_path.is_file():
        adaptation_text = adaptation_path.read_text(encoding="utf-8")
        for marker in ["检查当前宿主实际提供的工具 schema", "不能从模型名称推导工具可用"]:
            if marker not in adaptation_text:
                findings.append(Finding(rel(adaptation_path, root), f"missing host adaptation contract: {marker}"))

    initialization_path = skill / "scripts/init_codestable.py"
    if initialization_path.is_file():
        initialization_text = initialization_path.read_text(encoding="utf-8")
        for task_directory in [
            "codestable/tasks/active",
            "codestable/tasks/archived",
        ]:
            if task_directory not in initialization_text:
                findings.append(
                    Finding(
                        rel(initialization_path, root),
                        f"missing Task workspace directory: {task_directory}",
                    )
                )

        for removed_task_directory in [
            "codestable/tasks/tombstones",
            "codestable/tasks/staging",
            "codestable/tasks/conflicts",
            "codestable/tasks/locks",
        ]:
            if removed_task_directory in initialization_text:
                findings.append(
                    Finding(
                        rel(initialization_path, root),
                        f"obsolete Task runtime directory remains: {removed_task_directory}",
                    )
                )

    for filename in ["README.md", "README.en.md"]:
        path = root / filename
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for marker in ["tasks/", "Task", "archived"]:
                if marker not in text:
                    findings.append(Finding(filename, f"missing public Task contract: {marker}"))

    forbidden_post_commit_phrases = {
        "skills/cs/references/do.md": ["用户确认先通", "不通就停下等待用户"],
        "skills/cs/templates/entities/ff-issue.md": ["待用户确认是否写入"],
        "skills/cs/templates/entities/issue.md": ["须二次确认", "需要用户确认："],
        "README.md": ["则停止并回到 Design、Talk 或新的事项"],
    }
    for relative_path, phrases in forbidden_post_commit_phrases.items():
        path = root / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase in text:
                findings.append(
                    Finding(relative_path, f"reopens a post-commit human checkpoint: {phrase}")
                )

    runtime_path = skill / "scripts/codestable_task_runtime.py"
    if runtime_path.is_file():
        runtime_text = runtime_path.read_text(encoding="utf-8")
        for obsolete_runtime_marker in [
            "import fcntl",
            "tombstone_root",
            "staging_root",
            "conflict_root",
            "lock_root",
        ]:
            if obsolete_runtime_marker in runtime_text:
                findings.append(
                    Finding(
                        rel(runtime_path, root),
                        f"obsolete Task transaction mechanism remains: {obsolete_runtime_marker}",
                    )
                )


def check_task_runtime_behavior(root: Path, findings: list[Finding]) -> None:
    required_test_paths = (
        root / "tests/test_task_runtime.py",
        root / "tests/test_skill_contracts.py",
    )
    for test_path in required_test_paths:
        if not test_path.is_file():
            findings.append(Finding(rel(test_path, root), "Required repository test is missing"))
            continue
        test_result = subprocess.run(
            ["python3", str(test_path)],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if test_result.returncode != 0:
            failure_output = (test_result.stdout + test_result.stderr).strip()
            findings.append(
                Finding(
                    rel(test_path, root),
                    f"Repository behavior tests failed: {failure_output}",
                )
            )


def check_repo(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    check_version(root, findings)
    check_skill_layout(root, findings)
    check_quality_contract(root, findings)
    check_economy_contract(root, findings)
    check_ui_spec_contract(root, findings)
    check_readmes(root, findings)
    check_task_contract(root, findings)
    check_task_runtime_behavior(root, findings)
    if (root / "dist").exists():
        findings.append(Finding("dist", "temporary distribution output must not be committed"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the CodeStable single-skill repository.")
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable findings.")
    args = parser.parse_args()
    findings = check_repo(Path(args.root))
    if args.json:
        print(json.dumps({"ok": not findings, "findings": [finding.__dict__ for finding in findings]}, indent=2))
    elif findings:
        print("Skill repository check failed:")
        for finding in findings:
            print(f"- {finding.path}: {finding.message}")
    else:
        print("Skill repository check passed.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
