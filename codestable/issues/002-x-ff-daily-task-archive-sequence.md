---
kind: issue
title: "增加 Task 每日归档顺序号"
type: ff
status: closed
created: 2026-08-08
epic: ""
---

# 增加 Task 每日归档顺序号

## 做了什么

将 Task 归档文件名改为 `YYYY-MM-DD-NNN-{task}.md`。三位序号按归档日期在所有 Task 之间共享，每天从 `001` 开始，并按实际归档顺序递增。

## 改了哪些

- `skills/cs/scripts/codestable_task_runtime.py`：增加归档文件名解析、每日序号分配、扫描与恢复校验。
- `tests/test_task_runtime.py`：覆盖同日递增、跨日重置及既有归档恢复场景。
- `skills/cs/SKILL.md`、`skills/cs/references/task.md`、Task 模板及中英文 README：同步新命名契约。
- `codestable/tasks/archived/`：将仓库内既有归档迁移到新命名格式。

## 怎么验证的

Task runtime 的 60 项单元测试与完整套件的 72 项测试全部通过；仓库契约检查、Python 编译、差异格式检查与 Task scan 也通过。

## 对 codestable/ 的影响

- 已同步 Task 核心结构、reference、template、runtime、README 与全局安装的 `cs` 契约，不存在同一归档命名的两套表述。
