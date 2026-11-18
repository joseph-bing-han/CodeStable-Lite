---
doc_type: task-list
task: {task}
goal: {goal}
status: active
workflow: {workflow}
owner_skill: cs
created: YYYY-MM-DD
updated: YYYY-MM-DD
archived: null
related_docs: []
---

# {goal}

## 1. 任务目标

{goal}

## 2. 当前状态

active

## 3. Agent 原生 Tasks 同步区

- [ ] {step}

## 4. CodeStable 文档索引

{已存在的相关 Issue / Spec 等前置依据；纯只读、初始化或明确禁止业务文档时说明依据与边界。related_docs 同步实际路径。}

## 5. 执行步骤

### 1. {step}

- 状态：pending
- 完成信号：{evidence}

## 6. 中断恢复提示

先核对关联业务依据，再从第一个未完成步骤继续，并以本 Task 正本恢复 Agent 原生 Tasks。计划确定后按 `references/autonomy.md` 自动择优，不再请求路线确认。

Task 已归档时只继续关联文档的最终回写，适用于本次只剩回写的情况。按归档记录中的位置与路径映射恢复，不修改冻结 Task，不为回写另建 Task。同目标有新增工作时使用 runtime 的 `continue` 移回 active 并追加步骤。完成并验证后重新归档。业务正本维护最终引用。

## 7. 完成与归档记录

YYYY-MM-DD：Task 已创建。

{创建时记录前置文档与已确认结论；归档前记录回写内容、目标章节、授权和预期改名映射。归档后实际回写结果进入业务正本，不预填完成。}
