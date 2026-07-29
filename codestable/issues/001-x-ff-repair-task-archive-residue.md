---
kind: issue
title: "修复 Task 归档残留"
type: ff
status: closed
created: 2026-08-01
epic: ""
---

# 修复 Task 归档残留

## 做了什么

修复归档完成后旧写入者重新创建 active Task，导致 active 与 archived 同时存在、任务无法闭环的问题。归档和 cleanup 现在只清理能够由唯一有效 archive 及源快照证明的同源残留，分叉证据继续 fail closed。

## 改了哪些

- `skills/cs/scripts/codestable_task_runtime.py` — 增加 quarantine、文件身份与 hash 复核、唯一 archive 校验、异常恢复和可重放归档逻辑。
- `tests/test_task_runtime.py` — 覆盖同源/分叉残留、无效/多 archive、并发替换、发布冲突和 quarantine 中断恢复。
- `skills/cs/references/task.md`、`README.md`、`README.en.md` — 同步归档残留清理、恢复和单写者边界。

## 怎么验证的

`python3 -m unittest discover -s tests -p 'test_*.py'`（62 项）、`python3 tools/check-skill-repository.py`、Python `py_compile`、`git diff --check` 和 Task runtime `scan` 均通过；独立终审为 PASS。

## 对 codestable/ 的影响

- 未改变 Project Spec 的业务真相；已同步 Task runtime 参考契约和 README，并保留本次修复记录。
