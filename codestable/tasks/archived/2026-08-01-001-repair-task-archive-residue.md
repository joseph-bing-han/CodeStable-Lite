---
doc_type: task-list
task: repair-task-archive-residue
goal: Repair safe cleanup of reappearing archived Task sources
status: archived
workflow: bug
owner_skill: cs
created: 2026-08-01
updated: 2026-08-01
archived: 2026-08-01
related_docs:
  - skills/cs/scripts/codestable_task_runtime.py
  - tests/test_task_runtime.py
  - skills/cs/references/task.md
  - README.md
  - README.en.md
  - codestable/issues/001-x-ff-repair-task-archive-residue.md
  - /Users/joseph/code/KKTripsBackend/codestable/tasks
---

# Repair safe cleanup of reappearing archived Task sources

## 1. 任务目标

Repair safe cleanup of reappearing archived Task sources

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] Reproduce and identify stale active residue
- [x] Implement safe archive residue cleanup
- [x] Synchronize Task contracts and public documentation
- [x] Run regression tests and independent review
- [x] Repair the KKTripsBackend duplicate Task and verify closure

## 4. CodeStable 文档索引

- `skills/cs/scripts/codestable_task_runtime.py`
- `tests/test_task_runtime.py`
- `skills/cs/references/task.md`
- `README.md`
- `README.en.md`
- `codestable/issues/001-x-ff-repair-task-archive-residue.md`
- `/Users/joseph/code/KKTripsBackend/codestable/tasks`

## 5. 执行步骤

### 1. Reproduce and identify stale active residue

- 状态：done

### 2. Implement safe archive residue cleanup

- 状态：done

### 3. Synchronize Task contracts and public documentation

- 状态：done

### 4. Run regression tests and independent review

- 状态：done

### 5. Repair the KKTripsBackend duplicate Task and verify closure

- 状态：done

## 6. 中断恢复提示

从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。

## 7. 完成与归档记录

2026-08-01：Task 已创建。

2026-08-01：Reproduced the duplicate in KKTripsBackend. The archived record was created at 00:01:37, while the active path was recreated 79 seconds later at 00:02:56. Its SHA-256 exactly matches the archived source snapshot 36b03c95b204d892d81744e2a39bcf1edab66fede76e6691c7389d4ca8761b36, proving archive removed the original source and a stale writer restored the completed snapshot afterward. Current cleanup only reports every active/archive duplicate and cannot safely heal this cryptographically identical residue.

2026-08-01：Added provenance-aware cleanup and archive replay recovery. A lone valid archive may remove a recreated active path only when its bytes match either the archive itself or the source SHA-256 recorded by that archive. Divergent active evidence remains fail-closed. Three focused regression tests now pass.

2026-08-01：Synchronized the source Task reference, Chinese and English READMEs, and the installed global cs runtime/reference. The documented contract now distinguishes byte-identical archived-source residue, which cleanup may remove, from divergent active evidence, which remains fail-closed. The Task template and initializer require no changes because their schema and directory contract are unchanged.

2026-08-01：First independent review found a TOCTOU risk between path-based provenance checking and unlink, plus archive identity recheck and fail-closed test gaps. Reworked cleanup to atomically move active into a private quarantine before validation, revalidate the archive inode/content snapshot before deleting only the quarantined object, restore divergent evidence without overwrite, and preserve concurrent new active content. Added coverage for invalid/multiple archives, archived-content residues, concurrent active replacement, concurrent archive invalidation, and archive replay failure paths.

2026-08-01：Second independent review found remaining windows around quarantine replacement, a second archive appearing during cleanup, normal first-archive publication, placeholder cleanup, and filename-date provenance binding. Added descriptor/stat/hash guarded unlink, unique-archive re-enumeration, self-contained filename/date validation, placeholder cleanup on every failed move, and routed initial archive publication through quarantine so a concurrently recreated active path is never unlinked. Added deterministic race-injection tests for each path; 60 tests now pass.

2026-08-01：Final verification passed: 62 tests, Skill repository contract check, py_compile for source/tests/installed runtime, git diff --check, and Task scan. Independent final review returned PASS under the documented single-writer boundary. KKTripsBackend was not modified because its duplicate files disappeared during the run and the user selected runtime-only continuation; no unsafe restoration or deletion was performed. Closed fast-forward record: codestable/issues/001-x-ff-repair-task-archive-residue.md.

2026-08-01：Task 已标记 completed，等待归档。

2026-08-01：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：1a5d4931f528c3a33d19d942ce0c8fbfcd52fbf3bbe4fe0e7312bba27478843f
