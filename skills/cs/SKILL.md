---
name: cs
description: >
  CodeStable：一套软件演化理解（Vision/Project Spec/Epic/Issue + codestable/ 制度记忆），按用户当前姿态行动——讨论、快改、受管理实现、修 bug、整理愿景/规格、现状理解、关闭收尾、按需 review。
  触发：cs、CodeStable、讨论/先聊清楚、快速/快改/直接开干、穿刺、修 bug/debug、整理 vision/spec、关闭/收尾、review、这系统怎么工作、项目已有 codestable/ 且在处理愿景规格 bug 实现关闭时。
  调用 cs 不等于生成完整业务流水线：先判姿态再行动。完整初始化 codestable/ 须用户明确要求；强制 Task runtime 可按需创建 codestable/tasks/。
---

# CodeStable

CodeStable 是一套理解和推进软件演化的方法。它用 Vision、Project Spec、Epic、Issue 和 `codestable/` 中的制度记忆连接目标、现实与行动；它**不是**强制流水线，也不是 Agent 编排器。

调用 `cs` 不等于跑完整流程。先判断用户此刻要讨论、理解、设计、实现还是收尾，再采用匹配的管理强度。

### 沟通方式：先结论，再展开

这里“不跑完整生命周期”只表示不强迫每个请求生成 Vision / Spec / Epic / Issue；**不豁免 Task 生命周期**。Task 是全部姿态共享的运行账本，不是另一套业务流程。

### 沟通默认：先简单，后展开

先用自然、简短的话说清**结论和原因**，优先使用用户正在使用的词；不要一上来抛框架、术语、章节或长清单。只有用户明确要求、需要做取舍/授权，或必须给出验证与风险证据时，才展开实现安排、规则与细节。简短不是省略关键判断：先让用户容易听懂，再按需下钻。

### 节省上下文（Codex）

同一会话中，已经完整读取且没有变化的 `SKILL.md`、reference、template 或相邻说明，必须复用既有理解，不要重复读取。仅在用户要求重读、文件已变化，或当前理解不足以支撑判断时，读取相关最小范围。

### 不预拆迷雾

还不能精确表述的问题，不要为追踪而提前拆成 issue；先用 Talk、Explore 或穿刺把目标、现状或关键风险弄清，能说成可关闭行动后再建 issue 或 Epic。

### 全部姿态强制 Task 主线

先读 [Task 主线](references/task.md) 与 [计划后自治](references/autonomy.md)。尚不能形成目标与步骤时属于 intake，可以使用 AskQuestion 澄清；一旦计划足以开工，必须按以下顺序执行，**所有姿态无例外**：

1. 扫描 `codestable/tasks/active/` 与 `archived/`，创建或恢复 Task；
2. 以 Task 正本同步 Agent 原生 Tasks，在当前 run 开始工作；
3. 每个可观察批次完成后，先用 SHA-256 陈旧快照保护更新 Task，再继续下一批；
4. 自动完成分析、设计、实现或只读交付、验证、必要 Review 与修复循环；
5. 全部完成后把 Task 标记 completed，立即原子归档并 cleanup；
6. 只有 archived 正本 schema 有效、active 同名文件不存在且 scan 无冲突，才能给出完成式最终答复。

Task 不可被用户要求的无痕模式豁免。“不要 issue / 不写 ff / 只读 / 小改 / 只在对话回答”只影响业务实体和交付形式，不影响 Task 创建、更新、完成与归档。Task 自身操作更新当前 Task，不递归创建第二个 Task。

计划写入 active Task 后即进入无人值守：禁止再次 AskQuestion，也不要求用户选择实现路线或批准普通下一步；出现分叉、失败或范围内偏差时，按 autonomy 的契约一致性、风险、可逆性、证据与总成本排序自动选择推荐方向，更新 Task 后持续执行到全部工作完成。

---

## 1. 先定姿态

从用户原话与上下文中选择**一个主姿态**。选定后立即读取“必读”，再开始行动；未命中的姿态文件不要预读。

| 主姿态 | 用户常这样说 | 必读 | 按需读 | 默认边界 |
|---|---|---|---|---|
| **接入** | 初始化 cs、接入 CodeStable、补齐 `codestable/` | [onboard](references/onboard.md) | — | 须明确授权；不编造业务内容 |
| **讨论** | 聊聊、先理清、想清楚再做、帮我规划一下 | [talk](references/talk.md) | [docs](references/docs.md)；具体变化 → [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 确认前不落盘、不建 issue/epic/vision |
| **愿景** | 应用将来什么样、整理 vision、产品全景 | [vision](references/vision.md) | [docs](references/docs.md)；质量方向 → [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 确认后才写 vision；不强迫开开发事项 |
| **规格** | 维护 spec、当前真相、epic 活规格 | [spec](references/spec.md) | [docs](references/docs.md)；质量约束 → [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 只写仍成立的结论 |
| **理解现状** | 怎么工作的、这条链路、影响范围 | [explore](references/explore.md) | [docs](references/docs.md)；服务具体变化 → [quality](references/quality.md) | 先现状说明；值得复用再 Explore issue |
| **修 bug** | 坏了、不符合预期、debug、修这个 bug | [complain](references/complain.md) | [debug](references/debug.md)、[economy](references/economy.md)、[quality](references/quality.md)；结构 → [code-design](references/code-design.md) | 简单默认快改落 `ff`；复杂可受管理 |
| **设计** | 怎么实现、先设计、实现方案 | [design](references/design.md) | [code-design](references/code-design.md)、[economy](references/economy.md)、[quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 不写代码；高风险标穿刺顺序 |
| **快交付** | 快速、快改、小改一下、直接开干、别走流程 | [fast](references/fast.md) | [economy](references/economy.md)；必要时 [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 轻检索 + 验证；`ff` 可按用户要求省略，Task 永不省略 |
| **受管理实现** | 做这个 issue、推进 epic、实现（有档）、穿刺/先打通 | [do](references/do.md) | [code-design](references/code-design.md)、[economy](references/economy.md)、[quality](references/quality.md)；现状不清 → [explore](references/explore.md)；UI → [ui-spec](references/ui-spec.md) | 完成 ≠ 关闭；风险先穿刺再加厚 |
| **收尾** | 关闭、收尾、做完并沉淀、毕业回写 | [close](references/close.md) | [docs](references/docs.md)、[quality](references/quality.md)；有界简化 → [economy](references/economy.md) | 须在 Task 创建前获得关闭授权；未授权保持 open 且不补问；**不**自动进 `done/` |
| **审代码** | review、评审、看看这 diff/PR | [code-design](references/code-design.md)（文末 Review） | [economy](references/economy.md)；相关 → [quality](references/quality.md) | 用户点名才做；默认只审不改 |
| **记知识** | 记一下坑、写 note | [note](references/note.md) | [docs](references/docs.md) | 同主题改原 note，不新建第二条 |
| **学流程** | 我带你跑一遍、教 AI 做某流程 | [maketools](references/maketools.md) | [docs](references/docs.md) | 危险操作授权在 Task 创建前收束 |

### 怎样判断姿态

1. **用户授权与原话优先**于“看起来该走重流程”。
2. **小且明确、要快、未要求建档** → **快交付**（不是“先讨论一整轮”）。
3. **目标糊、取舍未定** → **讨论**；聊清后再切快交付 / 受管理 / 愿景等。
4. **已有常规 issue 或用户点名 issue/epic** → **受管理实现**（或先设计）。
5. **坏的是已有行为** → **修 bug**；新能力 → 快交付或受管理，不是 complain。
6. **只问怎么工作** → **理解现状**；不要默认开改。
7. **意图不清且选错会实质改变后续**（例如会不会建 issue、会不会改代码）→ 仅在 Task 创建前用 AskQuestion 给一句推荐 + 理由；Task 创建后按 [计划后自治](references/autonomy.md) 自动择优。
8. 写/改 **Agent 技能本身**仍由当前 `cs` 与同一 Task 负责完整生命周期；可读取相关技能编写规则辅助，但不得转移 owner、另建入口或另建 Task。

### 选择管理强度

| 情况 | 默认选择 |
|---|---|
| 小、一次做完、低风险，或用户要快 | **快改** → 必留 `ff`（[fast](references/fast.md)） |
| 用户**明确**不要 issue / `ff` | 可无 `ff`；Task 仍强制创建、更新和归档；真相失效仍同步 spec 或标漂移 |
| 范围取舍、多轮、交接、显著风险、长期质量承诺 | **常规 issue**（`issue.md`，`type: feature\|bug\|chore\|refactor`） |
| 跨模块、多批、规格在边界内反复演化 | **Epic**；够清楚的切片可 epic 内直接推进 |
| 技术/集成/迁移风险需先证明可通 | **穿刺**（[do](references/do.md) 手法）再加厚 |
| 用户明确要管理 / 明确不要业务实体 | 服从其 Issue / `ff` 偏好；Task 账本不可豁免 |

---

## 2. 世界模型与工作区

### 从目标到现实

```text
Vision Spec（目标世界）
        │ 摘取一段有界变化
        ▼
Epic Spec（变化中的活规格） ──推进──> Epic Issues
        │ Epic 关闭后毕业
        ▼
Project Spec（当前现实）

独立 Issue ─────────关闭毕业────────> Project Spec
```

Vision 保存目标世界；Epic 承载一段有边界的大变化；Issue 是可关闭的行动；Project Spec 只保存当前仍成立的现实。

只靠 Issue 会丢失方向；只靠 Project Spec 无法安放互斥构想；把未来与现实混写会失去时间边界；巨型 Issue 又难以关闭。因此，只把**值得跨会话保留**的信息写入 `codestable/`，并放到承担相应职责的位置。

### `codestable/` 工作区地图

CodeStable 的制度记忆统一存放在项目的 `codestable/` 下。

```text
codestable/
├── vision/  目标世界、旅程与候选方向
├── spec/    当前稳定真相
├── epics/   有界的大变化
├── issues/  可关闭行动（含 ff 与 Explore）
├── notes/   可复用知识
├── talks/   尚未落定的讨论
├── tools/   稳定、可执行的流程工具
└── tasks/   全部姿态的 active / archived 运行账本
```

根 `issues/` 与每个 Epic 内的 `issues/` 使用同一种结构，但各自独立编号：

| 实体 | 路径 | 回答什么 |
|---|---|---|
| **Vision** | `codestable/vision/` | 应用最终什么样、旅程与能力、候选/互斥方向 |
| **Project Spec** | `codestable/spec/` | 现在仍然成立的项目真相（按场景/能力，不按代码目录） |
| **Epic** | `codestable/epics/{NNN}-o\|x-{名}/spec.md` | 有界大变化：已定/仍变、可推进什么（活规格） |
| **Issue** | `codestable/issues/{NNN}-o\|x-[{ff}-]{名}.md` 或 Explore 目录 | 可关闭行动；快改用 `ff` |
| **Task** | `codestable/tasks/active/{task}.md`、`archived/YYYY-MM-DD-NNN-{task}.md` | 本次工作如何推进、恢复和原子闭环 |

图中的 `o|x` 表示取 `o`（open）或 `x`（closed），不是路径中的字面字符。路径表达唯一归属：只属于一个 Epic 的事项进入该 Epic 的 `issues/`，其余留在根 `issues/`。常规 Issue 与 `ff` 是单文件；只有需要独立调查工作区的 Explore Issue 使用目录。Epic 的 `issues/` 在首个所属事项创建时再建立。

**Task 与 Issue 的命名空间必须隔离。** `YYYY-MM-DD-NNN-{task}.md` 只用于 `codestable/tasks/archived/`，不得把日期、每日序号、Task slug 或 Task 目录结构复用到任何 `issues/` 树。普通 Issue 与 `ff` 各自只有一份带所属树序号的 Markdown 正本；根因、修复范围、验证和执行记录写入该正本或 Task，不另建 `{date}-{task}/`、`*-fix-note.md`、`*-report.md`、`*-analysis.md` 等补充事项目录或文件。只有 Explore Issue 可以使用 `{NNN}-o|x-{名}/index.md` 目录结构。检索到历史非规范目录时可将其作为证据读取，但不得照抄为新产物；没有迁移授权时也不自动整理历史文件。

`done/` 只是用户主动整理后的存放位置，不是新的生命周期状态。关闭不会自动移动事项；`done/` 中的内容仍参与检索和编号。

这张图是定位地图，不是每次工作的必读清单。按当前姿态和关键词命中逐层下钻，只读取足以支撑判断的局部。

### 各实体回答什么

| 实体 | 回答的问题 |
|---|---|
| **Vision** | 应用最终要成为什么样；有哪些旅程、能力以及候选或互斥方向 |
| **Project Spec** | 项目现在有哪些仍然成立的稳定事实；按场景和能力组织，不按代码目录组织 |
| **Epic** | 这段有界大变化已经确定什么、仍在变化什么、接下来可以推进什么 |
| **Issue** | 要完成并关闭哪一个具体行动；物理位置表达唯一归属 |
| **Fast Fix (`ff`)** | 这个小改做了什么、改了哪里、怎样验证、是否影响制度记忆 |
| **Explore Issue** | 一个复杂、可停止、可复用的现状调查得出了什么；简单理解只做现状说明，不建事项 |
| **Talk** | 一个尚未落定的议题如何被提出、纠正和收束，以及建议从哪里继续 |
| **Note** | 哪些知识、证据、步骤与坑点在未来仍值得复用 |
| **Tool** | 哪段已跑通的流程已经稳定到可以重复执行，同时仍需守住哪些危险边界 |

### 路径、命名与编号

每棵编号树分别编号：根 `issues/`、每个 Epic 的 `issues/`、`epics/`、`notes/`、`talks/` 都从本树（**包含 `done/`**）已有最大开头数字加 1。编号至少三位；超过 999 后继续使用 `1000`、`1001`，不设上限。

Issue 编号不是全局身份。引用 Epic Issue 时，必须给完整路径，或写成 `Epic NNN / Issue NNN`。

| 形态 | 路径 |
|---|---|
| 独立 Issue | `codestable/issues/{NNN}-o\|x-{名}.md` |
| Epic Issue | `codestable/epics/{EEE}-o\|x-{epic}/issues/{NNN}-o\|x-{名}.md` |
| 快改 | 所属 issues 树下 `{NNN}-o\|x-ff-{名}.md`；`type: ff`；模板 `ff-issue.md` |
| Explore Issue | 所属 issues 树下 `{NNN}-o\|x-{名}/index.md` |
| Epic | `codestable/epics/{NNN}-o\|x-{名}/spec.md`；每个 Epic 只有一份权威 spec |
| 已整理事项 | 对应 issues 树的 `done/` 下保留同名文件或目录 |
| 已整理 Epic | `codestable/epics/done/` 下保留同名目录 |
| Talk / Note | `{NNN}-{名}.md`，不使用 `o`、`x` 或 `ff` |

**归属由路径决定：**
- 关闭：路径 `-o-` → `-x-`，序号与名称不变；`status: closed`。
- 常规 issue 模板：`templates/entities/issue.md`（`type: feature|bug|chore|refactor`）。
- **ff** 只四节：做了什么 / 改了哪些 / 怎么验证 / 对 `codestable/` 的影响；禁止迷你 Design。
- Talk：`codestable/talks/`；Note：`codestable/notes/`（同主题改原文件）；Tool：`codestable/tools/`。
- Task 不参与 issues、epics、notes、talks 等实体编号树；Task archived 文件使用独立的每日三位序号。Task slug 使用小写英文短横线。启动短规则只进会注入的 `AGENTS.md` 或 `CLAUDE.md`（不两处重复）。**不建 `facts.md`。**
- 项目局部旧规则、历史文件或相邻样例若要求为普通 Issue / `ff` 另建日期目录、Task 目录或 `fix-note`，视为已过期的组织契约；新产物仍按本节单一正本规则生成，并在 Task 中记录冲突来源，不制造第二套结构。

- 只属于一个 Epic 的 Issue，必须进入该 Epic 的 `issues/`。
- 不属于任何 Epic 的 Issue，留在根 `issues/`。
- 跨多个 Epic 的事项，不得随意挂到其中一个；应保留为独立 Issue，或升级为 Epic。
- `ff`、bug、feature、chore、refactor 与 Explore Issue 都遵守同一归属规则。
- 新建 Issue 不再用 `epic` frontmatter 表达归属。归属改变时移动原事项并更新明确引用，不复制第二份。

旧版中位于根 `issues/`、依靠 `epic` frontmatter 关联的**已关闭** Issue 仍然有效，不自动迁移。仍在推进的旧 Issue，在下次实质更新时移入所属 Epic：优先保留原编号；若编号冲突，则使用该 Epic issues 树的下一编号，并更新明确引用。

关闭 Issue 时，将目标路径中的 `-o-` 改为 `-x-`，序号与名称不变，并把 `status` 改为 `closed`。关闭 Epic 时只改 Epic 目录名，内部 Issue 随目录保留。

常规 Issue 使用 `templates/entities/issue.md`，`type` 只能是 `feature|bug|chore|refactor`。`ff` 只回答四件事：做了什么、改了哪些、怎样验证、对 `codestable/` 有什么影响；不要写成迷你 Design，也不要保留空槽位。

Talk 写入 `codestable/talks/`；Note 写入 `codestable/notes/`，同主题更新原文件；Tool 写入 `codestable/tools/`。启动时必须自动注入的短规则，只写入 `AGENTS.md` 或 `CLAUDE.md`，不要在两处重复，也不要创建 `facts.md`。

### 什么内容可以写到哪一层

| 写入位置 | 时机 |
|---|---|
| Vision 目标内容 | 用户确认的愿景整理；实现结论要改目标时只在 Task 创建前确认，计划后记录差异并保持原目标 |
| Vision 实现程度/链接 | Epic **关闭**时按事实 |
| Project Spec | 独立 issue/Explore **关闭**毕业；Epic **关闭**合并；快改真相失效；规格姿态维护 |
| Epic Spec | 规格姿态；epic 下 issue 关闭回写 |
| Issue / ff | 受管理推进；快改完成后写/关 `ff` |

出现冲突时，按 `用户最新确认 > 证据与代码 > 疑似过期的 spec` 判断。Epic 与 Vision 不一致时，先说明这是收窄实现还是修改目标，不要静默绕过。

### 完成、关闭、done 与 Git

| 状态 | 含义 |
|---|---|
| **完成** | 实现与验证达成目标 |
| **关闭** | 用户授权收尾：`o`→`x`、毕业回写；git 中可按契约 commit 相关文件 |
| **整理进 done** | 仅用户主动要求时挪已 `-x-` 项；关闭/快改/会话结束**不自动**做；`done/` 仍参与检索 |
| **Task 归档** | 每个 workflow 完成后的机械闭环；不等于关闭 Issue / Epic，也不需要二次授权 |

| 用户动作或场景 | 默认行为 |
|---|---|
| 快改 | 验证后默认写 `ff`（或直接 `x-ff`）；用户可省略 `ff`，但 Task 必须归档；不自动 commit/push |
| 受管理实现 | 完成即可；**不**自动关闭 issue；不 commit/push |
| 用户说做完/修好 | 完成验证；小改仍落 `ff`（除非不要痕迹）；常规 issue 不自动关 |
| 用户说关闭/收尾 | [close](references/close.md)；不自动进 `done/` |
| push / 部署 / 初始化或覆盖 `codestable/` / 关 epic / 破坏性操作 | **必须**明确授权 |

毕业方向：

- 独立 Issue → Project Spec。
- Epic 内 Issue → Epic Spec。
- Epic 关闭 → 将稳定结论的**具体内容**合并进 Project Spec，并检查 Vision；只链接 Epic 不算毕业回写。
- `ff` 默认不做大段毕业；若现有真相失效，则同步 spec 或明确标记漂移。

详细规则见 [close](references/close.md)。

### 质量语言

使用 ISO/IEC 25010:2023 的九个质量特征作为统一语言，但不要把它变成九项必填表。**一旦选中某项，它就是承诺。**

快改不写形式化质量清单，但仍须遵守 spec、用户要求与必要护栏。信息安全性与安全性是不同概念，不要笼统混称为“安全”。详见 [quality](references/quality.md)。

---

## 3. 开工协议

任何姿态结束 intake、准备 substantive work 时，先创建或恢复 Task；Task runtime 可按需只创建 `codestable/tasks/`，不以完整 onboard 作为前置。随后若项目已有其余 `codestable/` 内容，再做本协议（各 reference 不重复展开）：

1. **Task gate**：直接扫描文件系统；恢复匹配 active Task，或用 runtime 创建新 Task；同步 Agent 原生 Tasks。
2. **扫 `codestable/`**：路径浏览 + 关键词 grep。本会话同主题已扫且无新写入可复用。
3. **按权重深读**：`spec/`（最高）→ 相关 epic / notes → issues（含 `-x-`、`ff`、`done/`）→ 按需 talks/vision/tools。
4. **现状够用吗**：一句话触发→结果？不够 → 现状说明；跨多边界/要复用 → Explore issue。
5. **管理强度**：见上文表。管理强度只决定业务实体厚度，不影响 Task。
6. 与代码冲突：先核对证据，再改真相——不静默用代码盖掉已记录取舍，也不盲信过期文档。

有目标 Issue 时，确认正在处理的是其**当前版本**；在 Epic 下工作时，读取该 Epic 的 `spec.md`。

把 `codestable/` 当作制度记忆：遇到奇怪代码先查 Spec，踩到旧坑先查 Notes，要理解历史取舍先查 Issue。

---

## 4. 授权边界

- 方向已确认且用户要求执行 → 创建 Task 并进入无人值守，推进到**完成并归档 Task**；不在任何普通步骤、方案分叉或失败修复间反复确认。
- 确认前：讨论不落盘；设计不写代码。
- 计划确定后：禁止再次 AskQuestion；按 [计划后自治](references/autonomy.md) 自动选择推荐方向并持续执行。
- 完成 ≠ 关闭；关闭 ≠ `done/`；Task 归档 ≠ 关闭业务实体。实现/快改后只执行风险需要的 Review，**不**自动 push。
- 初始化 `codestable/`、覆盖入口、关 epic、危险操作、推送、部署：须明确授权。
- 未在计划确定前获授权的不可逆动作不纳入计划；选择非破坏性方向完成其余目标，不在执行中再次询问。

---

## 5. 按需读取的原则文件

| 文件 | 何时读取 |
|---|---|
| [task](references/task.md) / [autonomy](references/autonomy.md) | 全部姿态结束 intake 后必读；不按场景省略 |
| [quality](references/quality.md) | 具体变化的讨论/设计/实现/关闭；质量相关 bug；spec 记约束 |
| [economy](references/economy.md) | 设计/实现/修 bug 取舍；关闭时发现有界简化 |
| [code-design](references/code-design.md) | 设计/受管理实现/结构问题；**Review 必读（含文末）** |
| [ui-spec](references/ui-spec.md) | UI 空间关系、信息层级、多状态 |
| [docs](references/docs.md) | 写或重组 vision/spec/explore/notes/talk 等文档 |
| [debug](references/debug.md) | 修 bug 升级慢路径时 |

模板：`templates/entities/`（`task.md`、`issue.md`、`ff-issue.md`、explore/vision/spec/talk/notes…）。初始化：`scripts/init_codestable.py`；Task runtime：`scripts/codestable_task_runtime.py`。产物格式以各 reference 为准，勿凭文件名猜。
