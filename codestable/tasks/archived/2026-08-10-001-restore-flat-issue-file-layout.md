---
doc_type: task-list
task: restore-flat-issue-file-layout
goal: Keep Task archive sequencing isolated from Issue file layout
status: archived
workflow: bug
owner_skill: cs
created: 2026-08-10
updated: 2026-08-10
archived: 2026-08-10
related_docs:
  - skills/cs/SKILL.md
  - skills/cs/references
  - skills/cs/templates
  - skills/cs/scripts
  - README.md
  - README.en.md
  - codestable/issues/003-x-ff-restore-flat-issue-layout.md
---

# Keep Task archive sequencing isolated from Issue file layout

## 1. 任务目标

Keep Task archive sequencing isolated from Issue file layout

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] Trace the Issue layout regression to its contract source
- [x] Correct affected CodeStable documentation, templates, scripts, and tests
- [x] Run regression verification and independent review
- [x] Record the fast-fix artifact and close the work

## 4. CodeStable 文档索引

- `skills/cs/SKILL.md`
- `skills/cs/references`
- `skills/cs/templates`
- `skills/cs/scripts`
- `README.md`
- `README.en.md`
- `codestable/issues/003-x-ff-restore-flat-issue-layout.md`

## 5. 执行步骤

### 1. Trace the Issue layout regression to its contract source

- 状态：done

### 2. Correct affected CodeStable documentation, templates, scripts, and tests

- 状态：done

### 3. Run regression verification and independent review

- 状态：done

### 4. Record the fast-fix artifact and close the work

- 状态：done

## 6. 中断恢复提示

从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。

## 7. 完成与归档记录

2026-08-10：Task 已创建。

2026-08-10：Root cause traced: Task daily sequencing remained scoped to tasks/archived, while legacy project-local fix-note rules and historical dated Issue directories were copied as precedent. The Skill needs an explicit namespace boundary forbidding dated/task directories and supplemental fix-note/report artifacts for ordinary Issues and ff records.

2026-08-10：Synchronized the namespace-isolation contract across SKILL.md, Task/Fast/Complain references, Task/Issue/ff templates, agent metadata, bilingual READMEs, changelog, repository checker, and contract tests. Task runtime remains unchanged and is now asserted not to touch codestable/issues.

2026-08-10：Verification batch passed after Explore-specific synchronization: 13 Skill contract tests, 60 Task runtime tests, repository contract check, py_compile, git diff --check, and IDE lint diagnostics all passed. Independent review is still running.

2026-08-10：Independent reviewer returned PASS with no blocking, major, or minor findings. It confirmed the Issue/Task isolation contract is synchronized and Task runtime behavior was not expanded.

2026-08-10：Created the canonical flat fast-fix record at codestable/issues/003-x-ff-restore-flat-issue-layout.md. Existing malformed KCPortal directories were intentionally left unchanged; its stale AGENTS.md fix-note rule is recorded as an external project-level conflict.

2026-08-10：Task 已标记 completed，等待归档。

2026-08-10：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：d5be05af6302792bebff88f6c980640f6a9a85acdfea27ef8fed4b10165c4394
