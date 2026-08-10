# Task：全部姿态的强制运行账本

Task 是 `cs` 单一入口内的横切运行主线，不是新的 Skill，也不替代 Vision、Project Spec、Epic、Issue、Explore、Talk 或 `ff`。这些实体记录软件理解与演化边界；Task 只记录本次工作如何创建、推进、恢复和闭环。

**Task List 是 source of truth**；Agent 原生 Todo / Tasks 只是运行时镜像。Task 文件先更新，原生任务视图后同步。原生视图不可用时继续以 Task 文件推进，不得只更新原生视图。

## 1. 适用边界：所有姿态

除尚未形成可执行目标的 intake 澄清外，所有姿态都必须走 Task 生命周期，包括：接入、讨论整理、愿景、规格、理解现状、修 bug、设计、快交付、受管理实现、收尾、只读 Review、记知识和学流程。

- 可以在**计划确定前**使用 AskQuestion 澄清目标、边界和验收。
- 一旦能写出本次目标与步骤，就先创建或恢复 Task，再开始读取仓库、分析、设计、写文档、改代码或 Review。
- Task 创建是机械 gate，不询问是否创建；“不要痕迹”“只读”“小改”“不用 issue”都不能豁免。
- 只操作 Task 自身时更新当前 Task，不递归创建“管理 Task 的 Task”。这不是例外，而是同一生命周期的内部动作。

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
| `related_docs` | canonical 产物、代码和证据索引 |

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

`completed` 不是最终状态。只有 archived 正本 schema 有效，且 active 同名文件不存在，Task 才闭环。

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

**归档不是 Task 计划步骤。** checklist 和执行步骤不得包含“归档 Task / archive Task”之类的生命周期动作。实际工作步骤全部完成后，runtime 机械执行 `complete -> archive -> cleanup / scan`；archive 正本本身已经证明归档发生，无需再用一个待办记录它。

archive 再次校验调用方提供的 source hash，把 active 正本改写为 archived schema，原子移动到私有 quarantine，再记录源快照 hash 并以独占硬链接发布 archived 正本；原命令重放可以收敛 quarantine 移动后或 archive 发布后的中断。目标已存在时不会覆盖证据。若 active 在归档后被旧写入者重建，`cleanup` 会判断它是否与 archived 记录的源快照或归档正文完全一致；一致时清理这份残留，不一致时保留双方证据并报告 `duplicate-task-state`。删除前会持有文件描述符并复核 device、inode、size、mtime 与 hash；本模型仍以单写者为前提，不承诺抵御另一个不合作进程在最终系统调用窗口内替换私有 quarantine。`scan` 只负责验证状态，不执行删除。

## 6. 全流程 spine

```text
intake / 必要澄清
  -> 形成目标与计划
  -> 创建或恢复 active Task
  -> 同步 Agent 原生 Tasks
  -> 执行一个可观察批次
  -> 先更新 Task，再继续
  -> 验证 / Review / 修复循环
  -> 全部目标与 gate 完成
  -> Task 标记 completed
  -> 立即原子归档
  -> cleanup / scan 验证 active 同名文件不存在
  -> 最终答复
```

“可观察批次”是能独立说明输入、动作和结果的一组工作，例如完成一次调查、实现一个垂直切片、处理一轮 review findings、完成一组文档同步或跑完一轮验证。不要把每个文件编辑拆成一个批次，也不要跨多个已完成批次不更新。

## 7. 恢复与冲突

1. 开始 substantive work 前同时扫描 active 与 archived。
2. 唯一匹配 active Task：恢复第一个未完成步骤，在当前 run 继续。
3. 没有 active 且已有 archived：不得复活；新目标使用新 slug。
4. 多个 active 都可能匹配时，不在计划后询问用户；按目标文本、related docs、最近更新时间和当前诉求确定最匹配项。仍无法唯一确定时，为当前明确目标创建新 slug，不覆盖旧 Task。
5. active 中出现 `status: archived` 表示归档移动中断；按其 `archived` 日期和当前 hash 再次执行 archive，不需要中间目录。若 active 只是被重建为与 archived 完全一致的旧快照，archive 或 cleanup 可以安全清除这份残留并恢复单一正本。
6. active 与 archived 同名并存、同 slug 多个 archive 或任一 Task schema 无效时 fail closed：保留原文件，先报告 finding，不自动删除或覆盖。对比结果若证明 active 只是 archive 的字节级重现，则视为残留恢复问题，而不是两份不同来源的 Task。
7. `scan` 报告 `archive-pending-move`、`duplicate-task-state`、`multiple-archives`、`invalid-task-document`、`invalid-archived-task`、`duplicate-daily-archive-sequence` 与 `noncontiguous-daily-archive-sequence`；`tasks/` 下的额外 runtime 目录，以及 active / archived 内的目录、symlink、非小写 `.md` 文件也属于 finding。存在这些 finding 时，完成 gate 不成立。若唯一 active 残留与 archived 正本完全同源，先运行 `cleanup` 清理，再用 `scan` 验证闭环；存在非规范归档文件时不得删除 active 证据。
8. `scan` 发现任一 finding 时命令返回非零状态；自动化调用不得只读取输出而忽略退出码。

## 8. 完成 gate

Task 进入 `completed` 前必须满足：

- Task 同步区和执行步骤全部完成；
- 本次目标的实现、文档或只读交付物已完成；
- 必要测试、静态检查、Review、QA 或 Agent 可执行且可观察判定的验收已通过；用户人工验收仅在 Task 创建前明确纳入时才是完成条件，计划后不得临时新增；
- 相关 canonical 文档已同步，不存在同一契约两套表述；
- 没有未处理的 blocking finding；
- 没有计划内待办或确定性的下一动作。

归档后再执行 cleanup 和 scan。active 同名文件仍存在、archive schema 无效或存在重复状态时，不得给出完成式最终答复。
