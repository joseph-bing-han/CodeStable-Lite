---
doc_type: task-list
task: harden-issue-layout-regression-tests
goal: Resolve independent review findings for Issue layout isolation
status: archived
workflow: bug
owner_skill: cs
created: 2026-08-10
updated: 2026-08-10
archived: 2026-08-10
related_docs:
  - tests/test_skill_contracts.py
  - tools/check-skill-repository.py
  - skills/cs/templates/entities/ff-issue.md
  - skills/cs/templates/entities/task.md
  - codestable/issues/003-x-ff-restore-flat-issue-layout.md
---

# Resolve independent review findings for Issue layout isolation

## 1. 任务目标

Resolve independent review findings for Issue layout isolation

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] Replace brittle marker checks with behavioral isolation tests
- [x] Complete ff template policy and remove ineffective Task template policy
- [x] Run regression verification and independent review
- [x] Update the existing fast-fix record and close the work

## 4. CodeStable 文档索引

- `tests/test_skill_contracts.py`
- `tools/check-skill-repository.py`
- `skills/cs/templates/entities/ff-issue.md`
- `skills/cs/templates/entities/task.md`
- `codestable/issues/003-x-ff-restore-flat-issue-layout.md`

## 5. 执行步骤

### 1. Replace brittle marker checks with behavioral isolation tests

- 状态：done

### 2. Complete ff template policy and remove ineffective Task template policy

- 状态：done

### 3. Run regression verification and independent review

- 状态：done

### 4. Update the existing fast-fix record and close the work

- 状态：done

## 6. 中断恢复提示

从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。

## 7. 完成与归档记录

2026-08-10：Task 已创建。

2026-08-10：Replaced lexical runtime/initializer checks and duplicated checker markers with temporary-workspace behavior tests that preserve ordinary Issue, ff, and Explore sentinel trees byte-for-byte across initialization and the full Task lifecycle. Completed the ff template prohibition for fix-note/report/analysis and removed the ineffective global policy paragraph from the Task instance template.

2026-08-10：Final verification passed: 62 Task runtime tests, 13 Skill contract tests, repository check, py_compile, and git diff --check. Independent final review returned PASS with all prior findings closed and no new blocking, major, or minor findings.

2026-08-10：Updated codestable/issues/003-x-ff-restore-flat-issue-layout.md with the behavior-test design, complete duplicate-artifact policy, 62-test result, and final PASS review. Final repository check, Task scan, and diff check remain clean.

2026-08-10：Task 已标记 completed，等待归档。

2026-08-10：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：2600c5fd69299f6c5119484a0d720744c963df052b4f1e23274e29b8cc09376d
