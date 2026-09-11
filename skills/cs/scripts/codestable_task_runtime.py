#!/usr/bin/env python3
"""Manage the single-writer lifecycle of CodeStable Task documents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Sequence


TASK_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ARCHIVED_TASK_FILENAME_PATTERN = re.compile(
    r"^(?P<archive_date>\d{4}-\d{2}-\d{2})-"
    r"(?P<daily_sequence>\d{3})-"
    r"(?P<task>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
LEGACY_ARCHIVED_TASK_FILENAME_PATTERN = re.compile(
    r"^(?P<archive_date>\d{4}-\d{2}-\d{2})-"
    r"(?P<task>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
MAX_DAILY_ARCHIVE_SEQUENCE = 999
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
ACTIVE_STATUSES = frozenset({"active", "blocked", "completed", "cancelled"})
ARCHIVABLE_STATUSES = frozenset({"completed", "cancelled"})
EXECUTION_STATUSES = frozenset({"pending", "in-progress", "blocked", "done"})
ACTIVE_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "active": frozenset({"active", "blocked", "completed", "cancelled"}),
    "blocked": frozenset({"blocked", "active"}),
    "completed": frozenset({"completed"}),
    "cancelled": frozenset({"cancelled"}),
}
PROTECTED_UPDATE_FIELDS = frozenset({"doc_type", "task", "status", "created", "archived"})
TASK_REQUIRED_FIELDS = frozenset(
    {
        "doc_type",
        "task",
        "goal",
        "status",
        "workflow",
        "owner_skill",
        "created",
        "updated",
        "archived",
        "related_docs",
    }
)
TASK_SECTION_HEADINGS = (
    "## 1. 任务目标",
    "## 2. 当前状态",
    "## 3. Agent 原生 Tasks 同步区",
    "## 4. CodeStable 文档索引",
    "## 5. 执行步骤",
    "## 6. 中断恢复提示",
    "## 7. 完成与归档记录",
)
ARCHIVE_TERM_PATTERN = re.compile(r"归档|\barchiv(?:e|ing|al)\b", re.IGNORECASE)
ANALYTICAL_ARCHIVE_STEP_PATTERN = re.compile(
    r"^(?:分析|调查|研究|审查|验证|评估|设计|解释|理解|检查)|"
    r"^(?:analy[sz]e|investigate|research|review|verify|evaluate|design|"
    r"explain|understand|inspect|test|document)\b|"
    r"^(?:archive|archival)\b.*\b(?:strategy|analysis|recovery|behavior|"
    r"design|mechanism|policy)\b",
    re.IGNORECASE,
)
ARCHIVE_COMMAND_STEP_PATTERN = re.compile(
    r"^(?:将|把|执行|完成|进行|开始|发布|机械执行|移动)|"
    r"^(?:publish|perform|execute|complete|run|move|finalize|start)\b",
    re.IGNORECASE,
)


class TaskRuntimeError(RuntimeError):
    """Raised when a Task lifecycle operation cannot proceed safely."""


@dataclass(frozen=True)
class TaskPaths:
    root: Path
    task_root: Path
    active_root: Path
    archived_root: Path
    active_path: Path


@dataclass(frozen=True)
class TaskSummary:
    task: str
    status: str
    workflow: str
    owner_skill: str
    path: str


@dataclass(frozen=True)
class RuntimeFinding:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ScanResult:
    active: tuple[TaskSummary, ...]
    archived: tuple[TaskSummary, ...]
    findings: tuple[RuntimeFinding, ...]


@dataclass(frozen=True)
class ArchiveResult:
    task: str
    archived_path: str


@dataclass(frozen=True)
class FileIdentity:
    device: int
    inode: int
    size: int
    modified_ns: int


@dataclass(frozen=True)
class ArchiveProvenance:
    identity: FileIdentity
    archive_sha256: str
    acceptable_active_sha256s: frozenset[str]


@dataclass(frozen=True)
class TaskPlan:
    checklist_items: tuple[tuple[str, str], ...]
    execution_steps: tuple[tuple[str, str], ...]


def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_expected_sha256(expected_sha256: str) -> None:
    if not SHA256_PATTERN.fullmatch(expected_sha256):
        raise TaskRuntimeError("Expected SHA-256 must contain exactly 64 lowercase hex characters")


def validate_task_slug(task: str) -> None:
    if not TASK_SLUG_PATTERN.fullmatch(task):
        raise TaskRuntimeError(f"Invalid task slug: {task!r}")


def validate_iso_date(date_text: str) -> None:
    if not ISO_DATE_PATTERN.fullmatch(date_text):
        raise TaskRuntimeError(f"Invalid date: {date_text!r}")
    try:
        date.fromisoformat(date_text)
    except ValueError as error:
        raise TaskRuntimeError(f"Invalid date: {date_text!r}") from error


def parse_archived_task_filename(path: Path) -> tuple[str, int, str]:
    filename_match = ARCHIVED_TASK_FILENAME_PATTERN.fullmatch(path.name)
    if filename_match is None:
        raise TaskRuntimeError(
            "Archived Task filename must use YYYY-MM-DD-NNN-{task}.md"
        )
    archive_date = filename_match.group("archive_date")
    validate_iso_date(archive_date)
    daily_sequence = int(filename_match.group("daily_sequence"))
    if daily_sequence < 1:
        raise TaskRuntimeError("Archived Task daily sequence must start at 001")
    task = filename_match.group("task")
    validate_task_slug(task)
    return archive_date, daily_sequence, task


def resolve_root(root: Path) -> Path:
    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise TaskRuntimeError(f"Repository root is not a directory: {resolved_root}")
    return resolved_root


def ensure_path_has_no_symlink(root: Path, target: Path) -> None:
    try:
        relative_target = target.relative_to(root)
    except ValueError as error:
        raise TaskRuntimeError(f"Task path escapes repository root: {target}") from error

    current_path = root
    for path_component in relative_target.parts:
        current_path = current_path / path_component
        if current_path.is_symlink():
            raise TaskRuntimeError(f"Task path contains a symlink: {current_path}")


def build_task_paths(root: Path, task: str) -> TaskPaths:
    validate_task_slug(task)
    resolved_root = resolve_root(root)
    task_root = resolved_root / "codestable" / "tasks"
    active_root = task_root / "active"
    archived_root = task_root / "archived"
    task_paths = TaskPaths(
        root=resolved_root,
        task_root=task_root,
        active_root=active_root,
        archived_root=archived_root,
        active_path=active_root / f"{task}.md",
    )
    for managed_path in (
        task_paths.task_root,
        task_paths.active_root,
        task_paths.archived_root,
        task_paths.active_path,
    ):
        ensure_path_has_no_symlink(resolved_root, managed_path)
    return task_paths


def ensure_task_directories(task_paths: TaskPaths) -> None:
    for directory in (task_paths.active_root, task_paths.archived_root):
        directory.mkdir(parents=True, exist_ok=True)
        ensure_path_has_no_symlink(task_paths.root, directory)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(temporary_descriptor, "w", encoding="utf-8", newline="\n") as file_handle:
            file_handle.write(content)
            file_handle.flush()
            os.fsync(file_handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def publish_archive_without_overwrite(source_path: Path, destination_path: Path) -> None:
    """Publish an archive atomically without replacing existing evidence."""
    os.link(source_path, destination_path)


def publish_active_task_without_overwrite(source_path: Path, destination_path: Path) -> None:
    """Publish a newly created active Task without replacing existing evidence."""
    os.link(source_path, destination_path)


def atomic_create_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(temporary_descriptor, "w", encoding="utf-8", newline="\n") as file_handle:
            file_handle.write(content)
            file_handle.flush()
            os.fsync(file_handle.fileno())
        try:
            publish_active_task_without_overwrite(temporary_path, path)
        except FileExistsError as error:
            raise TaskRuntimeError(
                "Active task target appeared during creation; existing evidence was preserved"
            ) from error
    finally:
        temporary_path.unlink(missing_ok=True)


def parse_frontmatter(content: str) -> dict[str, object]:
    match = FRONTMATTER_PATTERN.match(content)
    if match is None:
        raise TaskRuntimeError("Task document is missing YAML frontmatter")

    frontmatter: dict[str, object] = {}
    list_field: str | None = None
    for raw_line in match.group("body").splitlines():
        if raw_line.startswith("  - "):
            if list_field is None:
                raise TaskRuntimeError("Task frontmatter contains an orphaned list item")
            list_value = frontmatter.setdefault(list_field, [])
            if not isinstance(list_value, list):
                raise TaskRuntimeError(f"Task frontmatter field is not a list: {list_field}")
            list_value.append(raw_line[4:].strip())
            continue

        list_field = None
        field_name, separator, raw_value = raw_line.partition(":")
        if not separator or not field_name.strip():
            raise TaskRuntimeError(f"Invalid Task frontmatter line: {raw_line!r}")
        field_name = field_name.strip()
        field_value = raw_value.strip()
        if field_name in frontmatter:
            raise TaskRuntimeError(f"Task frontmatter contains a duplicate field: {field_name}")
        if field_value == "":
            frontmatter[field_name] = []
            list_field = field_name
        elif field_value == "[]":
            frontmatter[field_name] = []
        elif field_value == "null":
            frontmatter[field_name] = None
        else:
            frontmatter[field_name] = field_value.strip('"')
    return frontmatter


def extract_section(content: str, heading: str, next_heading: str) -> str:
    section_pattern = re.compile(
        rf"(?ms)^{re.escape(heading)}\s*$\n(?P<section>.*?)^{re.escape(next_heading)}\s*$"
    )
    match = section_pattern.search(content)
    if match is None:
        raise TaskRuntimeError(f"Task document has an invalid section boundary: {heading}")
    return match.group("section")


def is_lifecycle_only_step(title: str) -> bool:
    normalized_title = " ".join(title.strip().split())
    if ARCHIVE_TERM_PATTERN.search(normalized_title) is None:
        return False
    if ANALYTICAL_ARCHIVE_STEP_PATTERN.search(normalized_title):
        return False

    normalized_lowercase_title = normalized_title.lower()
    references_task = "任务" in normalized_title or re.search(
        r"\btask\b",
        normalized_lowercase_title,
    )
    starts_with_archive_term = normalized_title.startswith("归档") or re.match(
        r"^(?:archive|archiving|archival)\b",
        normalized_lowercase_title,
        re.IGNORECASE,
    )
    has_command_verb = ARCHIVE_COMMAND_STEP_PATTERN.search(normalized_title)
    joins_archive_to_follow_up_work = re.search(
        r"归档\s*(?:并|然后)|\barchive\b\s+(?:and|then)\b",
        normalized_title,
        re.IGNORECASE,
    )
    is_bare_archive_action = bool(
        re.fullmatch(r"(?:归档|archive|archiving|archival)", normalized_title, re.IGNORECASE)
    )
    return bool(
        references_task
        or starts_with_archive_term
        or has_command_verb
        or joins_archive_to_follow_up_work
        or is_bare_archive_action
    )


def parse_task_plan(
    content: str,
    allow_legacy_title_mismatch: bool = False,
    allow_legacy_lifecycle_step: bool = False,
) -> TaskPlan:
    checklist_section = extract_section(
        content,
        "## 3. Agent 原生 Tasks 同步区",
        "## 4. CodeStable 文档索引",
    )
    checklist_items = tuple(
        (match.group("state"), match.group("title").strip())
        for match in re.finditer(
            r"(?m)^- \[(?P<state>[ x])\] (?P<title>.+?)\s*$",
            checklist_section,
        )
    )
    if not checklist_items:
        raise TaskRuntimeError("Task must contain at least one native Tasks checklist item")
    checklist_titles = [title for _, title in checklist_items]
    if len(checklist_titles) != len(set(checklist_titles)):
        raise TaskRuntimeError("Task native Tasks checklist contains duplicate items")

    execution_section = extract_section(
        content,
        "## 5. 执行步骤",
        "## 6. 中断恢复提示",
    )
    step_matches = list(
        re.finditer(r"(?m)^### (?P<number>\d+)\. (?P<title>.+?)\s*$", execution_section)
    )
    if not step_matches:
        raise TaskRuntimeError("Task must contain at least one execution step")

    execution_steps: list[tuple[str, str]] = []
    expected_numbers = list(range(1, len(step_matches) + 1))
    actual_numbers = [int(match.group("number")) for match in step_matches]
    if actual_numbers != expected_numbers:
        raise TaskRuntimeError("Task execution step numbers must be contiguous and start at one")
    for step_index, step_match in enumerate(step_matches):
        block_start = step_match.end()
        block_end = (
            step_matches[step_index + 1].start()
            if step_index + 1 < len(step_matches)
            else len(execution_section)
        )
        step_block = execution_section[block_start:block_end]
        status_matches = re.findall(r"(?m)^- 状态：([^\n]+)\s*$", step_block)
        if len(status_matches) != 1:
            raise TaskRuntimeError("Each Task execution step must contain exactly one status")
        execution_status = status_matches[0].strip()
        if execution_status not in EXECUTION_STATUSES:
            raise TaskRuntimeError(f"Task execution step status is invalid: {execution_status}")
        execution_steps.append((execution_status, step_match.group("title").strip()))

    execution_titles = [title for _, title in execution_steps]
    if len(execution_titles) != len(set(execution_titles)):
        raise TaskRuntimeError("Task execution steps contain duplicate titles")
    if len(checklist_items) != len(execution_steps):
        raise TaskRuntimeError("Task checklist and execution steps must contain the same item count")
    if not allow_legacy_title_mismatch and checklist_titles != execution_titles:
        raise TaskRuntimeError(
            "Task checklist and execution step titles must match in the same order"
        )
    if not allow_legacy_lifecycle_step and any(
        is_lifecycle_only_step(title) for title in checklist_titles + execution_titles
    ):
        raise TaskRuntimeError(
            "Task plans must not include archive lifecycle operations as work steps"
        )
    return TaskPlan(checklist_items=checklist_items, execution_steps=tuple(execution_steps))


def validate_task_document(
    content: str,
    task: str,
    archived: bool = False,
    allow_legacy_plan_mismatch: bool = False,
    allow_legacy_lifecycle_step: bool = False,
) -> dict[str, object]:
    validate_task_slug(task)
    frontmatter = parse_frontmatter(content)
    missing_fields = TASK_REQUIRED_FIELDS.difference(frontmatter)
    if missing_fields:
        raise TaskRuntimeError(
            f"Task frontmatter is missing required fields: {sorted(missing_fields)!r}"
        )
    unknown_fields = set(frontmatter).difference(TASK_REQUIRED_FIELDS)
    if unknown_fields:
        raise TaskRuntimeError(
            f"Task frontmatter contains unknown fields: {sorted(unknown_fields)!r}"
        )
    if frontmatter["doc_type"] != "task-list":
        raise TaskRuntimeError("Task doc_type must be task-list")
    if frontmatter["task"] != task:
        raise TaskRuntimeError("Task frontmatter slug does not match the target filename")
    for required_text_field in ("goal", "workflow", "owner_skill", "created", "updated"):
        field_value = frontmatter[required_text_field]
        if not isinstance(field_value, str) or not field_value.strip():
            raise TaskRuntimeError(f"Task frontmatter field must be non-empty: {required_text_field}")
    if frontmatter["owner_skill"] != "cs":
        raise TaskRuntimeError("Task owner_skill must be cs in CodeStable Lite")
    validate_iso_date(str(frontmatter["created"]))
    validate_iso_date(str(frontmatter["updated"]))

    status = str(frontmatter["status"])
    allowed_statuses = {"archived"} if archived else ACTIVE_STATUSES
    if status not in allowed_statuses:
        raise TaskRuntimeError(f"Task status is invalid for this location: {status}")
    archived_date = frontmatter["archived"]
    if archived:
        if not isinstance(archived_date, str):
            raise TaskRuntimeError("Archived Task must record an archive date")
        validate_iso_date(archived_date)
    elif archived_date is not None:
        raise TaskRuntimeError("Active Task archived field must be null")
    if not isinstance(frontmatter["related_docs"], list):
        raise TaskRuntimeError("Task related_docs must be a list")
    for section_heading in TASK_SECTION_HEADINGS:
        section_occurrence_count = len(
            re.findall(rf"(?m)^{re.escape(section_heading)}\s*$", content)
        )
        if section_occurrence_count == 0:
            raise TaskRuntimeError(f"Task document is missing section: {section_heading}")
        if section_occurrence_count != 1:
            raise TaskRuntimeError(f"Task document contains a duplicate section: {section_heading}")
    document_section_headings = tuple(
        match.group("heading").rstrip()
        for match in re.finditer(r"(?m)^(?P<heading>## .+?)\s*$", content)
    )
    if document_section_headings != TASK_SECTION_HEADINGS:
        raise TaskRuntimeError(
            "Task document sections must exactly match the fixed headings in order"
        )
    current_status_section = extract_section(content, "## 2. 当前状态", "## 3. Agent 原生 Tasks 同步区")
    current_status_lines = [line.strip() for line in current_status_section.splitlines() if line.strip()]
    if current_status_lines != [status]:
        raise TaskRuntimeError("Task current status section must match frontmatter status")
    task_plan = parse_task_plan(
        content,
        allow_legacy_title_mismatch=allow_legacy_plan_mismatch,
        allow_legacy_lifecycle_step=allow_legacy_lifecycle_step,
    )
    for (checklist_state, checklist_title), (execution_status, execution_title) in zip(
        task_plan.checklist_items,
        task_plan.execution_steps,
        strict=True,
    ):
        step_is_complete = checklist_state == "x"
        execution_is_complete = execution_status == "done"
        if step_is_complete != execution_is_complete:
            raise TaskRuntimeError(
                "Task checklist and execution status must agree for step: "
                f"{checklist_title or execution_title}"
            )
    return frontmatter


def validate_status_transition(current_status: str, candidate_status: str) -> None:
    allowed_statuses = ACTIVE_STATUS_TRANSITIONS.get(current_status, frozenset())
    if candidate_status not in allowed_statuses:
        raise TaskRuntimeError(
            f"Illegal Task status transition: {current_status} -> {candidate_status}"
        )


def validate_plan_preserved(current_content: str, candidate_content: str) -> None:
    current_plan = parse_task_plan(
        current_content,
        allow_legacy_title_mismatch=True,
        allow_legacy_lifecycle_step=True,
    )
    candidate_plan = parse_task_plan(candidate_content)
    current_checklist_titles = [title for _, title in current_plan.checklist_items]
    current_execution_titles = [title for _, title in current_plan.execution_steps]
    candidate_titles = [title for _, title in candidate_plan.checklist_items]
    preserved_step_indexes = [
        step_index
        for step_index, title in enumerate(current_checklist_titles)
        if not is_lifecycle_only_step(title)
        and not is_lifecycle_only_step(current_execution_titles[step_index])
    ]
    if len(candidate_titles) < len(preserved_step_indexes):
        raise TaskRuntimeError("Task update cannot remove a committed step")

    current_titles_are_aligned = current_checklist_titles == current_execution_titles
    if current_titles_are_aligned:
        required_titles = [current_checklist_titles[index] for index in preserved_step_indexes]
        if candidate_titles[: len(required_titles)] != required_titles:
            raise TaskRuntimeError("Task update cannot rename or reorder a committed step")
        return

    # Legacy Tasks may have used different display titles for the two plan views.
    # Reconciliation can select either existing title at each position, but cannot invent a new one.
    for candidate_index, step_index in enumerate(preserved_step_indexes):
        candidate_title = candidate_titles[candidate_index]
        allowed_titles = {
            current_checklist_titles[step_index],
            current_execution_titles[step_index],
        }
        if candidate_title not in allowed_titles:
            raise TaskRuntimeError("Task plan reconciliation cannot invent a new step identity")


def validate_completion_gate(content: str) -> None:
    task_plan = parse_task_plan(content)
    if any(state != "x" for state, _ in task_plan.checklist_items):
        raise TaskRuntimeError("Task has unfinished work in its native Tasks checklist")
    if any(status != "done" for status, _ in task_plan.execution_steps):
        raise TaskRuntimeError("Task has unfinished work in its execution steps")


def validate_update_preserves_protected_fields(
    current_frontmatter: dict[str, object],
    candidate_frontmatter: dict[str, object],
) -> None:
    for field_name in PROTECTED_UPDATE_FIELDS:
        if current_frontmatter[field_name] != candidate_frontmatter[field_name]:
            raise TaskRuntimeError(f"Task update attempted to change protected Task field: {field_name}")


def replace_frontmatter_field(content: str, field_name: str, value: str) -> str:
    field_pattern = re.compile(rf"(?m)^{re.escape(field_name)}:\s*.*$")
    if field_pattern.search(content) is None:
        raise TaskRuntimeError(f"Task frontmatter field is missing: {field_name}")
    return field_pattern.sub(f"{field_name}: {value}", content, count=1)


def replace_current_status(content: str, status: str) -> str:
    section_pattern = re.compile(r"(?m)(^## 2\. 当前状态\s*$\n+)([^\n]+)")
    if section_pattern.search(content) is None:
        raise TaskRuntimeError("Task current status section is invalid")
    return section_pattern.sub(rf"\g<1>{status}", content, count=1)


def append_archive_record(content: str, record: str) -> str:
    return f"{content.rstrip()}\n\n{record}\n"


def render_task_document(
    task: str,
    goal: str,
    workflow: str,
    owner: str,
    steps: Sequence[str],
    related_docs: Sequence[str],
    current_date: str,
) -> str:
    validate_iso_date(current_date)
    if not steps:
        raise TaskRuntimeError("Task creation requires at least one committed step")
    normalized_steps = [step.strip() for step in steps]
    if any(not step for step in normalized_steps):
        raise TaskRuntimeError("Task steps cannot be empty")
    if len(normalized_steps) != len(set(normalized_steps)):
        raise TaskRuntimeError("Task steps must be unique")
    if any(is_lifecycle_only_step(step) for step in normalized_steps):
        raise TaskRuntimeError(
            "Task plans must not include archive lifecycle operations as work steps"
        )

    related_doc_lines = (
        "\n".join(f"  - {related_doc}" for related_doc in related_docs)
        if related_docs
        else "related_docs: []"
    )
    related_doc_frontmatter = (
        f"related_docs:\n{related_doc_lines}" if related_docs else related_doc_lines
    )
    related_doc_body = (
        "\n".join(f"- `{related_doc}`" for related_doc in related_docs)
        if related_docs
        else "无。"
    )
    step_checklist = "\n".join(f"- [ ] {step}" for step in normalized_steps)
    step_sections = "\n\n".join(
        f"### {step_index}. {step}\n\n- 状态：pending"
        for step_index, step in enumerate(normalized_steps, start=1)
    )
    return (
        "---\n"
        "doc_type: task-list\n"
        f"task: {task}\n"
        f"goal: {goal}\n"
        "status: active\n"
        f"workflow: {workflow}\n"
        f"owner_skill: {owner}\n"
        f"created: {current_date}\n"
        f"updated: {current_date}\n"
        "archived: null\n"
        f"{related_doc_frontmatter}\n"
        "---\n\n"
        f"# {goal}\n\n"
        "## 1. 任务目标\n\n"
        f"{goal}\n\n"
        "## 2. 当前状态\n\n"
        "active\n\n"
        "## 3. Agent 原生 Tasks 同步区\n\n"
        f"{step_checklist}\n\n"
        "## 4. CodeStable 文档索引\n\n"
        f"{related_doc_body}\n\n"
        "## 5. 执行步骤\n\n"
        f"{step_sections}\n\n"
        "## 6. 中断恢复提示\n\n"
        "从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。"
        "计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。\n\n"
        "## 7. 完成与归档记录\n\n"
        f"{current_date}：Task 已创建。\n"
    )


def archived_files_for_task(task_paths: TaskPaths) -> list[Path]:
    archived_paths: list[Path] = []
    if not task_paths.archived_root.is_dir():
        return archived_paths
    for archived_entry in task_paths.archived_root.iterdir():
        if not archived_entry.is_file() or archived_entry.is_symlink():
            continue
        try:
            _, _, archived_task = parse_archived_task_filename(archived_entry)
        except TaskRuntimeError:
            continue
        if archived_task == task_paths.active_path.stem:
            archived_paths.append(archived_entry)
    return sorted(archived_paths)


def noncanonical_archive_entries(task_paths: TaskPaths) -> list[tuple[Path, TaskRuntimeError]]:
    invalid_entries: list[tuple[Path, TaskRuntimeError]] = []
    if not task_paths.archived_root.is_dir():
        return invalid_entries
    for archived_entry in task_paths.archived_root.iterdir():
        if archived_entry.is_symlink() or not archived_entry.is_file():
            invalid_entries.append(
                (
                    archived_entry,
                    TaskRuntimeError(
                        "Archived Task workspace may contain only regular lowercase .md files"
                    ),
                )
            )
            continue
        try:
            parse_archived_task_filename(archived_entry)
        except TaskRuntimeError as error:
            invalid_entries.append((archived_entry, error))
    return sorted(invalid_entries, key=lambda entry: entry[0].name)


def validate_archive_workspace_filenames(task_paths: TaskPaths) -> None:
    invalid_entries = noncanonical_archive_entries(task_paths)
    if invalid_entries:
        invalid_path, invalid_error = invalid_entries[0]
        raise TaskRuntimeError(
            "Archived workspace contains a noncanonical file: "
            f"{invalid_path.name}. {invalid_error}"
        )


def allocate_daily_archive_path(task_paths: TaskPaths, archive_date: str) -> Path:
    validate_archive_workspace_filenames(task_paths)
    daily_sequences: list[int] = []
    for archived_entry in task_paths.archived_root.iterdir():
        if not archived_entry.is_file() or archived_entry.is_symlink():
            continue
        entry_archive_date, daily_sequence, _ = parse_archived_task_filename(archived_entry)
        if entry_archive_date == archive_date:
            daily_sequences.append(daily_sequence)

    sorted_daily_sequences = sorted(daily_sequences)
    expected_daily_sequences = list(range(1, len(sorted_daily_sequences) + 1))
    if sorted_daily_sequences != expected_daily_sequences:
        raise TaskRuntimeError(
            f"Archive date {archive_date} must contain unique contiguous sequences from 001"
        )
    next_daily_sequence = max(daily_sequences, default=0) + 1
    if next_daily_sequence > MAX_DAILY_ARCHIVE_SEQUENCE:
        raise TaskRuntimeError(
            f"Archive date {archive_date} already contains the maximum "
            f"{MAX_DAILY_ARCHIVE_SEQUENCE} Tasks"
        )
    archived_path = task_paths.archived_root / (
        f"{archive_date}-{next_daily_sequence:03d}-{task_paths.active_path.stem}.md"
    )
    ensure_path_has_no_symlink(task_paths.root, archived_path)
    return archived_path


def migrate_legacy_archive_filenames(root: Path) -> list[dict[str, str]]:
    resolved_root = resolve_root(root)
    archived_root = resolved_root / "codestable" / "tasks" / "archived"
    ensure_path_has_no_symlink(resolved_root, archived_root)
    if not archived_root.is_dir():
        raise TaskRuntimeError(f"Archived Task workspace is missing: {archived_root}")

    legacy_archives_by_date: dict[str, list[tuple[Path, str]]] = {}
    canonical_dates: set[str] = set()
    for archived_entry in sorted(archived_root.iterdir()):
        if archived_entry.is_symlink() or not archived_entry.is_file():
            raise TaskRuntimeError(
                "Archive filename migration requires only regular .md files in archived"
            )
        archived_content = archived_entry.read_text(encoding="utf-8")
        archived_frontmatter = parse_frontmatter(archived_content)
        frontmatter_task = str(archived_frontmatter.get("task"))
        try:
            archive_date, _, canonical_task = parse_archived_task_filename(archived_entry)
            if frontmatter_task == canonical_task:
                validate_task_document(archived_content, canonical_task, archived=True)
                if archived_frontmatter["archived"] != archive_date:
                    raise TaskRuntimeError(
                        f"Canonical archive date does not match document: {archived_entry.name}"
                    )
                canonical_dates.add(archive_date)
                continue
        except TaskRuntimeError:
            pass

        legacy_match = LEGACY_ARCHIVED_TASK_FILENAME_PATTERN.fullmatch(archived_entry.name)
        if legacy_match is None:
            raise TaskRuntimeError(
                f"Archive filename migration found an unsupported file: {archived_entry.name}"
            )
        archive_date = legacy_match.group("archive_date")
        task = legacy_match.group("task")
        validate_iso_date(archive_date)
        validate_task_slug(task)
        archived_frontmatter = validate_task_document(archived_content, task, archived=True)
        if archived_frontmatter["archived"] != archive_date:
            raise TaskRuntimeError(
                f"Legacy archive date does not match document: {archived_entry.name}"
            )
        legacy_archives_by_date.setdefault(archive_date, []).append((archived_entry, task))

    migrated_paths: list[dict[str, str]] = []
    for archive_date, legacy_archives in sorted(legacy_archives_by_date.items()):
        if archive_date in canonical_dates or len(legacy_archives) != 1:
            raise TaskRuntimeError(
                "Archive filename migration cannot infer completion order for "
                f"{archive_date}; assign YYYY-MM-DD-NNN names manually first"
            )
        legacy_path, task = legacy_archives[0]
        migrated_path = archived_root / f"{archive_date}-001-{task}.md"
        try:
            os.link(legacy_path, migrated_path)
        except FileExistsError as error:
            raise TaskRuntimeError(
                f"Archive filename migration target already exists: {migrated_path.name}"
            ) from error
        legacy_path.unlink()
        migrated_paths.append(
            {
                "from": legacy_path.relative_to(resolved_root).as_posix(),
                "to": migrated_path.relative_to(resolved_root).as_posix(),
            }
        )
    return migrated_paths


def unexpected_active_workspace_entries(task_paths: TaskPaths) -> list[Path]:
    unexpected_entries: list[Path] = []
    if not task_paths.active_root.is_dir():
        return unexpected_entries
    for active_entry in task_paths.active_root.iterdir():
        entry_is_regular_markdown = (
            not active_entry.is_symlink()
            and active_entry.is_file()
            and active_entry.suffix == ".md"
            and TASK_SLUG_PATTERN.fullmatch(active_entry.stem) is not None
        )
        if not entry_is_regular_markdown:
            unexpected_entries.append(active_entry)
    return sorted(unexpected_entries)


def validate_active_mutation_preflight(
    task_paths: TaskPaths,
    expected_sha256: str,
) -> None:
    if archived_files_for_task(task_paths):
        raise TaskRuntimeError(
            "Task exists in both active and archived locations; preserve both and resolve the conflict"
        )
    if not task_paths.active_path.is_file():
        raise TaskRuntimeError(f"Active task does not exist: {task_paths.active_path}")
    if calculate_sha256(task_paths.active_path) != expected_sha256:
        raise TaskRuntimeError(
            "Active task content changed after it was read; reload and merge before retrying"
        )


def create_task(
    root: Path,
    task: str,
    goal: str,
    workflow: str,
    owner: str,
    steps: Sequence[str],
    related_docs: Sequence[str],
    current_date: str | None = None,
) -> Path:
    task_paths = build_task_paths(root, task)
    ensure_task_directories(task_paths)
    validate_archive_workspace_filenames(task_paths)
    creation_date = current_date or date.today().isoformat()
    content = render_task_document(
        task=task,
        goal=goal,
        workflow=workflow,
        owner=owner,
        steps=steps,
        related_docs=related_docs,
        current_date=creation_date,
    )
    validate_task_document(content, task)
    if task_paths.active_path.exists():
        raise TaskRuntimeError(f"Active task already exists: {task_paths.active_path}")
    if archived_files_for_task(task_paths):
        raise TaskRuntimeError(f"Archived task already exists for slug: {task}")
    atomic_create_text(task_paths.active_path, content)
    return task_paths.active_path


def write_active_task(
    root: Path,
    task: str,
    content_path: Path,
    expected_sha256: str,
) -> Path:
    validate_expected_sha256(expected_sha256)
    task_paths = build_task_paths(root, task)
    candidate_content = content_path.read_text(encoding="utf-8")
    candidate_frontmatter = validate_task_document(candidate_content, task)
    validate_active_mutation_preflight(task_paths, expected_sha256)

    current_content = task_paths.active_path.read_text(encoding="utf-8")
    current_frontmatter = validate_task_document(
        current_content,
        task,
        allow_legacy_plan_mismatch=True,
        allow_legacy_lifecycle_step=True,
    )
    current_status = str(current_frontmatter["status"])
    candidate_status = str(candidate_frontmatter["status"])
    if current_status not in {"active", "blocked"}:
        raise TaskRuntimeError("Completed or cancelled Tasks are frozen and can only be archived")
    validate_status_transition(current_status, candidate_status)
    validate_update_preserves_protected_fields(current_frontmatter, candidate_frontmatter)
    validate_plan_preserved(current_content, candidate_content)
    validate_active_mutation_preflight(task_paths, expected_sha256)
    atomic_write_text(task_paths.active_path, candidate_content)
    return task_paths.active_path


def update_task(
    root: Path,
    task: str,
    expected_sha256: str,
    replacements: dict[str, str],
    progress_record: str,
    current_date: str | None = None,
) -> Path:
    validate_expected_sha256(expected_sha256)
    task_paths = build_task_paths(root, task)
    update_date = current_date or date.today().isoformat()
    validate_iso_date(update_date)
    if not progress_record.strip():
        raise TaskRuntimeError("Task update requires a non-empty progress record")
    validate_active_mutation_preflight(task_paths, expected_sha256)

    current_content = task_paths.active_path.read_text(encoding="utf-8")
    current_frontmatter = validate_task_document(
        current_content,
        task,
        allow_legacy_plan_mismatch=True,
        allow_legacy_lifecycle_step=True,
    )
    if current_frontmatter["status"] not in {"active", "blocked"}:
        raise TaskRuntimeError("Only active or blocked Tasks can receive progress updates")
    candidate_content = current_content
    for old_text, new_text in replacements.items():
        occurrence_count = candidate_content.count(old_text)
        if occurrence_count != 1:
            raise TaskRuntimeError(
                "Each guarded Task replacement must match exactly once; "
                f"matched {occurrence_count} times: {old_text!r}"
            )
        candidate_content = candidate_content.replace(old_text, new_text, 1)
    candidate_content = replace_frontmatter_field(candidate_content, "updated", update_date)
    candidate_content = append_archive_record(
        candidate_content,
        f"{update_date}：{progress_record}",
    )
    candidate_frontmatter = validate_task_document(candidate_content, task)
    validate_update_preserves_protected_fields(current_frontmatter, candidate_frontmatter)
    validate_plan_preserved(current_content, candidate_content)
    validate_active_mutation_preflight(task_paths, expected_sha256)
    atomic_write_text(task_paths.active_path, candidate_content)
    return task_paths.active_path


def set_task_status(
    root: Path,
    task: str,
    target_status: str,
    expected_sha256: str,
    reason: str,
    current_date: str | None = None,
) -> Path:
    validate_expected_sha256(expected_sha256)
    task_paths = build_task_paths(root, task)
    status_date = current_date or date.today().isoformat()
    validate_iso_date(status_date)
    if target_status not in ACTIVE_STATUSES:
        raise TaskRuntimeError(f"Illegal Task status transition target: {target_status}")
    validate_active_mutation_preflight(task_paths, expected_sha256)

    content = task_paths.active_path.read_text(encoding="utf-8")
    frontmatter = validate_task_document(content, task)
    current_status = str(frontmatter["status"])
    if current_status not in {"active", "blocked"}:
        raise TaskRuntimeError("Completed or cancelled Tasks are frozen and can only be archived")
    if target_status == current_status:
        raise TaskRuntimeError("Task status command must change the current status")
    validate_status_transition(current_status, target_status)
    if target_status == "completed":
        raise TaskRuntimeError("Use the complete command to apply the Task completion gate")
    content = replace_frontmatter_field(content, "status", target_status)
    content = replace_frontmatter_field(content, "updated", status_date)
    content = replace_current_status(content, target_status)
    content = append_archive_record(
        content,
        f"{status_date}：Task 状态从 {current_status} 变更为 {target_status}。原因：{reason}",
    )
    validate_task_document(content, task)
    validate_active_mutation_preflight(task_paths, expected_sha256)
    atomic_write_text(task_paths.active_path, content)
    return task_paths.active_path


def complete_task(
    root: Path,
    task: str,
    expected_sha256: str,
    current_date: str | None = None,
) -> Path:
    validate_expected_sha256(expected_sha256)
    task_paths = build_task_paths(root, task)
    completion_date = current_date or date.today().isoformat()
    validate_iso_date(completion_date)
    validate_active_mutation_preflight(task_paths, expected_sha256)

    content = task_paths.active_path.read_text(encoding="utf-8")
    frontmatter = validate_task_document(content, task)
    if frontmatter["status"] != "active":
        raise TaskRuntimeError("Only an active Task can be marked completed")
    validate_completion_gate(content)
    content = replace_frontmatter_field(content, "status", "completed")
    content = replace_frontmatter_field(content, "updated", completion_date)
    content = replace_current_status(content, "completed")
    content = append_archive_record(
        content,
        f"{completion_date}：Task 已标记 completed，等待归档。",
    )
    validate_task_document(content, task)
    validate_active_mutation_preflight(task_paths, expected_sha256)
    atomic_write_text(task_paths.active_path, content)
    return task_paths.active_path


def render_archived_task_content(
    source_content: str,
    archive_date: str,
    source_sha256: str | None = None,
) -> str:
    archived_content = replace_frontmatter_field(source_content, "status", "archived")
    archived_content = replace_frontmatter_field(archived_content, "updated", archive_date)
    archived_content = replace_frontmatter_field(archived_content, "archived", archive_date)
    archived_content = replace_current_status(archived_content, "archived")
    archive_record = f"{archive_date}：Task 已原子移动到 archived，active 正本已移除。"
    if source_sha256 is not None:
        validate_expected_sha256(source_sha256)
        archive_record = f"{archive_record} 源快照 SHA-256：{source_sha256}"
    return append_archive_record(
        archived_content,
        archive_record,
    )


def extract_archived_source_sha256(archived_content: str, archive_date: str) -> str | None:
    final_record = archived_content.rstrip().splitlines()[-1]
    record_pattern = re.compile(
        rf"{re.escape(archive_date)}：Task 已原子移动到 archived，active 正本已移除。 "
        r"源快照 SHA-256：(?P<sha256>[0-9a-f]{64})"
    )
    record_match = record_pattern.fullmatch(final_record)
    return record_match.group("sha256") if record_match is not None else None


def build_file_identity(file_stat: os.stat_result) -> FileIdentity:
    return FileIdentity(
        device=file_stat.st_dev,
        inode=file_stat.st_ino,
        size=file_stat.st_size,
        modified_ns=file_stat.st_mtime_ns,
    )


def read_file_snapshot(path: Path) -> tuple[bytes, FileIdentity]:
    with path.open("rb") as file_handle:
        identity_before_read = build_file_identity(os.fstat(file_handle.fileno()))
        content = file_handle.read()
        identity_after_read = build_file_identity(os.fstat(file_handle.fileno()))
    if identity_before_read != identity_after_read:
        raise TaskRuntimeError(f"File changed while it was being read: {path}")
    return content, identity_after_read


def read_archive_provenance(
    task_paths: TaskPaths,
    archived_path: Path,
) -> ArchiveProvenance:
    ensure_path_has_no_symlink(task_paths.root, archived_path)
    archived_bytes, archive_identity = read_file_snapshot(archived_path)
    archived_content = archived_bytes.decode("utf-8")
    archived_frontmatter = validate_task_document(
        archived_content,
        task_paths.active_path.stem,
        archived=True,
    )
    archive_date = str(archived_frontmatter["archived"])
    filename_archive_date, _, filename_task = parse_archived_task_filename(archived_path)
    if filename_archive_date != archive_date or filename_task != task_paths.active_path.stem:
        raise TaskRuntimeError("Archived Task date does not match its filename")
    archive_sha256 = hashlib.sha256(archived_bytes).hexdigest()
    acceptable_active_sha256s = {archive_sha256}
    archived_source_sha256 = extract_archived_source_sha256(
        archived_content,
        archive_date,
    )
    if archived_source_sha256 is not None:
        acceptable_active_sha256s.add(archived_source_sha256)
    return ArchiveProvenance(
        identity=archive_identity,
        archive_sha256=archive_sha256,
        acceptable_active_sha256s=frozenset(acceptable_active_sha256s),
    )


def archive_provenance_is_current(
    task_paths: TaskPaths,
    archived_path: Path,
    expected_provenance: ArchiveProvenance,
) -> bool:
    if archived_files_for_task(task_paths) != [archived_path]:
        return False
    try:
        archived_bytes, current_identity = read_file_snapshot(archived_path)
    except (OSError, TaskRuntimeError):
        return False
    return (
        current_identity == expected_provenance.identity
        and hashlib.sha256(archived_bytes).hexdigest() == expected_provenance.archive_sha256
    )


def move_active_task_to_quarantine(task_paths: TaskPaths) -> Path | None:
    temporary_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{task_paths.active_path.name}.",
        suffix=".cleanup-residue",
        dir=task_paths.active_root,
    )
    os.close(temporary_descriptor)
    quarantine_path = Path(temporary_name)
    move_succeeded = False
    try:
        os.replace(task_paths.active_path, quarantine_path)
        move_succeeded = True
    except FileNotFoundError:
        return None
    finally:
        if not move_succeeded:
            quarantine_path.unlink(missing_ok=True)
    return quarantine_path


def quarantine_files_for_task(task_paths: TaskPaths) -> list[Path]:
    quarantine_pattern = f".{task_paths.active_path.name}.*.cleanup-residue"
    return sorted(task_paths.active_root.glob(quarantine_pattern))


def unlink_file_if_snapshot_is_current(
    path: Path,
    expected_identity: FileIdentity,
    expected_sha256: str,
) -> bool:
    try:
        with path.open("rb") as file_handle:
            current_identity = build_file_identity(os.fstat(file_handle.fileno()))
            current_sha256 = hashlib.sha256(file_handle.read()).hexdigest()
            identity_after_read = build_file_identity(os.fstat(file_handle.fileno()))
            path_identity = build_file_identity(path.lstat())
            snapshot_is_current = (
                current_identity == expected_identity
                and identity_after_read == expected_identity
                and path_identity == expected_identity
                and current_sha256 == expected_sha256
            )
            if not snapshot_is_current:
                return False
            path.unlink()
            return True
    except FileNotFoundError:
        return False


def restore_quarantined_active_task(
    task_paths: TaskPaths,
    quarantine_path: Path,
) -> None:
    quarantined_bytes, quarantine_identity = read_file_snapshot(quarantine_path)
    quarantined_sha256 = hashlib.sha256(quarantined_bytes).hexdigest()
    try:
        publish_active_task_without_overwrite(quarantine_path, task_paths.active_path)
    except FileExistsError as error:
        raise TaskRuntimeError(
            "Active Task changed during cleanup; quarantined evidence was preserved at "
            f"{quarantine_path.relative_to(task_paths.root).as_posix()}"
        ) from error
    quarantine_was_removed = unlink_file_if_snapshot_is_current(
        quarantine_path,
        quarantine_identity,
        quarantined_sha256,
    )
    if not quarantine_was_removed:
        raise TaskRuntimeError(
            "Quarantined Task changed during restoration; all evidence was preserved at "
            f"{task_paths.active_path.relative_to(task_paths.root).as_posix()} and "
            f"{quarantine_path.relative_to(task_paths.root).as_posix()}"
        )


def remove_active_task_if_proven_residue(
    task_paths: TaskPaths,
    archived_path: Path,
) -> bool:
    quarantine_path = move_active_task_to_quarantine(task_paths)
    if quarantine_path is None:
        return True

    try:
        residue_was_removed = remove_quarantined_task_if_proven_residue(
            task_paths,
            archived_path,
            quarantine_path,
        )
        if residue_was_removed:
            return True
        restore_quarantined_active_task(task_paths, quarantine_path)
        return False
    except Exception as error:
        if quarantine_path.exists():
            try:
                restore_quarantined_active_task(task_paths, quarantine_path)
            except TaskRuntimeError as restore_error:
                raise restore_error from error
        raise


def remove_quarantined_task_if_proven_residue(
    task_paths: TaskPaths,
    archived_path: Path,
    quarantine_path: Path,
) -> bool:
    archive_provenance = read_archive_provenance(task_paths, archived_path)
    quarantined_bytes, quarantine_identity = read_file_snapshot(quarantine_path)
    quarantined_sha256 = hashlib.sha256(quarantined_bytes).hexdigest()
    residue_is_proven = (
        quarantined_sha256 in archive_provenance.acceptable_active_sha256s
        and archive_provenance_is_current(
            task_paths,
            archived_path,
            archive_provenance,
        )
    )
    return residue_is_proven and unlink_file_if_snapshot_is_current(
        quarantine_path,
        quarantine_identity,
        quarantined_sha256,
    )


def recover_interrupted_archive_quarantine(
    task_paths: TaskPaths,
    archived_path: Path,
    archive_date: str,
    expected_sha256: str,
) -> ArchiveResult | None:
    quarantine_paths = quarantine_files_for_task(task_paths)
    if not quarantine_paths:
        return None
    if len(quarantine_paths) > 1 or task_paths.active_path.exists():
        raise TaskRuntimeError(
            "Archive recovery found conflicting active or quarantined Task evidence"
        )

    quarantine_path = quarantine_paths[0]
    ensure_path_has_no_symlink(task_paths.root, quarantine_path)
    existing_archives = archived_files_for_task(task_paths)
    if existing_archives == [archived_path]:
        archive_provenance = read_archive_provenance(task_paths, archived_path)
        acceptable_retry_hashes = set(archive_provenance.acceptable_active_sha256s)
        if expected_sha256 not in acceptable_retry_hashes:
            raise TaskRuntimeError(
                "Archived task content does not match the expected retry snapshot"
            )
        if not remove_quarantined_task_if_proven_residue(
            task_paths,
            archived_path,
            quarantine_path,
        ):
            raise TaskRuntimeError(
                "Interrupted archive quarantine diverged; all evidence was preserved"
            )
        return ArchiveResult(
            task=task_paths.active_path.stem,
            archived_path=archived_path.relative_to(task_paths.root).as_posix(),
        )
    if existing_archives:
        raise TaskRuntimeError("Archive recovery found multiple or mismatched archives")

    quarantined_bytes, quarantine_identity = read_file_snapshot(quarantine_path)
    quarantined_sha256 = hashlib.sha256(quarantined_bytes).hexdigest()
    quarantined_content = quarantined_bytes.decode("utf-8")
    quarantined_frontmatter = validate_task_document(
        quarantined_content,
        task_paths.active_path.stem,
        archived=True,
    )
    if quarantined_frontmatter["archived"] != archive_date:
        raise TaskRuntimeError("Interrupted archive date does not match the requested date")
    recorded_source_sha256 = extract_archived_source_sha256(
        quarantined_content,
        archive_date,
    )
    acceptable_retry_hashes = {quarantined_sha256}
    if recorded_source_sha256 is not None:
        acceptable_retry_hashes.add(recorded_source_sha256)
    if expected_sha256 not in acceptable_retry_hashes:
        raise TaskRuntimeError(
            "Interrupted archive content does not match the expected retry snapshot"
        )

    try:
        publish_archive_without_overwrite(quarantine_path, archived_path)
    except OSError as error:
        raise TaskRuntimeError(
            "Interrupted archive publication could not be resumed; evidence was preserved"
        ) from error
    published_archive_provenance = read_archive_provenance(task_paths, archived_path)
    archive_is_unique_and_current = (
        archived_files_for_task(task_paths) == [archived_path]
        and published_archive_provenance.archive_sha256 == quarantined_sha256
    )
    quarantine_was_removed = (
        archive_is_unique_and_current
        and unlink_file_if_snapshot_is_current(
            quarantine_path,
            quarantine_identity,
            quarantined_sha256,
        )
    )
    if not quarantine_was_removed:
        raise TaskRuntimeError(
            "Interrupted archive changed during recovery; all evidence was preserved"
        )
    return ArchiveResult(
        task=task_paths.active_path.stem,
        archived_path=archived_path.relative_to(task_paths.root).as_posix(),
    )


def archive_task(
    root: Path,
    task: str,
    archive_date: str,
    expected_sha256: str,
) -> ArchiveResult:
    validate_iso_date(archive_date)
    validate_expected_sha256(expected_sha256)
    task_paths = build_task_paths(root, task)
    ensure_task_directories(task_paths)
    validate_archive_workspace_filenames(task_paths)
    existing_archives = archived_files_for_task(task_paths)
    if len(existing_archives) > 1:
        raise TaskRuntimeError("Task has more than one archived document")
    archived_path = (
        existing_archives[0]
        if existing_archives
        else allocate_daily_archive_path(task_paths, archive_date)
    )
    ensure_path_has_no_symlink(task_paths.root, archived_path)
    recovery_result = recover_interrupted_archive_quarantine(
        task_paths,
        archived_path,
        archive_date,
        expected_sha256,
    )
    if recovery_result is not None:
        findings = cleanup_task(root, task)
        if findings:
            finding_codes = ", ".join(finding.code for finding in findings)
            raise TaskRuntimeError(f"Task archive recovery cleanup failed: {finding_codes}")
        return recovery_result

    if not task_paths.active_path.exists():
        if existing_archives == [archived_path]:
            build_task_summary(archived_path, task_paths.root, task, archived=True)
            archived_content = archived_path.read_text(encoding="utf-8")
            acceptable_retry_hashes = {calculate_sha256(archived_path)}
            archived_source_sha256 = extract_archived_source_sha256(
                archived_content,
                archive_date,
            )
            if archived_source_sha256 is not None:
                acceptable_retry_hashes.add(archived_source_sha256)
            if expected_sha256 not in acceptable_retry_hashes:
                raise TaskRuntimeError(
                    "Archived task content does not match the expected retry snapshot"
                )
            return ArchiveResult(
                task=task,
                archived_path=archived_path.relative_to(task_paths.root).as_posix(),
            )
        raise TaskRuntimeError("Task has no active source that can be archived")
    if existing_archives:
        if existing_archives == [archived_path] and archived_path.is_file():
            if calculate_sha256(task_paths.active_path) != expected_sha256:
                raise TaskRuntimeError(
                    "Active task content changed after it was read; reload before archiving"
                )
            build_task_summary(archived_path, task_paths.root, task, archived=True)
            removed_proven_residue = remove_active_task_if_proven_residue(
                task_paths,
                archived_path,
            )
            if removed_proven_residue and not task_paths.active_path.exists():
                findings = cleanup_task(root, task)
                if findings:
                    finding_codes = ", ".join(finding.code for finding in findings)
                    raise TaskRuntimeError(f"Task archive cleanup failed: {finding_codes}")
                return ArchiveResult(
                    task=task,
                    archived_path=archived_path.relative_to(task_paths.root).as_posix(),
                )
        raise TaskRuntimeError("Task exists in both active and archived locations")
    if calculate_sha256(task_paths.active_path) != expected_sha256:
        raise TaskRuntimeError(
            "Active task content changed after it was read; reload before archiving"
        )

    source_content = task_paths.active_path.read_text(encoding="utf-8")
    source_frontmatter = parse_frontmatter(source_content)
    source_status = str(source_frontmatter.get("status"))
    if source_status == "archived":
        validate_task_document(source_content, task, archived=True)
        if source_frontmatter["archived"] != archive_date:
            raise TaskRuntimeError("Pending archived Task date does not match the requested date")
        archived_content = source_content
    else:
        validate_task_document(source_content, task)
        if source_status not in ARCHIVABLE_STATUSES:
            raise TaskRuntimeError("Task must be completed or cancelled before archive")
        archived_content = render_archived_task_content(
            source_content,
            archive_date,
            source_sha256=expected_sha256,
        )
        validate_task_document(archived_content, task, archived=True)
        atomic_write_text(task_paths.active_path, archived_content)

    expected_archived_sha256 = hashlib.sha256(archived_content.encode("utf-8")).hexdigest()
    if calculate_sha256(task_paths.active_path) != expected_archived_sha256:
        raise TaskRuntimeError("Task changed while preparing its archived representation")
    quarantine_path = move_active_task_to_quarantine(task_paths)
    if quarantine_path is None:
        raise TaskRuntimeError("Active Task disappeared while preparing its archive")
    quarantined_bytes, quarantine_identity = read_file_snapshot(quarantine_path)
    quarantined_sha256 = hashlib.sha256(quarantined_bytes).hexdigest()
    if quarantined_sha256 != expected_archived_sha256:
        restore_quarantined_active_task(task_paths, quarantine_path)
        raise TaskRuntimeError("Task changed while moving its archived representation")
    try:
        publish_archive_without_overwrite(quarantine_path, archived_path)
    except OSError as error:
        try:
            restore_quarantined_active_task(task_paths, quarantine_path)
        except TaskRuntimeError as restore_error:
            raise restore_error from error
        if isinstance(error, FileExistsError):
            raise TaskRuntimeError(
                "Archived task target appeared during publication; existing evidence was preserved"
            ) from error
        raise TaskRuntimeError("Archived Task publication failed; active evidence was restored") from error

    published_archive_provenance = read_archive_provenance(task_paths, archived_path)
    published_archive_is_valid = (
        archived_files_for_task(task_paths) == [archived_path]
        and published_archive_provenance.archive_sha256 == expected_archived_sha256
    )
    quarantine_was_removed = published_archive_is_valid and unlink_file_if_snapshot_is_current(
        quarantine_path,
        quarantine_identity,
        quarantined_sha256,
    )
    if not quarantine_was_removed:
        raise TaskRuntimeError(
            "Task changed during archive publication; quarantined evidence was preserved at "
            f"{quarantine_path.relative_to(task_paths.root).as_posix()}"
        )

    findings = cleanup_task(root, task)
    if findings:
        finding_codes = ", ".join(finding.code for finding in findings)
        raise TaskRuntimeError(f"Task archive cleanup failed: {finding_codes}")
    return ArchiveResult(
        task=task,
        archived_path=archived_path.relative_to(task_paths.root).as_posix(),
    )


def cleanup_task(root: Path, task: str) -> list[RuntimeFinding]:
    task_paths = build_task_paths(root, task)
    findings: list[RuntimeFinding] = []
    unexpected_active_entries = unexpected_active_workspace_entries(task_paths)
    if unexpected_active_entries:
        for unexpected_entry in unexpected_active_entries:
            findings.append(
                RuntimeFinding(
                    code="unexpected-active-entry",
                    message=(
                        "Active Task workspace may contain only regular lowercase .md files"
                    ),
                    path=unexpected_entry.relative_to(task_paths.root).as_posix(),
                )
            )
        return findings
    invalid_archive_entries = noncanonical_archive_entries(task_paths)
    if invalid_archive_entries:
        for invalid_path, invalid_error in invalid_archive_entries:
            findings.append(
                RuntimeFinding(
                    code="invalid-archived-task",
                    message=str(invalid_error),
                    path=invalid_path.relative_to(task_paths.root).as_posix(),
                )
            )
        if task_paths.active_path.exists():
            findings.append(
                RuntimeFinding(
                    code="duplicate-task-state",
                    message=(
                        "Active Task was preserved because archived contains "
                        "noncanonical evidence"
                    ),
                    path=task_paths.active_path.relative_to(task_paths.root).as_posix(),
                )
            )
        return findings
    archived_paths = archived_files_for_task(task_paths)
    valid_archived_paths: list[Path] = []
    if not archived_paths:
        findings.append(
            RuntimeFinding(
                code="archived-task-missing",
                message="Task has no archived document",
                path=task_paths.archived_root.relative_to(task_paths.root).as_posix(),
            )
        )
        return findings
    if len(archived_paths) > 1:
        findings.append(
            RuntimeFinding(
                code="multiple-archives",
                message="Task has more than one archived document",
                path=task_paths.archived_root.relative_to(task_paths.root).as_posix(),
            )
        )
    for archived_path in archived_paths:
        try:
            archived_task = parse_archived_task_filename(archived_path)[2]
            build_task_summary(archived_path, task_paths.root, archived_task, archived=True)
            valid_archived_paths.append(archived_path)
        except TaskRuntimeError as error:
            findings.append(
                RuntimeFinding(
                    code="invalid-archived-task",
                    message=str(error),
                    path=archived_path.relative_to(task_paths.root).as_posix(),
                )
            )
    if task_paths.active_path.exists():
        removed_proven_residue = False
        if len(archived_paths) == 1 and valid_archived_paths == archived_paths:
            try:
                removed_proven_residue = remove_active_task_if_proven_residue(
                    task_paths,
                    archived_paths[0],
                )
            except (OSError, TaskRuntimeError, UnicodeDecodeError) as error:
                findings.append(
                    RuntimeFinding(
                        code="cleanup-race-detected",
                        message=str(error),
                        path=task_paths.active_root.relative_to(task_paths.root).as_posix(),
                    )
                )
        if not removed_proven_residue or task_paths.active_path.exists():
            findings.append(
                RuntimeFinding(
                    code="duplicate-task-state",
                    message="Task exists in both active and archived locations",
                    path=task_paths.active_path.relative_to(task_paths.root).as_posix(),
                )
            )
    return findings


def task_summary(path: Path, root: Path, archived: bool) -> TaskSummary:
    ensure_path_has_no_symlink(root, path)
    task = parse_archived_task_filename(path)[2] if archived else path.stem
    return build_task_summary(path, root, task, archived)


def build_task_summary(
    path: Path,
    root: Path,
    task: str,
    archived: bool,
    validate_archive_filename: bool = True,
) -> TaskSummary:
    content = path.read_text(encoding="utf-8")
    frontmatter = validate_task_document(content, task, archived=archived)
    if archived and validate_archive_filename:
        filename_archive_date, _, filename_task = parse_archived_task_filename(path)
        if filename_task != task or frontmatter["archived"] != filename_archive_date:
            raise TaskRuntimeError("Archived Task date does not match its filename")
    return TaskSummary(
        task=task,
        status=str(frontmatter["status"]),
        workflow=str(frontmatter["workflow"]),
        owner_skill=str(frontmatter["owner_skill"]),
        path=path.relative_to(root).as_posix(),
    )


def scan_tasks(root: Path) -> ScanResult:
    resolved_root = resolve_root(root)
    task_root = resolved_root / "codestable" / "tasks"
    active_root = task_root / "active"
    archived_root = task_root / "archived"
    active_tasks: list[TaskSummary] = []
    archived_tasks: list[TaskSummary] = []
    findings: list[RuntimeFinding] = []
    active_slugs: set[str] = set()
    archived_slugs: set[str] = set()
    archive_counts: dict[str, int] = {}
    daily_archive_paths: dict[tuple[str, int], list[Path]] = {}
    daily_archive_sequences: dict[str, list[int]] = {}

    required_directories = (
        (task_root, "task-root"),
        (active_root, "active-root"),
        (archived_root, "archived-root"),
    )
    workspace_is_valid = True
    for required_directory, directory_name in required_directories:
        relative_path = required_directory.relative_to(resolved_root).as_posix()
        try:
            ensure_path_has_no_symlink(resolved_root, required_directory)
        except TaskRuntimeError as error:
            findings.append(
                RuntimeFinding(
                    code="unsafe-task-workspace",
                    message=str(error),
                    path=relative_path,
                )
            )
            workspace_is_valid = False
            continue
        if not required_directory.exists():
            findings.append(
                RuntimeFinding(
                    code="missing-task-workspace",
                    message=f"Task workspace {directory_name} is missing",
                    path=relative_path,
                )
            )
            workspace_is_valid = False
        elif not required_directory.is_dir():
            findings.append(
                RuntimeFinding(
                    code="invalid-task-workspace",
                    message=f"Task workspace {directory_name} is not a directory",
                    path=relative_path,
                )
            )
            workspace_is_valid = False
    if not workspace_is_valid:
        return ScanResult(active=(), archived=(), findings=tuple(findings))

    allowed_task_root_entries = {"active", "archived"}
    for task_root_entry in sorted(task_root.iterdir()):
        if task_root_entry.name not in allowed_task_root_entries:
            findings.append(
                RuntimeFinding(
                    code="unexpected-task-workspace-entry",
                    message="Task workspace may contain only active and archived directories",
                    path=task_root_entry.relative_to(resolved_root).as_posix(),
                )
            )

    valid_active_paths: list[Path] = []
    for active_entry in sorted(active_root.iterdir()):
        if active_entry.is_symlink() or not active_entry.is_file() or active_entry.suffix != ".md":
            findings.append(
                RuntimeFinding(
                    code="unexpected-active-entry",
                    message="Active Task workspace may contain only regular lowercase .md files",
                    path=active_entry.relative_to(resolved_root).as_posix(),
                )
            )
            continue
        valid_active_paths.append(active_entry)

    for active_path in valid_active_paths:
        active_slug = active_path.stem
        active_slugs.add(active_slug)
        try:
            active_tasks.append(task_summary(active_path, resolved_root, archived=False))
        except TaskRuntimeError as active_error:
            try:
                archived_summary = build_task_summary(
                    active_path,
                    resolved_root,
                    active_slug,
                    archived=True,
                    validate_archive_filename=False,
                )
                active_tasks.append(archived_summary)
                findings.append(
                    RuntimeFinding(
                        code="archive-pending-move",
                        message="Task has archived content in the active directory",
                        path=active_path.relative_to(resolved_root).as_posix(),
                    )
                )
            except TaskRuntimeError:
                findings.append(
                    RuntimeFinding(
                        code="invalid-task-document",
                        message=str(active_error),
                        path=active_path.relative_to(resolved_root).as_posix(),
                    )
                )

    valid_archived_paths: list[Path] = []
    for archived_entry in sorted(archived_root.iterdir()):
        if (
            archived_entry.is_symlink()
            or not archived_entry.is_file()
            or archived_entry.suffix != ".md"
        ):
            findings.append(
                RuntimeFinding(
                    code="unexpected-archived-entry",
                    message="Archived Task workspace may contain only regular lowercase .md files",
                    path=archived_entry.relative_to(resolved_root).as_posix(),
                )
            )
            continue
        valid_archived_paths.append(archived_entry)

    for archived_path in valid_archived_paths:
        try:
            archive_date, daily_sequence, archived_slug = parse_archived_task_filename(
                archived_path
            )
            archived_tasks.append(task_summary(archived_path, resolved_root, archived=True))
        except TaskRuntimeError as error:
            findings.append(
                RuntimeFinding(
                    code="invalid-archived-task",
                    message=str(error),
                    path=archived_path.relative_to(resolved_root).as_posix(),
                )
            )
            continue
        archived_slugs.add(archived_slug)
        archive_counts[archived_slug] = archive_counts.get(archived_slug, 0) + 1
        daily_archive_paths.setdefault((archive_date, daily_sequence), []).append(
            archived_path
        )
        daily_archive_sequences.setdefault(archive_date, []).append(daily_sequence)

    for duplicate_slug in sorted(active_slugs.intersection(archived_slugs)):
        findings.append(
            RuntimeFinding(
                code="duplicate-task-state",
                message="Task exists in both active and archived locations",
                path=f"codestable/tasks/active/{duplicate_slug}.md",
            )
        )
    for archived_slug, archive_count in sorted(archive_counts.items()):
        if archive_count > 1:
            findings.append(
                RuntimeFinding(
                    code="multiple-archives",
                    message="Task has more than one archived document",
                    path=f"codestable/tasks/archived/{archived_slug}",
                )
            )
    for (archive_date, daily_sequence), sequence_paths in sorted(daily_archive_paths.items()):
        if len(sequence_paths) > 1:
            findings.append(
                RuntimeFinding(
                    code="duplicate-daily-archive-sequence",
                    message=(
                        f"Archive date {archive_date} uses daily sequence "
                        f"{daily_sequence:03d} more than once"
                    ),
                    path=sequence_paths[0].parent.relative_to(resolved_root).as_posix(),
                )
            )
    for archive_date, daily_sequences in sorted(daily_archive_sequences.items()):
        sorted_sequences = sorted(set(daily_sequences))
        expected_sequences = list(range(1, len(sorted_sequences) + 1))
        if sorted_sequences != expected_sequences:
            findings.append(
                RuntimeFinding(
                    code="noncontiguous-daily-archive-sequence",
                    message=(
                        f"Archive date {archive_date} must use contiguous daily sequences "
                        "starting at 001"
                    ),
                    path=archived_root.relative_to(resolved_root).as_posix(),
                )
            )
    return ScanResult(
        active=tuple(active_tasks),
        archived=tuple(archived_tasks),
        findings=tuple(findings),
    )


def print_json(value: object) -> None:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage CodeStable Task lifecycle documents.")
    parser.add_argument("--root", default=".", help="Repository root.")
    command_parsers = parser.add_subparsers(dest="command", required=True)

    command_parsers.add_parser("scan", help="List active and archived Tasks.")

    create_parser = command_parsers.add_parser("create", help="Create an active Task.")
    create_parser.add_argument("--task", required=True)
    create_parser.add_argument("--goal", required=True)
    create_parser.add_argument("--workflow", required=True)
    create_parser.add_argument("--owner", default="cs")
    create_parser.add_argument("--step", action="append", default=[])
    create_parser.add_argument("--related-doc", action="append", default=[])
    create_parser.add_argument("--date")

    write_parser = command_parsers.add_parser("write-active", help="CAS-update an active Task.")
    write_parser.add_argument("--task", required=True)
    write_parser.add_argument("--content-file", required=True)
    write_parser.add_argument("--expected-sha256", required=True)

    update_parser = command_parsers.add_parser("update", help="Apply guarded Task replacements.")
    update_parser.add_argument("--task", required=True)
    update_parser.add_argument("--expected-sha256", required=True)
    update_parser.add_argument(
        "--replacements-json",
        default="{}",
        help="Optional JSON object of guarded text replacements.",
    )
    update_parser.add_argument("--record", required=True)
    update_parser.add_argument("--date")

    status_parser = command_parsers.add_parser("set-status", help="Block, resume, or cancel a Task.")
    status_parser.add_argument("--task", required=True)
    status_parser.add_argument("--status", required=True, choices=["active", "blocked", "cancelled"])
    status_parser.add_argument("--expected-sha256", required=True)
    status_parser.add_argument("--reason", required=True)
    status_parser.add_argument("--date")

    complete_parser = command_parsers.add_parser("complete", help="Mark an active Task completed.")
    complete_parser.add_argument("--task", required=True)
    complete_parser.add_argument("--expected-sha256", required=True)
    complete_parser.add_argument("--date")

    archive_parser = command_parsers.add_parser("archive", help="Atomically move a Task to archived.")
    archive_parser.add_argument("--task", required=True)
    archive_parser.add_argument("--date", required=True)
    archive_parser.add_argument("--expected-sha256", required=True)

    cleanup_parser = command_parsers.add_parser("cleanup", help="Validate archive closure.")
    cleanup_parser.add_argument("--task", required=True)

    command_parsers.add_parser(
        "migrate-archive-filenames",
        help="Migrate unambiguous legacy archive filenames to daily sequences.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    arguments = parser.parse_args()
    root = Path(arguments.root)
    try:
        if arguments.command == "scan":
            scan_result = scan_tasks(root)
            print_json(scan_result)
            return 1 if scan_result.findings else 0
        elif arguments.command == "create":
            created_path = create_task(
                root=root,
                task=arguments.task,
                goal=arguments.goal,
                workflow=arguments.workflow,
                owner=arguments.owner,
                steps=arguments.step,
                related_docs=arguments.related_doc,
                current_date=arguments.date,
            )
            print_json(
                {
                    "status": "created",
                    "path": created_path.relative_to(root.resolve()).as_posix(),
                    "plan_committed": True,
                    "execution_mode": "unattended",
                    "ordinary_questions_allowed": False,
                    "necessary_clarification_or_authorization_allowed": True,
                    "next_action": "continue-first-incomplete-step",
                }
            )
        elif arguments.command == "write-active":
            updated_path = write_active_task(
                root=root,
                task=arguments.task,
                content_path=Path(arguments.content_file),
                expected_sha256=arguments.expected_sha256,
            )
            print_json(
                {
                    "status": "updated",
                    "path": updated_path.relative_to(root.resolve()).as_posix(),
                }
            )
        elif arguments.command == "update":
            replacements = json.loads(arguments.replacements_json)
            if not isinstance(replacements, dict) or not all(
                isinstance(old_text, str) and isinstance(new_text, str)
                for old_text, new_text in replacements.items()
            ):
                raise TaskRuntimeError("Task replacements must be a JSON object of string pairs")
            updated_path = update_task(
                root=root,
                task=arguments.task,
                expected_sha256=arguments.expected_sha256,
                replacements=replacements,
                progress_record=arguments.record,
                current_date=arguments.date,
            )
            print_json(
                {
                    "status": "updated",
                    "path": updated_path.relative_to(root.resolve()).as_posix(),
                }
            )
        elif arguments.command == "set-status":
            updated_path = set_task_status(
                root=root,
                task=arguments.task,
                target_status=arguments.status,
                expected_sha256=arguments.expected_sha256,
                reason=arguments.reason,
                current_date=arguments.date,
            )
            print_json(
                {
                    "status": arguments.status,
                    "path": updated_path.relative_to(root.resolve()).as_posix(),
                }
            )
        elif arguments.command == "complete":
            completed_path = complete_task(
                root=root,
                task=arguments.task,
                expected_sha256=arguments.expected_sha256,
                current_date=arguments.date,
            )
            print_json(
                {
                    "status": "completed",
                    "path": completed_path.relative_to(root.resolve()).as_posix(),
                }
            )
        elif arguments.command == "archive":
            print_json(
                archive_task(
                    root=root,
                    task=arguments.task,
                    archive_date=arguments.date,
                    expected_sha256=arguments.expected_sha256,
                )
            )
        elif arguments.command == "cleanup":
            findings = cleanup_task(root, arguments.task)
            print_json({"ok": not findings, "findings": [asdict(finding) for finding in findings]})
            return 1 if findings else 0
        elif arguments.command == "migrate-archive-filenames":
            migrated_paths = migrate_legacy_archive_filenames(root)
            print_json({"status": "migrated", "paths": migrated_paths})
    except (TaskRuntimeError, OSError, json.JSONDecodeError) as error:
        print_json({"error": str(error)})
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
