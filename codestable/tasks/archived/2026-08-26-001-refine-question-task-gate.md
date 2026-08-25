---
doc_type: task-list
task: refine-question-task-gate
goal: 重构 cs 的 Task 适用边界，让简单 Question 不创建 Task，无法区分时在计划前通过 AskQuestion 确认
status: archived
workflow: skill-evolution
owner_skill: cs
created: 2026-08-26
updated: 2026-08-26
archived: 2026-08-26
related_docs:
  - skills/cs/SKILL.md
  - skills/cs/references/task.md
  - skills/cs/references/autonomy.md
  - skills/cs/agents/openai.yaml
  - skills/cs/templates/entities/task.md
  - README.md
  - README.en.md
  - tests/test_skill_contracts.py
  - tools/check-skill-repository.py
---

# 重构 cs 的 Task 适用边界，让简单 Question 不创建 Task，无法区分时在计划前通过 AskQuestion 确认

## 1. 任务目标

重构 cs 的 Task 适用边界，让简单 Question 不创建 Task，无法区分时在计划前通过 AskQuestion 确认

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 定义 Question 与 Issue 的判定边界和歧义确认规则
- [x] 同步 SKILL、Task reference、自治规则、姿态 references、Agent prompt、模板与公共文档
- [x] 更新契约测试和仓库检查，并完成全量验证

## 4. CodeStable 文档索引

- `skills/cs/SKILL.md`
- `skills/cs/references/task.md`
- `skills/cs/references/autonomy.md`
- `skills/cs/agents/openai.yaml`
- `skills/cs/templates/entities/task.md`
- `README.md`
- `README.en.md`
- `tests/test_skill_contracts.py`
- `tools/check-skill-repository.py`

## 5. 执行步骤

### 1. 定义 Question 与 Issue 的判定边界和歧义确认规则

- 状态：done

### 2. 同步 SKILL、Task reference、自治规则、姿态 references、Agent prompt、模板与公共文档

- 状态：done

### 3. 更新契约测试和仓库检查，并完成全量验证

- 状态：done

## 6. 中断恢复提示

从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。

## 7. 完成与归档记录

2026-08-26：Task 已创建。

2026-08-26：已完成 Question 与 Issue 的判定边界、简单现状询问例外以及歧义时 AskQuestion 前置确认规则。

2026-08-26：已同步 SKILL、Task 主线、自治规则、全部姿态 references、Agent prompt、Task 模板、双语 README、CHANGELOG 与历史公开表述；Question 不创建 Task 的新契约已统一接入。

2026-08-26：完成验证：15 项 Skill 契约测试、62 项 Task runtime 测试、仓库综合检查、Python 语法编译和 IDE lint 均通过；Question / Issue 新契约已覆盖入口、references、README、Agent prompt、测试与检查器。

2026-08-26：Task 已标记 completed，等待归档。

2026-08-26：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：77b0fc679b1ed87a7599332b768dfcf79912b5384dfb736744bf6031f855c156
