---
name: cs
description: >
  CodeStable：用 Vision / Project Spec / Epic / Issue 与 codestable/ 制度记忆理解和推进软件演化；按用户当前姿态行动——讨论、快改、受管理实现、修 bug、整理愿景/规格、理解现状、关闭收尾、按需 review。
  触发：cs、CodeStable、讨论/先聊清楚、快速/快改/直接开干、穿刺、修 bug/debug、整理 vision/spec、关闭/收尾、review、这系统怎么工作，或项目已有 codestable/ 且正在处理愿景、规格、bug、实现与关闭。
---

# CodeStable

CodeStable 是一套理解和推进软件演化的方法。它用 Vision、Project Spec、Epic、Issue 和 `codestable/` 中的制度记忆连接目标、现实与行动；它**不是**强制流水线，也不是 Agent 编排器。

调用 `cs` 不等于跑完整流程。先判断用户此刻要讨论、理解、设计、实现还是收尾，再采用匹配的管理强度。

### 沟通方式：先结论，再展开

先用用户正在使用的词，简短说明**结论和原因**。只有需要做取舍、取得授权，或必须展示验证与风险证据时，才展开框架、规则和细节。简短不等于省略关键判断，而是先让用户容易理解，再按需下钻。

### 节省上下文（Codex）

同一会话中，已经完整读取且没有变化的 `SKILL.md`、reference、template 或相邻说明，必须复用既有理解，不要重复读取。仅在用户要求重读、文件已变化，或当前理解不足以支撑判断时，读取相关最小范围。

---

## 1. 先定姿态

从用户原话与上下文中选择**一个主姿态**。选定后立即读取“必读”，再开始行动；未命中的姿态文件不要预读。

| 主姿态 | 用户常这样说 | 必读 | 按需读 | 默认边界 |
|---|---|---|---|---|
| **接入** | 初始化 cs、接入 CodeStable、补齐 `codestable/` | [onboard](references/onboard.md) | — | 必须明确授权；不编造业务内容 |
| **讨论** | 聊聊、先理清、想清楚再做、帮我规划一下 | [talk](references/talk.md) | [docs](references/docs.md)；具体变化 → [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 用户确认前不落盘，不建 issue、epic 或 vision |
| **愿景** | 应用将来什么样、整理 vision、产品全景 | [vision](references/vision.md) | [docs](references/docs.md)；质量方向 → [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 确认后才写 vision；不强迫创建开发事项 |
| **规格** | 维护 spec、当前真相、epic 活规格 | [spec](references/spec.md) | [docs](references/docs.md)；质量约束 → [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 只写仍然成立的结论 |
| **理解现状** | 怎么工作的、这条链路、影响范围 | [explore](references/explore.md) | [docs](references/docs.md)；服务具体变化 → [quality](references/quality.md) | 先解释现状；复杂且值得复用时才建 Explore Issue |
| **修 bug** | 坏了、不符合预期、debug、修这个 bug | [complain](references/complain.md) | [debug](references/debug.md)、[economy](references/economy.md)、[quality](references/quality.md)；结构 → [code-design](references/code-design.md) | 简单问题默认快改并留下 `ff`；复杂问题可受管理推进 |
| **设计** | 怎么实现、先设计、实现方案 | [design](references/design.md) | [code-design](references/code-design.md)、[economy](references/economy.md)、[quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 不写代码；高风险先安排穿刺顺序 |
| **快交付** | 快速、快改、小改一下、直接开干、别走流程 | [fast](references/fast.md) | [economy](references/economy.md)；必要时 [quality](references/quality.md)；UI → [ui-spec](references/ui-spec.md) | 默认轻检索、验证并留下 `ff`；用户明确不要痕迹时才可省略 `ff` |
| **受管理实现** | 做这个 issue、推进 epic、实现（有档）、穿刺/先打通 | [do](references/do.md) | [code-design](references/code-design.md)、[economy](references/economy.md)、[quality](references/quality.md)；现状不清 → [explore](references/explore.md)；UI → [ui-spec](references/ui-spec.md) | 完成不等于关闭；风险先穿刺，再加厚 |
| **收尾** | 关闭、收尾、做完并沉淀、毕业回写 | [close](references/close.md) | [docs](references/docs.md)、[quality](references/quality.md)；有界简化 → [economy](references/economy.md) | 关闭需要用户授权；不自动移入 `done/` |
| **审代码** | review、评审、看看这 diff/PR | [code-design](references/code-design.md)（文末 Review） | [economy](references/economy.md)；相关时 → [quality](references/quality.md) | 用户点名才做；默认只审不改 |
| **记知识** | 记一下坑、写 note | [note](references/note.md) | [docs](references/docs.md) | 同主题更新原 note，不重复新建 |
| **学流程** | 我带你跑一遍、教 AI 做某流程 | [maketools](references/maketools.md) | [docs](references/docs.md) | 危险操作前再次确认 |

### 怎样判断姿态

1. 用户的原话与授权，优先于“看起来应该走重流程”。
2. 事情小、目标清楚、用户要快且没有要求建档 → **快交付**。
3. 目标模糊或取舍未定 → **讨论**；聊清后再切换到快交付、受管理实现、愿景等姿态。
4. 已有常规 Issue，或用户点名 Issue / Epic → **受管理实现**，必要时先设计。
5. 已有行为坏了 → **修 bug**；新增能力 → 快交付或受管理实现，不归入 Complain。
6. 用户只问系统怎样工作 → **理解现状**，不要默认开始修改。
7. 意图不清，而且选错会实质改变后续，例如是否建 Issue、是否改代码 → 给一句话推荐和理由，请用户选择；不要默认采用重流程。
8. 写或修改 Agent 技能本身，不属于 CodeStable 的职责。

### 选择管理强度

| 情况 | 默认选择 |
|---|---|
| 小、低风险、一次可完成，或用户明确要快 | **快改**；完成后留下 `ff`，见 [fast](references/fast.md) |
| 用户明确不要痕迹或不要写 Issue | 可以不留 `ff`；若现有真相失效，仍须同步 spec 或标记漂移 |
| 涉及范围取舍、多轮推进、交接、显著风险或长期质量承诺 | 建立**常规 Issue**：`type: feature\|bug\|chore\|refactor` |
| 跨模块、多批次，且规格会在边界内持续演化 | 建立 **Epic**；边界足够清楚的切片可直接在 Epic 内推进 |
| 技术、集成或迁移风险需要先证明可行 | 先做**穿刺**，见 [do](references/do.md)，再加厚实现 |
| 用户明确要求管理或明确不要建档 | 服从用户选择 |

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
├── vision/                         目标世界、旅程与候选方向
│   ├── index.md                    Vision 地图
│   └── ...                         按旅程或能力展开
├── spec/                           当前稳定真相
│   ├── index.md                    Project Spec 地图
│   └── ...                         按场景或能力展开
├── epics/                          有界的大变化；本树独立编号
│   ├── EEE-o|x-{Epic名}/
│   │   ├── spec.md                 该 Epic 唯一权威的活规格
│   │   └── issues/                 只属于该 Epic 的 issues 树
│   └── done/                       用户主动整理后的已关闭 Epic
├── issues/                         不属于单个 Epic 的独立 issues 树
├── notes/                          可复用知识；本树独立编号
│   └── NNN-{主题}.md
├── talks/                          尚未落定的讨论；本树独立编号
│   └── NNN-{议题}.md
└── tools/                          稳定、可重复执行的流程工具
    └── ...                         说明、脚本及其所需资源
```

根 `issues/` 与每个 Epic 内的 `issues/` 使用同一种结构，但各自独立编号：

```text
issues/
├── NNN-o|x-{事项}.md               常规 Issue
├── NNN-o|x-ff-{事项}.md            快改记录
├── NNN-o|x-{探索名}/               Explore Issue
│   ├── index.md                    认知地图、边界、结论与毕业位置
│   └── *.md                        按「触发→结果」组织的路径文章
└── done/                           可选整理区；仍参与检索和编号
```

图中的 `o|x` 表示取 `o`（open）或 `x`（closed），不是路径中的字面字符。路径表达唯一归属：只属于一个 Epic 的事项进入该 Epic 的 `issues/`，其余留在根 `issues/`。常规 Issue 与 `ff` 是单文件；只有需要独立调查工作区的 Explore Issue 使用目录。Epic 的 `issues/` 在首个所属事项创建时再建立。

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
| Vision 目标内容 | 用户确认愿景后；实现结论若要改变目标，必须再次确认 |
| Vision 实现程度与链接 | Epic 关闭时，按已经发生的事实更新 |
| Project Spec | 独立 Issue / Explore Issue 关闭毕业；Epic 关闭合并；快改使现有真相失效；或处于规格维护姿态 |
| Epic Spec | 处于规格维护姿态；或 Epic 下的 Issue 关闭回写 |
| Issue / Explore Issue / `ff` | 受管理推进时按归属写入对应 issues 树；快改完成后写入并关闭 `ff` |

出现冲突时，按 `用户最新确认 > 证据与代码 > 疑似过期的 spec` 判断。Epic 与 Vision 不一致时，先说明这是收窄实现还是修改目标，不要静默绕过。

### 完成、关闭、done 与 Git

| 状态 | 含义 |
|---|---|
| **完成** | 实现和验证已经达到目标 |
| **关闭** | 用户授权收尾：`o` → `x`，并完成毕业回写；Git 操作按关闭契约执行 |
| **整理进 `done/`** | 用户主动要求后，将已关闭事项移入整理区；这不是关闭的默认步骤 |

| 用户动作或场景 | 默认行为 |
|---|---|
| 快改 | 验证后必须写 `ff`，也可以直接写成 `x-ff`；不自动 commit 或 push |
| 受管理实现 | 推进到完成即可；不自动关闭 Issue，也不自动 commit 或 push |
| 用户说“做完”或“修好” | 完成实现与验证；小改仍留下 `ff`，除非用户明确不要痕迹；常规 Issue 不自动关闭 |
| 用户说“关闭”或“收尾” | 执行 [close](references/close.md)；不自动移入 `done/` |
| push、部署、初始化或覆盖 `codestable/`、关闭 Epic、破坏性操作 | 必须取得明确授权 |

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

在设计、实现、快改、修 bug、维护规格或穿刺之前，如果项目已有 `codestable/`，先完成以下动作。各 reference 不再重复展开这套协议。

1. **浏览路径并检索关键词。** 扫描 `codestable/` 的结构与当前主题；同一会话中已经扫描且没有新写入时，复用已有结果。
2. **按权重深入读取。** 先读 `spec/`，再读相关 Epic 与 Notes，然后递归检索根目录和各 Epic 的 issues 树，包括 `-x-`、`ff` 与 `done/`；最后按需读取 Talks、Vision 和 Tools。
3. **判断现状是否足够。** 能否用一句话说明“触发如何经过系统产生结果”？不能则先做现状说明；跨多个边界或理解值得复用时，再建立 Explore Issue。
4. **选择管理强度。** 按前文“选择管理强度”执行。
5. **处理文档与代码冲突。** 先核对证据，再修正真相；不要用代码静默覆盖已记录的取舍，也不要盲信可能过期的文档。

有目标 Issue 时，确认正在处理的是其**当前版本**；在 Epic 下工作时，读取该 Epic 的 `spec.md`。

把 `codestable/` 当作制度记忆：遇到奇怪代码先查 Spec，踩到旧坑先查 Notes，要理解历史取舍先查 Issue。

---

## 4. 授权边界

这些边界适用于所有姿态：

- 方向已经确认且用户要求执行时，持续推进到**完成**或遇到真实阻塞，不要在正常步骤之间反复确认。
- 用户确认前，讨论不落盘；设计不写代码。
- 完成不等于关闭，关闭不等于进入 `done/`。
- 实现或快改后，不自动 Review，也不自动 push。
- 初始化 `codestable/`、覆盖入口文件、关闭 Epic、危险操作、推送和部署，都必须取得明确授权。

---

## 5. 按需读取的原则文件

| 文件 | 何时读取 |
|---|---|
| [quality](references/quality.md) | 讨论、设计、实现或关闭具体变化；处理质量相关 bug；在 spec 中记录质量约束 |
| [economy](references/economy.md) | 设计、实现或修 bug 时做取舍；关闭时发现可以进行有界简化 |
| [code-design](references/code-design.md) | 设计、受管理实现或结构问题；进行 Review 时必须读取全文，包括文末 Review 部分 |
| [ui-spec](references/ui-spec.md) | 处理 UI 空间关系、信息层级与多状态 |
| [docs](references/docs.md) | 编写或重组 Vision、Spec、Explore、Note、Talk 等文档 |
| [debug](references/debug.md) | 修 bug 需要升级到慢路径时 |

实体模板位于 `templates/entities/`，包括 `issue.md`、`ff-issue.md` 以及 Explore、Vision、Spec、Talk、Note 等模板。初始化脚本是 `scripts/init_codestable.py`。产物格式以相应 reference 为准，不要只根据文件名猜测。
