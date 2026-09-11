---
doc_type: task-list
task: adapt-cs-lite-gpt6
goal: 依据核验后的 GPT-6 官方能力优化 CS Lite 指令与运行契约，并完成同步和验证
status: archived
workflow: skill-evolution
owner_skill: cs
created: 2026-09-11
updated: 2026-09-12
archived: 2026-09-12
related_docs:
  - skills/cs/SKILL.md
  - skills/cs/references/autonomy.md
  - skills/cs/references/task.md
  - README.md
  - tests/test_skill_contracts.py
---

# 依据核验后的 GPT-6 官方能力优化 CS Lite 指令与运行契约，并完成同步和验证

## 1. 任务目标

依据核验后的 GPT-6 官方能力优化 CS Lite 指令与运行契约，并完成同步和验证

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 核验 GPT-6 资料与现有行为基线
- [x] 优化核心行动规则和运行时适配
- [x] 同步引用模板与项目说明
- [x] 完成针对性验证与独立审查

## 4. CodeStable 文档索引

- `skills/cs/SKILL.md`
- `skills/cs/references/autonomy.md`
- `skills/cs/references/task.md`
- `README.md`
- `tests/test_skill_contracts.py`

## 5. 执行步骤

### 1. 核验 GPT-6 资料与现有行为基线

- 状态：done

### 2. 优化核心行动规则和运行时适配

- 状态：done

### 3. 同步引用模板与项目说明

- 状态：done

### 4. 完成针对性验证与独立审查

- 状态：done

## 6. 中断恢复提示

从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。

## 7. 完成与归档记录

2026-09-11：Task 已创建。

2026-09-11：已读取用户指定帖子并核验官方 GPT-6 HTML 指南、模型页、async tools、steering 和 monitoring 文档。官方 latest-model.md 仍返回 GPT-5.6，未用其推导 GPT-6 能力。工作区起始干净；基线 78 项单测通过；仓库检查预存 CHANGELOG 缺失 0.6.1 章节失败。原生 Tasks 工具未暴露，使用本文件正本。独立仓库分析与行为基线进行中。

2026-09-11：用户两次要求继续后恢复同一 Task，scan 无冲突。已确定保留实体模型、Task schema、单写者、SHA-256 与归档保护；调整必要澄清/授权、宿主能力、中途变更、聚焦验证和重复规则。implement_adaptation 执行规则与 CLI 元数据及测试同步；old_skill_decisions 对固定 HEAD 做独立旧行为模拟；adaptation_plan_check 只读复核方案；source_map 已完成初步定位，正补充引用位置。前轮子代理随中断结束，不视为已交付结果。

2026-09-11：独立旧版行为模拟已完成（固定 HEAD138ba42，非真实 API 测试）：简单解释、小范围 bug 无原生工具、文案聚焦验证路径原本可行；确认 /cs 字样归类规则矛盾、计划后必要新授权禁问、CSV->JSON 替换承诺步骤缺合法闭环。独立计划复核确认方案可实施，补充 blocked取消状态中转、新旧Task关联及创建间隙恢复、pending映射未完成步骤且不夸大runtime能力。均已交唯一实现代理执行。

2026-09-11：本轮恢复：工作区只有本 Task 未跟踪文件，先前实现未落盘；scan 无冲突，重新运行 78 项单测通过，仓库检查仍仅缺 CHANGELOG 0.6.1 章节。当前宿主已暴露原生 Todo 与只读子代理，已从正本恢复任务镜像。帖子经替代网页抓取读取成功；Context7 索引仍主要为 GPT-5.6，不作为 GPT-6 证据。继续由父代理唯一写入，独立只读代理核对契约同步范围。

2026-09-11：用户补充范围已纳入步骤2至4：修复 Issue/Epic 规格回写与 talks/notes/tools 自动触发；核对执行出口、授权边界、模板和反例验证。本轮 scan 无冲突，工作区仅已有 Task 未跟踪；父代理唯一写入。发现 update 文档允许只追加记录但 CLI 强制 replacements-json，纳入定向修复。

2026-09-12：完成核心规则、运行时适配、引用模板与项目说明同步；仓库契约检查通过，Python 编译和差异格式检查通过，Task scan 无 finding。pytest 未执行成功，当前 Python 环境未安装 pytest；改用标准库测试作为后续验证。

2026-09-12：Task 已标记 completed，等待归档。

2026-09-12：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：ad866d2cf3e17857b9827e93de1678d2be3941d6f44fd5844efe343c82fbec1c
