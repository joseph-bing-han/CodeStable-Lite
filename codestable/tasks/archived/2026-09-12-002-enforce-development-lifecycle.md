---
doc_type: task-list
task: enforce-development-lifecycle
goal: 修正 CS 开发顺序为业务文档先行、Task 执行验证、归档后同步关联状态
status: archived
workflow: bug
owner_skill: cs
created: 2026-09-12
updated: 2026-09-12
archived: 2026-09-12
related_docs:
  - codestable/issues/004-o-enforce-development-lifecycle.md
  - codestable/spec/index.md
  - skills/cs/SKILL.md
  - skills/cs/references/task.md
  - skills/cs/references/retention.md
  - tests/test_skill_contracts.py
---

# 修正 CS 开发顺序为业务文档先行、Task 执行验证、归档后同步关联状态

## 1. 任务目标

修正 CS 开发顺序为业务文档先行、Task 执行验证、归档后同步关联状态

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 统一前置文档与归档后回写契约
- [x] 同步相关姿态、模板、脚本和项目说明
- [x] 补充顺序回归检查并验证修复
- [x] 独立复核并准备关联文档收尾

## 4. CodeStable 文档索引

- `codestable/issues/004-o-enforce-development-lifecycle.md`
- `codestable/spec/index.md`
- `skills/cs/SKILL.md`
- `skills/cs/references/task.md`
- `skills/cs/references/retention.md`
- `tests/test_skill_contracts.py`

## 5. 执行步骤

### 1. 统一前置文档与归档后回写契约

- 状态：done

### 2. 同步相关姿态、模板、脚本和项目说明

- 状态：done

### 3. 补充顺序回归检查并验证修复

- 状态：done

### 4. 独立复核并准备关联文档收尾

- 状态：done

## 6. 中断恢复提示

先核对关联业务依据，再从第一个未完成步骤继续，并以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。Task 已归档时只继续关联文档的最终回写，按归档记录中的位置与路径映射恢复；不修改冻结 Task，不为回写另建 Task。

## 7. 完成与归档记录

2026-09-12：Task 已创建。

2026-09-12：已先完成有界分析，创建 Issue 004 和当前规格漂移说明，之后才创建本 Task。工作区起始干净；现有 82 项标准库测试通过。保留旧归档原文；父代理唯一写入，独立只读代理核对关联契约。归档后将回写 Issue 004 与 spec/index.md 最终结果，不重建收尾 Task。

2026-09-12：已统一 SKILL、Task、自治与 retention 核心顺序：有界分析及相关业务依据先于 Task；执行验证完成后归档，再回写业务结果与最终状态。明确当前事实与未来目标、无业务文档授权例外、归档后中断恢复及历史路径映射，不修改冻结归档。继续同步各行动入口与模板，随后验证。

2026-09-12：已同步快改、实施、Bug、讨论、设计、规格、探索、愿景、关闭及初始化/知识/工具入口，前置模板、宿主提示和两份 README 均按新顺序调整。核对发现开工协议列表仍把 Task 放在检索前，已消除。用户确认以当前内容继续；HEAD 仍为原提交，未执行任何提交或回退。下一批同步生成式恢复提示并建立顺序回归检查。

2026-09-12：关联入口、模板与中英文 README 已同步，脚本仅增强生成式恢复提示与 archive CLI 后续回写提示，Task schema/归档保护不变。24 项技能契约检查通过；新增 archive CLI/重放测试先失败，准确检出旧响应没有后续回写提示，现已实现修正，开始全套验证。显式 Git porcelain 已正常显示全部未提交修改，没有外部提交或内容丢失。

2026-09-12：当前仓库 runtime 执行的 87 项标准库测试全部通过，新增 archive CLI 首次/重放出口已从失败转为通过；仓库契约检查、git diff --check、IDE lints 和 Task scan 通过。已启动针对当前工作区绝对路径的独立只读复核，明确禁止使用全局旧技能副本。Task 尚未归档；Issue/Spec 最终状态待按既定顺序回写。

2026-09-12：独立只读复核已返回：当前主顺序与恢复无阻塞；指出已授权关闭并提交分支中，提交包含归档后回写却可能被列为归档前步骤的循环依赖。已先在 Issue 004 补明确边界，本批仅修正 Task/Close 规则并增加相关断言，不执行 Git 提交。两种内存倒序反例（业务文档晚于Task、最终回写早于归档）均被顺序测试检出，未改动文件。

2026-09-12：最终独立复核确认顺序及恢复无阻塞，关闭/提交循环已消除并经同一只读审查者复核；最新87项测试、仓库契约检查、diff格式与IDE lints全部通过。归档后回写准备：Issue 004保留open并注明本轮实现完成/关闭就绪，记录87项验证、两种倒序反例、archive CLI初次/重放红绿证据与本Task实际归档路径；spec/index.md替换流程漂移为已验证的当前开发顺序、文档/Task职责和归档后恢复边界。本轮无关闭改名，无路径映射变动。Talk无多轮业务取舍增量；Note内容已直接进入技能与规格，不重复建；Tool无新增流程自动化需求，复用现有runtime及检查脚本。无Epic/Vision变更，不提交/推送/部署、不改全局技能副本或历史归档。归档后只执行以上机械回写与回读，不另建Task。

2026-09-12：Task 已标记 completed，等待归档。

2026-09-12：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：0311cc50f2d0da9c1743e9478612c8ad6aadf7054b329fac5cbe24ef6d8348d5
