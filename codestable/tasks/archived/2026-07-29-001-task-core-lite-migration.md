---
doc_type: task-list
task: task-core-lite-migration
goal: 将 CodeStable 的强制 Task 主线移植到 Lite 单入口工作流
status: archived
workflow: skill-evolution
owner_skill: cs
created: 2026-07-29
updated: 2026-07-29
archived: 2026-07-29
related_docs:
  - skills/cs/SKILL.md
  - skills/cs/references/task.md
  - skills/cs/references/autonomy.md
  - skills/cs/scripts/codestable_task_runtime.py
  - skills/cs/templates/entities/task.md
  - tools/check-skill-repository.py
  - README.md
  - README.en.md
---

# 将 CodeStable 的强制 Task 主线移植到 Lite 单入口工作流

## 1. 任务目标

保持 `cs` 单一 Skill 入口不变，为全部行动姿态加入不可跳过的 Task 创建、批次更新、完成与原子归档，并在计划确定后切换为无人值守执行，自动选择风险和总成本更低的推荐方向，持续到工作与验证全部完成。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 对照来源仓库并建立 Task 与自治契约失败基线
- [x] 实现并接入全部姿态的强制 Task 主线
- [x] 同步 references、templates、scripts、README 与检查器
- [x] 完成首轮测试、压力复测和独立审查
- [x] 将 runtime 收敛为 active / archived 单写者模型
- [x] 运行完整测试、压力复测与独立审查

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| 来源协议 | `/Users/joseph/code/CodeStable/plugins/codestable/skills/cs-task/` | Task 生命周期、schema 与归档状态机来源 |
| 来源 runtime | `/Users/joseph/code/CodeStable/plugins/codestable/skills/cs-onboard/tools/codestable-task-runtime.py` | 陈旧快照保护与归档状态机的参考来源 |
| Lite 入口 | `skills/cs/SKILL.md` | 单一入口与全部行动姿态的共享强制契约 |
| Lite Task 协议 | `skills/cs/references/task.md` | Task 单写者持久化与运行流程的权威说明 |
| Lite 自治协议 | `skills/cs/references/autonomy.md` | 计划确定后的无人值守决策和循环契约 |

## 5. 执行步骤

### 1. 对照来源仓库并建立 Task 与自治契约失败基线

- 状态：done
- 完成信号：仓库契约测试因缺少 Task 资产与强制规则而失败；压力场景能复现无痕快改、只读 review 和计划后重新询问三条绕过路径。

### 2. 实现并接入全部姿态的强制 Task 主线

- 状态：done
- 完成信号：`codestable/tasks/` schema、模板与 runtime 支持创建、CAS 更新、完成、原子移动归档、清理和扫描。

### 3. 同步 references、templates、scripts、README 与检查器

- 状态：done
- 完成信号：澄清以外的每个 `cs` workflow 都先恢复或创建 Task；每个可观察批次先更新 Task；最终答复前 Task 已归档且 active 无同名文件。

### 4. 完成首轮测试、压力复测和独立审查

- 状态：done
- 完成信号：计划落入 Task 后禁止再次 AskQuestion；偏差、测试失败和多方案分叉由 Agent 按可逆性、风险、契约一致性与总成本自动择优并持续执行。

### 5. 将 runtime 收敛为 active / archived 单写者模型

- 状态：done
- 完成信号：只保留 active / archived；陈旧快照保护、终态冻结、独占归档发布、中断恢复和重复状态扫描仍成立。

### 6. 运行完整测试、压力复测与独立审查

- 状态：done
- 完成信号：行为测试、仓库检查、diff 检查、三类压力复测和独立审查通过。


## 6. 中断恢复提示

读取本文件后从第一个非 done 步骤继续。计划已经确定，不再向用户询问实现路线；遇到分叉按 `autonomy.md` 的确定性排序选择推荐方向并回写本 Task。

## 7. 完成与归档记录

2026-07-29：完成来源 HEAD 与 Lite 结构对照，并通过三个只读压力场景确认当前协议允许无痕快改跳过 Task、只读流程不留 Task、计划后在关键分叉再次询问。

2026-07-29：新增标准库单元测试与仓库契约测试，并观察到它们因 Task 资产、全姿态继承标记和无人值守契约缺失而失败，失败基线成立。本文件是 runtime 尚未落地时的引导 Task；runtime 可用后，后续更新、完成和归档全部改走 runtime。

2026-07-29：Task 核心批次完成：新增 canonical reference、模板、标准库 runtime 与初始化目录；runtime 单元测试通过。

2026-07-29：单入口契约批次完成：全部姿态继承 Task 与自治协议，相关 references、初始化脚本、Agent 提示、双语 README、CHANGELOG 和仓库检查器已同步；静态契约测试通过。

2026-07-29：用户确认采用 Lite 单写者简化方案：移除 conflicts、locks、staging、tombstones，只保留 active 与 archived，并在简化后继续完整测试。

2026-07-29：完成 runtime 精简：工作区只创建 active 与 archived；新增非空计划、步骤不可丢失、终态冻结、archive source-hash guard、中断移动恢复和重复状态扫描门禁；15 项对抗性测试通过。

2026-07-29：完成契约同步：SKILL、Task/Onboard references、初始化脚本、双语 README、CHANGELOG、checker 与契约测试均改为 active/archived 两层模型；仓库综合检查与 15 项行为测试通过。

2026-07-29：第二轮压力复测：只读留痕通过；独立审查发现计划双视图错配、重复状态写入、scan/schema、archive 独占发布及多处计划后确认语义缺口。已通过受限迁移统一本 Task checklist 与执行步骤标题，随后补行为门禁和契约。

2026-07-29：按用户约束移除计划中的归档待办：archive 是 complete 后由 runtime 机械执行的生命周期动作，不再出现在 Task checklist 或执行步骤中；schema 同时拒绝新 Task 把 archive/归档列为工作步骤。

2026-07-29：关闭第二轮 review findings 并落实新约束：计划双视图严格同序、Task 正文状态与 schema 一致、重复状态禁止写入、scan 检查缺失/符号链接 workspace、归档独占发布不覆盖证据、恢复提示与自治契约同步；归档不再是 Task 计划项。23 项 runtime 对抗测试、12 项契约测试、仓库检查、语法与 diff 检查通过。

2026-07-29：关闭最新机制缺口并完成第三轮验证：归档步骤过滤兼顾绕过与调查负例，重复状态、祖先 symlink、封闭 schema、固定章节唯一性、双视图进度、scan 非零退出及无人值守 create metadata 均有行为门禁；28 项 runtime 测试、12 项契约测试、仓库检查器、语法、diff 与无 finding scan 通过，三路独立复审已启动。

2026-07-29：处理第三轮独立 review：修复 create 检查后覆盖竞态、固定章节封闭顺序、归档步骤语义绕过与误伤、严格 workspace scan、初始化 canonical index 类型校验、archive 原命令幂等重放，以及 Talk/人工验收/Issue 关闭的计划前边界；32 项 runtime 测试、12 项契约测试、综合 checker、编译、diff 与严格 scan 全部通过。

2026-07-29：最终验证与独立复审完成：33 项 runtime 测试、12 项 Skill 契约测试、仓库综合 checker、Python 编译、diff 检查、严格 Task scan 和 IDE lint 均通过；三路 focused closure 均为 PASS，Blocking 0、Important 0。

2026-07-29：Task 已标记 completed，等待归档。

2026-07-29：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：fb6e7b7857a65ac5b62aeaf99de93e57be08b62d859ace0ce1e363c8bfd7eed4
