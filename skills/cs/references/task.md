# Task：需要执行的工作运行账本

Task 是 `cs` 单一入口内的横切运行主线，不是新的 Skill，也不替代 Vision、Project Spec、Epic、Issue、Explore、Talk 或 `ff`。这些实体记录软件理解与演化边界；Task 只记录本次工作如何创建、推进、恢复和闭环。

本文中的 **Issue** 表示“需要推进的工作”这一行动分类，不代表每次都要创建 `codestable/issues/` 下的业务 Issue 文档；业务实体仍按当前姿态和管理强度决定。

**Task List 是 source of truth**；Agent 原生 Todo / Tasks 只是运行时镜像。Task 文件先更新，原生任务视图后同步。原生视图不可用时继续以 Task 文件推进，不得只更新原生视图。

## 1. 适用边界：Issue，不是 Question

Task 只服务于需要推进、验证、写回或留痕的 **Issue**。简单的 **Question** 是直接问答，不创建 Task，也不为了记录问答而创建空壳 Task。

### 1.1 先判定 Question 还是 Issue

- **Question**：用户主要要获得解释、事实、定义、现状说明、使用建议或方案比较；回答本身即可结束，不需要修改代码或文档，不需要验证运行结果，也不需要跨回合推进。
- **Issue**：用户要求或明确暗示需要执行可观察工作，例如调查并交付结论、设计并落盘、修改代码或文档、修复问题、运行验证、同步 `codestable/`、推进或关闭已有实体；这类工作创建或恢复 Task。
- **Question 中包含代码片段、文件路径或技术名词，不会因此自动变成 Issue**。判断依据是用户要“知道什么”还是要“完成什么”。
- **简单现状询问仍是 Question**：只要交付目标是解释当前机制，而不是生成可复用 Explore 产物或推进改变，就不创建 Task。

### 1.2 无法判定时先确认

如果根据用户原话和已有上下文无法可靠区分 Question 与 Issue，必须在创建 Task 前调用 `AskQuestion`，让用户选择“只回答这个问题（Question，不创建 Task）”或“把它作为需要推进的工作（Issue，创建 Task）”。推荐项应放在首位，并说明判断依据；不得猜测后直接创建 Task。

用户要求整理、设计并交付、实现、修复、Review、关闭或其他具体执行动作时，按 Issue 处理。“能不能帮我修好”是执行请求，不只回答“可以”；但 `/cs`、CodeStable、代码路径或技术名词本身不构成 Issue。“/cs 解释 Task”仍是 Question。结合上下文判断意图，不能仅靠关键词升级。

### 1.3 前置文档先于 Task gate

Issue 可以属于接入、讨论整理、愿景、规格、理解现状、修 bug、设计、快交付、受管理实现、收尾、只读 Review、记知识和学流程等不同姿态。先完成有界分析讨论与业务依据，再创建或恢复 Task；Task gate 约束实施，不阻止为明确工作而读取仓库、核对历史、收束方案和准备前置文档。

1. **分析形成结论**：明确目标、范围、现状依据、方案与验证方式；信息不足先澄清，不创建空壳 Task。需要长程调查或穿刺才能确定最终方案时，先明确本轮调查目标与停止条件，不假装未知已解决。
2. **准备前置文档**：按归属创建或更新相关 Issue、`ff`、Epic Spec 或现有目标正本，写入本轮结论及验收依据。已有同主题文档直接更新。Project Spec 只保存已成立事实；本次未实现目标留在 Issue / Epic，必要时先标具体漂移。
3. **再创建或恢复 Task**：扫描 active 与 archived，关联已经存在的依据，将实施和验证步骤写入 Task，再同步原生 Tasks 并执行。不得把首次创建必要 Issue / Spec 推迟到 Task 完成之后。

- 只准备本次需要的文档，不强制完整初始化或生成 Vision / Epic。维护 Spec / Talk / Note / Tool 时复用该正本；新建文档工作先记录已确认的目的与范围，Task 再负责完善与验证，不递归创建“为了写文档的文档”。
- 纯只读 Review 使用现有审查对象与规格；用户明确禁止业务文档时不越权创建，Task 记录授权边界及现有依据。这些情形不豁免已确认 Issue 的 Task，也不允许把例外套到普通实现。
- Task 创建是前置依据就绪后的机械 gate，不再询问“是否创建 Task”；只操作 Task 自身时不递归创建第二个 Task。

## 2. 目录与命名

```text
codestable/tasks/
├── active/
│   └── {task}.md
└── archived/
    └── YYYY-MM-DD-NNN-{task}.md
```

- Active 正本：`codestable/tasks/active/{task}.md`。
- Archived 正本：`codestable/tasks/archived/YYYY-MM-DD-NNN-{task}.md`。
- `{task}` 使用小写英文短横线，active 文件不带日期。
- archived 文件必须带归档日期和三位每日递增序号；当天第一个归档为 `001`，例如 `YYYY-MM-DD-001-{task}.md`。
- 序号按归档日期在所有 Task 之间共享，每天从 `001` 重新开始；同一天按完成归档的先后连续递增，不允许重复或跳号。
- 日期前缀、每日序号和 `{task}` slug 是 `tasks/archived/` 的私有命名契约，不改变 Issue、Epic、Note、Talk 或其他实体的路径与编号。Task runtime 只读写 `codestable/tasks/`，不得在 `issues/` 下创建日期目录、Task 目录或任何业务产物。
- Lite 采用单写者模型，不生成 lock、staging、tombstone 或 conflict 目录。Task Markdown 是唯一运行正本，Git 承担长期历史审计。
- 扫描 Task 必须直接枚举文件系统；不得因为 ignore-aware Glob / grep 没结果就判断没有 Task。

## 3. Schema 与固定正文

```yaml
---
doc_type: task-list
task: improve-auth-flow
goal: Improve the authentication flow
status: active
workflow: feature
owner_skill: cs
created: YYYY-MM-DD
updated: YYYY-MM-DD
archived: null
related_docs:
  - codestable/issues/001-o-improve-auth-flow.md
  - src/auth/service.py
---
```

字段约束：

frontmatter 是封闭 schema：除下表字段外不得添加未知字段。

| 字段 | 约束 |
|---|---|
| `doc_type` | 固定 `task-list` |
| `task` | 与 active 文件名一致的小写英文短横线 |
| `goal` | 本次可完成的人类可读目标 |
| `status` | active 中为 `active / blocked / completed / cancelled`；archive 中仅 `archived` |
| `workflow` | 当前姿态或工作类型 |
| `owner_skill` | Lite 固定由 `cs` 继续执行 |
| `created / updated / archived` | ISO 日期；未归档时 `archived: null` |
| `related_docs` | 已存在的前置业务依据、canonical 产物、代码和证据索引 |

固定正文必须各出现且只出现一次：

```text
## 1. 任务目标
## 2. 当前状态
## 3. Agent 原生 Tasks 同步区
## 4. CodeStable 文档索引
## 5. 执行步骤
## 6. 中断恢复提示
## 7. 完成与归档记录
```

模板见 `templates/entities/task.md`。

## 4. 状态机

```text
active -> blocked -> active
active -> completed -> archived
active -> cancelled -> archived
```

禁止：`active -> archived`、`blocked -> archived`、`completed -> active`、`cancelled -> active`、`archived -> active`。

`completed` 不是最终状态。只有 archived 正本 schema 有效，且 active 同名文件不存在，Task 才闭环。Task 归档后仍须完成关联业务文档的结果与最终状态回写，才能结束整个工作流。

## 5. Runtime

所有 create、批次 update、complete、archive 和 cleanup 必须通过 Skill 自带 runtime：

```bash
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . scan
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . create \
  --task {task} --goal "{goal}" --workflow {workflow} --owner cs \
  --step "{step}" --related-doc "{path}"
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . update \
  --task {task} --expected-sha256 {sha256} \
  --replacements-json '{"old":"new"}' --record "{progress}"
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . write-active \
  --task {task} --content-file {path} --expected-sha256 {sha256}
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . set-status \
  --task {task} --status blocked --expected-sha256 {sha256} \
  --reason "{reason}"
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . complete \
  --task {task} --expected-sha256 {sha256}
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . archive \
  --task {task} --date YYYY-MM-DD --expected-sha256 {sha256}
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . cleanup --task {task}
python3 <cs-skill>/scripts/codestable_task_runtime.py --root . migrate-archive-filenames
```

从旧版 `YYYY-MM-DD-{task}.md` 升级时，先运行 `migrate-archive-filenames`。同一天只有一个旧归档时，runtime 可安全迁移为 `001`；同一天存在多个旧归档或新旧格式混合时，历史完成顺序无法可靠推断，命令会 fail closed，必须先按已知完成顺序人工补齐三位序号。

`<cs-skill>` 从已加载 `SKILL.md` 的目录解析，不假设目标项目复制了 scripts。

Lite runtime 假定同一仓库同一时间只有一个 Task 写入者。创建 active Task 使用不覆盖目标的独占发布；若目标在发布时出现，保留已有证据并失败。更新已有 active Task 使用 SHA-256 陈旧快照保护：先读取正本并计算 hash，再提交完整新内容或受保护替换。若 hash 已变化，重新读取并合并；不得用旧快照覆盖。该机制用于单写者工作流中的外部改写检测，不提供多进程事务隔离。

`create` 要求至少一个实际工作步骤。checklist 与执行步骤的标题、顺序和完成进度必须一一对应：`[x]` 只对应 `done`，未勾选项只对应 `pending / in-progress / blocked`。`update` 可以执行受保护文本替换，也可以只追加一个证据批次记录；两种形式都必须提供当前 SHA-256。`write-active` 和 `update` 不允许删除、重命名或重排已承诺步骤，也不允许绕过状态机修改受保护字段。阻塞、恢复或取消使用显式 `set-status`，且目标状态必须不同于当前状态；完成使用 `complete`。`complete` 只接受 checklist 全部勾选且执行步骤全部为 `done` 的 Task。进入 `completed / cancelled` 后正文冻结，只能归档。

用户中途变更按 [autonomy](autonomy.md) 处理：补充细节可更新原 Task；必须替换承诺步骤时取消并归档旧 Task、关联新 Task，不伪造 done。原生 Todo 不支持 blocked 时，未完成步骤映射为 pending 并在内容标阻塞；Task 正本保留真实状态。runtime 不会调用宿主 Todo、管理子代理或判断规格毕业是否完成。

`archive` CLI 成功及重放成功均返回 `next_action: write-back-related-business-documents`，提醒继续关联文档回写；这不是业务回写已经完成的证明，runtime 不读写业务实体或验证其创建时序。

**归档不是 Task 计划步骤。** checklist 和执行步骤不得包含“归档 Task / archive Task”之类的生命周期动作。实际工作步骤全部完成后，runtime 机械执行 `complete -> archive -> cleanup / scan`；随后由 Agent 回写关联业务文档。归档后的最终状态回写也属于生命周期出口，不列成归档前必须勾选的步骤；其内容、目标位置和授权检查必须事先准备好。

**已授权提交包含最终回写时**，Task 步骤记录提交准备与验证，实际 commit 属于回写之后的收尾出口，不把未执行提交标成 done。归档前记录授权、待提交范围与恢复动作；归档后回写业务文档，再执行提交并核对结果，成功后才能宣布已提交。提交失败按业务正本与 Git 状态恢复，不修改冻结 Task。已承诺的实际提交步骤需要调整时仍走自治契约，不静默改成准备；此边界不豁免部署、生产写入等真正的执行目标。

archive 再次校验调用方提供的 source hash，把 active 正本改写为 archived schema，原子移动到私有 quarantine，再记录源快照 hash 并以独占硬链接发布 archived 正本；原命令重放可以收敛 quarantine 移动后或 archive 发布后的中断。目标已存在时不会覆盖证据。若 active 在归档后被旧写入者重建，`cleanup` 会判断它是否与 archived 记录的源快照或归档正文完全一致；一致时清理这份残留，不一致时保留双方证据并报告 `duplicate-task-state`。删除前会持有文件描述符并复核 device、inode、size、mtime 与 hash；本模型仍以单写者为前提，不承诺抵御另一个不合作进程在最终系统调用窗口内替换私有 quarantine。`scan` 只负责验证状态，不执行删除。

## 6. 全流程 spine

```text
Question
  -> 有界只读理解（按需）
  -> 直接回答（不创建 Task）

无法判定 Question / Issue
  -> Task 创建前调用 AskQuestion
  -> 选择 Question 或 Issue 路径

用户提出问题 / 需求
  -> 有界分析讨论 / 必要澄清，形成结论
  -> 创建或更新相关 Issue / Spec 等前置文档
  -> 创建或恢复 active Task
  -> 同步 Agent 原生 Tasks
  -> 实施修改或交付一个可观察批次
  -> 更新 Task
  -> 测试 / 必要 Review（失败 -> 修改 -> 更新 Task -> 复测）
  -> 准备业务回写内容、位置与授权依据
  -> 执行步骤与验证 gate 完成
  -> Task 标记 completed
  -> 立即原子归档
  -> cleanup / scan 验证 active 同名文件不存在
  -> 更新所有相关 Issue / Spec 等文档的结果、最终状态和链接
  -> 回读确认业务回写完整
  -> 最终答复
```

“可观察批次”是能独立说明输入、动作和结果的一组工作，例如完成一次调查、实现一个垂直切片、处理一轮 review findings、完成一组文档同步或跑完一轮验证。不要把每个文件编辑拆成一个批次，也不要跨多个已完成批次不更新。

Question 路径可以进行必要的有界只读读取，但不得为了回答问题创建或更新 Task、Issue、ff、Talk、Note 或其他持久化产物。若回答过程中发现需要跨回合推进、生成可复用调查产物、修改文件或运行必须留证的验证，应在进入该工作前重新执行 Question / Issue 判定；无法判定时使用 AskQuestion。

## 7. 恢复与冲突

1. 分析结论与前置文档就绪、准备进入执行时，同时扫描 active 与 archived；Question 路径不扫描或恢复 Task。
2. 唯一匹配 active Task：先确认关联业务依据仍然成立，再恢复第一个未完成步骤。旧 Task 缺前置依据时先补齐并如实记录补救，不倒填创建时序。
3. 没有 active 且已有 archived：不得复活。若只是该次归档后的业务回写中断，按第 9 条继续；真正的新执行目标先更新业务依据，再使用新 slug。
4. 多个 active 都可能匹配时，不在计划后询问用户；按目标文本、related docs、最近更新时间和当前诉求确定最匹配项。仍无法唯一确定时，为当前明确目标创建新 slug，不覆盖旧 Task。
5. active 中出现 `status: archived` 表示归档移动中断；按其 `archived` 日期和当前 hash 再次执行 archive，不需要中间目录。若 active 只是被重建为与 archived 完全一致的旧快照，archive 或 cleanup 可以安全清除这份残留并恢复单一正本。
6. active 与 archived 同名并存、同 slug 多个 archive 或任一 Task schema 无效时 fail closed：保留原文件，先报告 finding，不自动删除或覆盖。对比结果若证明 active 只是 archive 的字节级重现，则视为残留恢复问题，而不是两份不同来源的 Task。
7. `scan` 报告 `archive-pending-move`、`duplicate-task-state`、`multiple-archives`、`invalid-task-document`、`invalid-archived-task`、`duplicate-daily-archive-sequence` 与 `noncontiguous-daily-archive-sequence`；`tasks/` 下的额外 runtime 目录，以及 active / archived 内的目录、symlink、非小写 `.md` 文件也属于 finding。存在这些 finding 时，完成 gate 不成立。若唯一 active 残留与 archived 正本完全同源，先运行 `cleanup` 清理，再用 `scan` 验证闭环；存在非规范归档文件时不得删除 active 证据。
8. `scan` 发现任一 finding 时命令返回非零状态；自动化调用不得只读取输出而忽略退出码。
9. Task 已归档但关联文档尚未回写：读取归档证据、`related_docs` 与业务正本，只补同一工作流的最终回写，不修改冻结 Task，也不创建“收尾回写 Task”。归档前记录将发生的 `-o-` → `-x-` 等路径映射；归档后在业务正本记录原路径和 Task archive，更新仍可变的引用。恢复时按该映射定位，不为修历史链接改写 archive。回写失败时保留证据，明确报告“Task 已归档，业务回写未完成”，不得宣称工作完成。

## 8. 完成 gate

Task 进入 `completed` 前必须满足：

- Task 同步区和执行步骤全部完成；
- 本次目标的实现、文档或只读交付物已完成；
- 必要测试、静态检查、Review、QA 或 Agent 可执行且可观察判定的验收已通过；不临时添加无依据的人工验收，用户中途明确新增的验收与必要授权按自治契约处理；
- 实现与交付物的 canonical 契约已同步，不存在同一契约两套表述；关联业务文档的最终结果与状态留到归档后更新，不能提前伪称已完成；
- 已按 [自动回写与沉淀](retention.md) 准备规格、Talk、Note、Tool 的结论、目标位置、路径变化、授权或无增量依据，并记入现有正本；不得用 Task 归档代替业务回写；
- 没有未处理的 blocking finding；
- 没有未完成的执行或验证步骤；只剩机械归档、已准备好的关联状态回写，以及按上文安排的已授权收尾提交。

归档后执行 cleanup 和 scan，再更新所有相关 Issue / Spec 等文档的结果、最终状态与索引，回读确认。常规 Issue 未获关闭授权则保持 open，明确写完成/关闭就绪状态；`ff` 按默认授权关闭，Epic 关闭仍须明确批准。只读或禁止业务写入时说明不适用依据。

active 同名文件仍存在、archive schema 无效、存在重复状态或关联业务回写未完成时，不得给出完成式最终答复。Markdown runtime 不判断业务语义或文档真实创建时序，不能把 `scan` 通过当成这些检查已经完成。
