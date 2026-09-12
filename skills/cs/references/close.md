# Close：关闭与沉淀

本姿态继承 [Task 主线](task.md) 与 [计划后自治](autonomy.md)。询问关闭规则时直接回答且不创建 Task；真正关闭 Issue / Epic 时，先核对已有业务文档与授权、记录关闭范围和验收依据，再创建或恢复 Close Task 完成检查及回写准备。Task 归档后落实毕业内容、业务状态和路径变化，再核对引用；Task 归档本身不等于业务实体关闭。

关闭 issue 或 epic，把仍成立的结论**毕业**到正确层级；Epic 关闭时检查来源 Vision 的实现状态与链接。

**关闭 ≠ 完成。** 完成指实现与验证已达成目标；关闭须用户授权收尾（“关闭 / 收尾 / 做完并沉淀”等）。Git 契约见下与 `SKILL.md`。

**关闭 ≠ 整理进 `done/`。** 关闭只做 `o`→`x` 与毕业回写；把已完成项挪到其所属 issues 树的 `done/`，或把 Epic 挪到 `epics/done/`，仅在用户主动要求整理时进行（见 `SKILL.md`「完成 · 关闭 · done」）。

## 背景

复利在关闭时的回写：issue 留执行历史；epic spec 留活规格边界内的当前理解；project spec 留主线真相。回写层级见 `SKILL.md` 毕业规则与下文。

## 原则

**先检查可以关闭。** 目标达成、范围未暗扩、已选质量目标均有相称证据。Epic 的人类关闭授权必须在关闭执行前取得，不能因 issue 看起来都完成就自行关闭。实现验证后按 [自动回写与沉淀](retention.md) 准备当前事实，Task 归档后回写；关闭时复核已同步内容，不以关闭授权缺失阻止已授权的事实维护。

**只沉淀仍然有效的东西。** 不把事项全文搬进 spec；流水与中间判断留原事项。

**回写到正确层级。** 独立 issue → project spec；epic issue → epic spec；epic 关闭 → project spec 并检查 Vision。关闭 Epic 的毕业是把稳定结论的**具体内容**写进 Project Spec：不能只写“见某 Epic”、把 Epic 链接当作主叙述，或要求读者先读已关闭 Epic 才能理解当前系统。Epic 链接只保留为历史、证据或深入设计的阅读入口。普通 issue 不更新 Vision。notes / Agent 指令 / tools 按复用价值分流。

**只按事实更新 Vision 状态。** 实现程度与链接可更新；目标内容或候选关系要变时，修改前必须取得授权。未授权时记录偏差并保持原目标；必要澄清按 autonomy 处理。

**spec 写当前为什么这样。** 不写“某天从 A 改到 B”的流水。

**只按承诺检查质量。** 不重开九项清单。关键遗漏 → 回 Design 补目标与响应，再 Do；不能在关闭结论里临时降级。见 [quality](quality.md)。

**有界简化必须仍有界。** 检查上限、触发未发生、未削弱目标与承诺。稳定产品边界 → spec；维护坑点 → notes；触发已发生且阻碍目标 → 回 Design/Do，不能以“后续再做”关闭。见 [economy](economy.md)。

**UI 按真相层级毕业。** 见 [ui-spec](ui-spec.md)。

**核心理解不引用代码。** 代码路径与命令留 issue/notes/证据索引。见 [docs](docs.md)。

**先守组织再写内容。** 从 `codestable/spec/index.md` 找路径；缺位置先补入口，不散落平级文件。

**探索文章按渐进式披露毕业。** 不是原样搬家；稳定现状机制说明按 Spec 结构安置。

## 行动指南

### 读取关闭上下文

- issue：用户给路径则读该文件/目录；否则递归搜索根 `codestable/issues/` 与各 Epic 的 `issues/`，按名称、完整路径或 `Epic NNN / Issue NNN` 消歧
- epic：读权威 `spec.md`、同目录 `issues/`、明确引用的相邻材料；旧版根 issues 中带该 epic 关联的事项也要检索

写入或暂存前确认目标事项、将回写的 spec/notes/Agent 指令/tools、以及要提交代码的当前版本。

归档前完成验收、授权核对和内容级回写准备，在 Task 记录目标章节、证据及关闭改名映射。Task 更新、完成、原子归档并经 cleanup / scan 确认后，才执行下文的最终内容回写、closed 标记和路径改名；回写结果记录到业务正本，不改冻结 Task。若只是前次归档后的回写中断，按 task.md 恢复该出口，不再创建 Close Task。

### 关闭 issue

若目标是旧版根 `issues/` 中仍 open、但通过 `epic` frontmatter 归属某 Epic 的 Issue，先按 `SKILL.md` 迁移约定移入该 Epic 的 `issues/` 并更新明确引用，再关闭；已关闭历史项不为整理目录而迁移。

路径规则：只把目标 Issue 文件名或目录名中的 **`-o-` 改为 `-x-`**，保留 `NNN`、可选的 `ff`、名称与所属 issues 树不变。例如 `012-o-fix-login.md` → `012-x-fix-login.md`；Epic 内 `issues/015-o-ff-toolbar.md` → `issues/015-x-ff-toolbar.md`；Explore 目录 `issues/003-o-auth-flow/` → `issues/003-x-auth-flow/`。不要因关闭子 Issue 改 Epic 目录状态。

- **普通 issue**：检查目标、范围、质量目标、执行记录与验证；有界简化则检查上限/触发/方向。缺记录或证据 → 回 Design/Do。
- **ff issue**：检查四答是否齐全（做了什么 / 改了哪些 / 验证 / 对 `codestable/` 的影响）。真相失效须已同步 spec 或明确标漂移；不要求完整质量清单与实现设计。快改应先有 `o-ff`，Task 归档后回写并关闭；已经按此闭环的无需再关一次。
- **Explore issue**：不要求业务代码执行记录。须能讲清触发—过程—结果，相关责任/数据/状态有证据，未知显式标出；有具体变化时影响已分层。未达“足够行动” → 继续探索，不进 Do。

按物理归属回写；路径是权威来源，旧版 `epic` frontmatter 只用于识别并迁移 open 事项、读取已关闭历史：

- `type: ff`：默认不强制大段毕业；按「对 `codestable/` 的影响」执行已记录方向；坑点可进 notes
- 独立非 ff：稳定结论 → project spec
- Epic 内事项（包括 Explore）：结果、仍有效约束、推进变化与毕业候选 → 该 epic `spec.md`；验证记录只保留索引，不把测试流水写成规格
- `type: explore`：按上述物理归属毕业；独立 Explore 的稳定现状机制说明 → `codestable/spec/` 并更新 `index.md`；影响分析留 `related_issue`，证据与已排除理解留 Explore issue，在 `## 关闭回写` 记录迁入位置

坑点 → notes；启动短规则 → `AGENTS.md` / `CLAUDE.md`；稳定工具 → tools。

### 关闭 epic

仅用户明确批准并把关闭授权写入 Task 后执行。关闭就绪时按 retention 呈现可审查的毕业候选并请求一次授权；已有批准不重复问。随后自动确认：关闭条件满足；epic 内直接推进已有足够验证；相关 issue 已关或明确废弃/移出；质量约束有证据或保留为后续约束；毕业候选足够稳定。

先核验并准备 Epic 的稳定成果与合并位置；Close Task 归档后把具体内容整理进 `codestable/spec/` 的合适层级，再关闭 Epic。整理时至少回答：当前系统新增或改变了什么能力、它怎样工作、关键责任/数据或状态边界是什么、后续变化必须遵守什么约束、哪些范围仍不属于它。Project Spec 的正文必须让只读当前规格的人理解这些结论；不要用“详见 Epic”代替内容，也不要原样搬运 issue 列表、实施过程或测试流水。

写入后逐项检查：

- Project Spec 已有可独立阅读的能力说明、核心契约和长期取舍；链接只承担证据或深入阅读路径。
- 已关闭 Epic 中仍有价值的内容只保留为设计历史、验证证据、被排除方案或更细的背景，不再是当前真相的唯一出处。
- Project Spec 没有遗留与实现冲突的旧表述；活跃但尚未关闭的其他 Epic 不被误写成已毕业的稳定契约。

完成上述回写检查后，epic `spec.md` 标 `closed` 并记录 Project Spec 中的具体合并章节；目录名 `-o-` → `-x-`（序号与名称不变）。有来源 Vision 则按事实更新实现程度与链接；发现目标内容需要变化时，未经授权只记录偏差，不修改目标。

### 提交关闭变更

只有已明确授权 commit 时，关闭结论与长期实体回写才与相关业务变更进入同一 commit；未授权则保留工作区改动并完成其余关闭动作，不为可选提交补问。关闭授权不是提交授权。

顺序是 `准备与验证 -> Task 归档 -> 业务回写 -> 已授权提交 -> 最终答复`。Task 的执行步骤只承诺提交准备与验证，实际提交作为回写后的出口，不能在归档前把未发生的 commit 标为 done。归档前记录提交范围与授权；失败时从业务正本与 Git 状态恢复并明确报告未提交，不修改冻结 Task。未授权提交时跳过该出口。

已授权提交时，提交前运行 `git status --short`，只暂存相关文件。无关脏改不碰；同文件混有无法安全拆分的无关变更时排除该文件的提交并记录原因，不停止其余关闭动作。不 amend / rebase / reset；不 push，除非已明确授权。

## 产物契约

关闭 issue：

- 常规 issue 写清关闭结论：判断、验证摘要（含质量证据）、结论对应的目标文件及章节、遗留事项；无规格增量须说明原因；ff 以「对 `codestable/` 的影响」为准，可无长关闭结论
- `status: closed`；路径 `-o-` → `-x-`（序号与名称不变）

关闭 Explore issue：另更新 spec 阅读路径，并在 Explore 入口记录迁入结果。

关闭 epic：

- Project Spec 已直接写入稳定能力、核心契约、长期边界与取舍；不得只记录 Epic 链接或“见 Epic”
- `spec.md` 状态 `closed`；记录合并到 Project Spec 的具体章节与已检查/更新的 Vision
- 目录 `{NNN}-o-{名称}/` → `{NNN}-x-{名称}/`；不删除目录

遗留事项应成新 issue 候选或留在 epic 当前推进/阻碍中，不藏在关闭结论里；只有计划确定前已获授权才新建 Issue，否则记入 Task 候选后继续收尾。

## 收尾汇报

Task 归档后的业务回写、状态与路径核对全部完成后，才汇报为何可关、质量证据、沉淀到哪一层、Epic 时如何同步或保留 Vision、是否已 commit。路径与 commit 作证据；业务回写失败必须明确报告，不能只凭 Task archived 声称关闭完成。

## 应用场景

实现验证完成且获授权后关闭 issue；Explore 按归属合并 project/epic spec；bug/feature 关闭复核沉淀；Epic 获准后关闭并毕业。

不适用：代码未完成 → Do；设计缺口 → Design；规格仍变 → Spec；默认不推送不部署。
