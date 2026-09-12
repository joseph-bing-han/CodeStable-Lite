<div align="center">

# CodeStable

![CodeStable：从复杂工作流编排走向清晰的软件演化路径](./asset/CodeStableCover-v6.png)

[English](./README.en.md) · **中文**

**让人和 Agent 共同管理软件未知性与状态演进。**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-1-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/license-MIT-10B981?style=flat-square" alt="License"/>
</p>

</div>

---

CodeStable 是面向 AI 辅助开发的**可控软件演进框架**。它不要求人替 Agent 选择 Talk、Design 或 Do，也不要求每个需求都生成一整套 Vision、Spec、Epic 或 Issue；它帮助人和 Agent 持续判断：

- 项目现在已知什么，目标又是什么；
- 这次变化值得多强的管理；
- 还缺的是需求收束、现状理解，还是可行性证据；
- 新事实出现后，应继续、回写，还是明确转向；
- 哪些结论足够稳定，能成为下一轮工作的上下文。

它把这些判断与证据放在项目可读的 `codestable/` 工作区中，让长期项目不会只依赖某一次对话或某个 Agent 的记忆。

## 安装

使用 Skills CLI 安装当前维护的修改版：

仓库地址：[`joseph-bing-han/CodeStable-Lite`](https://github.com/joseph-bing-han/CodeStable-Lite)

```bash
npx skills add joseph-bing-han/CodeStable-Lite
```

默认安装到当前项目；希望所有项目都能使用当前修改版时加 `-g`：

```bash
npx skills add joseph-bing-han/CodeStable-Lite -g
```

本地开发时，在仓库根目录验证安装发现：

```bash
npx skills add . --list
```

更新已经安装的单一 Skill：

```bash
npx skills update cs
```

接入一个项目：

```bash
/cs 请在这个项目接入 CodeStable
```

之后始终使用同一个入口：

```bash
/cs
```

例如，你可以直接说“先聊清楚这个改动”“这条链路怎么工作”“快速修一下”“设计实现方案”“推进这个 issue”或“关闭并沉淀”。`cs` 根据当前意图选择必要的理解和行动，而不是要求你先记住一组命令。

仓库只分发 `skills/cs/` 这一个 Skill；共同契约在 `SKILL.md`，场景化规则按需位于 `references/`，模板与初始化脚本也留在同一技能包内。版本号记录在 `VERSION`，发布说明写入 `CHANGELOG.md`。

## 它解决的不是“怎样让 Agent 多跑几步”

AI 能写代码，并不等于它天然知道长期项目的当前边界、历史取舍和这次变化的真正归属。常见失败不是少了一张计划表，而是：

- 尚未形成的问题被伪装成详细任务；
- Agent 一次加载太多无关上下文，或者漏掉真正的约束；
- 代码、规格、设计历史分别存在，却没人知道哪个结论仍可作为当前依据；
- 实现中发现原设计不成立，却继续沿旧计划硬做；
- 做完的经验没有回到下一轮会读取的位置。

CodeStable 的核心对象不是 Agent 编排，而是软件自身的状态、认识和变化。它可以和任何 Agent、模型或协作方式一起使用；它负责让这些执行者面对的是一个可理解、可继续演进的项目。

## 一套判断系统，而非固定流水线

### 先判断 Question / Issue，再判断姿态并只加载需要的上下文

同一个会话中，用户可能在提问，也可能在讨论、理解现状、设计、快改、推进受管理事项或收尾沉淀。`cs` 先判断是 Question 还是 Issue；只有 Issue 才识别主姿态并读取对应的最小规则和项目材料。已经读过且未变化的内容会复用，而非重复塞进上下文。

这使用户不必判断“现在应调用哪个子技能”，也避免把尚未发生的流程提前加载。对 Agent 而言，正确上下文比更大上下文重要。

### Issue 共享同一条 Task 留痕主线，Question 不创建 Task

先区分用户是在提问（Question）还是要求推进工作（Issue）。解释、事实、定义、简单现状说明、使用建议和方案比较，若回答本身即可结束，就直接回答，不创建 Task。用户要求调查并交付、设计并落盘、修改代码或文档、修复、验证、同步 `codestable/`、推进或关闭已有实体时，才按 Issue 进入 Task 主线：

```text
用户提出问题 / 需求
  -> 分析讨论并形成结论
  -> 创建或更新相关 Issue / Spec 等前置文档
  -> 创建或恢复 Task
  -> 实施一个可观察批次
  -> 更新 Task
  -> 测试 / 必要 Review（失败则返回修改、更新 Task 与复测）
  -> 标记 completed
  -> 原子归档并确认 active 无同名残留
  -> 更新所有相关 Issue / Spec 等文档的结果、最终状态和链接
  -> 回读确认后结束
```

如果无法可靠判断 Question 还是 Issue，必须在创建 Task 前使用 AskQuestion 让用户选择；不得因为使用了 `/cs`、出现代码路径或提到技术名词，就把 Question 自动升级成 Task。Task List 是执行进度的 source of truth，Agent 自带 Todo / Tasks 只是运行时镜像；需求、方案和验收依据先保存在相关业务文档中，不能做完 Task 后才首次补建 Issue / Spec。

文档按需准备，不为小改生成整套 Vision / Epic，Project Spec 也不能把未实现目标当当前事实；维护文档本身复用目标正本，不递归建 Issue。明确禁止业务文档或纯只读 Review 时按授权处理，但已确认 Issue 的 Task 不可省略。`completed` 只是待归档态；`codestable/tasks/archived/` 正本有效、active 同名文件不存在且扫描无冲突，只证明 Task 闭环，关联业务文档的最终回写完成后整个工作流才结束。

归档文件名使用 `YYYY-MM-DD-NNN-{task}.md`。`NNN` 是同一归档日期下所有 Task 共享的三位顺序号，每天从 `001` 重新开始，并按实际归档顺序递增。

升级前若已有 `YYYY-MM-DD-{task}.md`，运行 `python3 <cs-skill>/scripts/codestable_task_runtime.py --root . migrate-archive-filenames`。同一天只有一个旧归档时可自动迁移；同一天存在多个旧归档时，runtime 不猜测历史顺序，须按已知完成顺序人工补齐序号。

Lite runtime 只允许 `tasks/active/` 与 `tasks/archived/`：create 和 archive 都用不覆盖已有证据的独占发布，scan 会把额外目录、非规范文件和 symlink 视为失败；archive 记录源快照 hash，因此成功响应丢失后可安全重放原命令。若归档后 active 路径被重建，archive 或 cleanup 只会在其内容与唯一有效 archive 正本或该正本记录的源快照完全一致时清除残留；若内容不同，则保留双方证据并 fail closed。

计划确定前可以通过结构化问题澄清目标、边界与授权，结论先写入相关文档再创建 Task。计划写入 Task 后进入无人值守：Agent 不询问普通推进，只在缺口会改变目标、正确性或权限且无法查证时提问；按契约一致性、风险、可逆性、证据强度和总成本自动选择推荐方向，处理失败，并持续到全部计划、验证、Task 归档与归档后的业务回写完成。用户中途纠正优先于旧计划；宿主能力需按实际工具 schema 核对，不能从模型名称推导。

归档前记录回写结论、目标章节与关闭改名映射；归档后回写中断时，从归档证据和业务正本继续，不复活或修改冻结 Task，也不另建一个“收尾 Task”。最终状态与实际路径在业务文档维护；回写未完成不能只凭 Task archived 宣布结束。

### 用四层世界模型定位变化

```text
Vision Spec ──摘取目标切片──> Epic Spec ──推进──> Issues（含 ff 快改痕迹）
     │                            │                    │
     │                            └──关闭毕业───────────┤
     └──目标世界                         Project Spec（当前稳定理解）
```

| 层级 | 回答的问题 | 适合承载什么 |
|---|---|---|
| Vision | 应用最终想成为怎样的世界？ | 用户旅程、能力地图、候选与互斥方向 |
| Project Spec | 项目目前哪些理解和边界仍成立？ | 当前能力、长期约束、统一语言、架构取舍 |
| Epic Spec | 这段有边界的大变化正在怎样推进？ | 活规格、当前推进、阻碍、毕业候选 |
| Issue | 这次可关闭的演进需要完成什么？ | 目标、证据、设计、实现、验证与回写 |
| Task | 这次工作怎样持续推进并恢复？ | 计划、批次进度、证据索引、完成与原子归档 |

Project Spec 是当前稳定理解的**权威入口**，不是不可质疑的绝对真理。用户的新确认优先；代码和其他证据可以证明记录已过期。遇到冲突时，先调查并修正、保留历史，或正式转向，而不是静默让任一方覆盖另一方。

### 用不同手法处理不同的未知

未知是正常状态，不应靠过早拆 Task 来假装消失。

| 不知道什么 | 优先手法 | 停止条件 |
|---|---|---|
| 真问题、边界或取舍 | Talk | 已能说清问题、边界与最大未知 |
| 当前系统怎样从触发走到结果 | 现状说明 / Explore | 已有足够行动的因果模型，未知被显式标出 |
| 未来方案能否成立 | 穿刺 | 最高风险路径已获得真实证据；不通就先处理方案 |

Design 不会把未读懂的部分写成确定结论；Do 遇到小偏差会回写，发现目标、边界或关键设计视图不成立时会停止沿旧方案继续、回到 Design，并把新的推荐方向写入 Task 后继续执行。**转向必须显式发生且可追溯。**

### 让管理强度匹配变化

| 情况 | 默认处理 |
|---|---|
| 小、明确、一次完成，或用户要求快 | 先写紧凑 `o-ff` 依据，再建 Task 实现与验证；Task 归档后回写并关为 `x-ff` |
| 有范围取舍、多轮推进、交接或显著风险 | 常规 Issue |
| 跨模块、多批推进、规格在边界内持续演化 | Epic Spec；清楚切片可在 Epic 内直接推进，也可按需开 Issue |
| 现状链路复杂、证据冲突或理解值得复用 | Explore Issue |

管理不是仪式：用户明确不要业务记录时可以不建 `ff`；用户明确要跟踪时也不因“看起来很小”而绕开 Issue。对已经确认的 Issue，Task 仍是不可豁免的运行账本。实现验证后准备稳定结论与回写位置；Task 归档后，独立 Issue 的事实同步到 Project Spec，Epic 内成果同步到 Epic Spec，并更新相关结果、推进状态及 Talk、Note、Tool 索引。常规 Issue / Epic 关闭与 Epic 毕业仍需相应授权，未授权则保留 open 并注明本轮完成/关闭就绪；`ff` 按快改规则关闭。Task 归档不等于关闭 Issue 或 Epic，也不等于移动到 `done/`。

### 把可复用的认识毕业到正确层级

Issue 不是普通待办，而是一次有明确认知起点、有限注意力范围和结束条件的软件演进事务。它把调查、设计、实现与验证放在能被审查的同一变化边界中。

实现或关闭时，过程、失败尝试和证据保留在 Issue 或 Epic 中；经过验证且仍成立的事实按归属先同步，Epic 只有在用户授权关闭后才把稳定结论“毕业”到 Project Spec：

```text
独立 Issue        → Project Spec
Epic 内 Issue      → 对应 Epic Spec
Explore Issue      → Project Spec 中的稳定现状说明
关闭 Epic          → Project Spec，并检查 Vision 的实现状态
```

Talk 记录已收束的讨论，Note 记录跨事项复用的经验，Tool 只记录已经跑通、稳定、重复且不绕过必要授权的自动化。每次相关工作结束都会检查这些出口，未达到条件时记录无新增或待验证原因。这样下一轮工作读取的是当前可用理解，而不是从历史记录中猜测什么仍有效。

## 质量如何统一

CodeStable 使用 [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) 的九项产品质量特征作为共同语言，而非认证清单。只有会改变设计或验收的质量目标才被选中；一旦选中，Design 必须响应，Do 必须提供相称证据，Close 才能确认它已达成。

## 实现如何保持经济性

实现遵循“最小充分变化”：先理解真实的触发—结果路径，再优先复用正确责任边界、删除或收窄不必要部分，最后才增加新代码。小 diff 如果落在错误归属处，不算经济。

## UI 规格如何使用图

当 UI 的空间关系、信息层级或多状态交互会影响需求理解时，Vision 或相关 Spec 使用可版本化的 ASCII 线框图、Mermaid 或其他合适图示表达关系；截图和高保真稿可以是证据，不能成为唯一规格。

## `codestable/` 工作区

接入后，项目根目录会生成下列工作区。它是人和 Agent 共同检索、维护的软件制度记忆：

```text
your-project/
└── codestable/
    ├── talks/                  # 已确认的讨论整理
    │   └── {NNN}-{name}.md
    ├── vision/                 # 目标应用世界
    │   └── index.md
    ├── spec/                   # 当前稳定理解
    │   └── index.md
    ├── epics/                  # 有界大变化
    │   └── {NNN}-o|x-{name}/
    │       └── spec.md
    ├── issues/                 # 可关闭行动、ff 与 Explore
    │   ├── {NNN}-o|x-{name}.md
    │   ├── {NNN}-o|x-ff-{name}.md
    │   └── {NNN}-o|x-{name}/   # Explore：含 index.md 与路径文章
    ├── notes/                  # 可复用知识
    │   └── {NNN}-{name}.md
    ├── tools/                  # 已跑通并稳定的流程工具
    └── tasks/                  # 已确认 Issue 的运行账本
        ├── active/{task}.md
        └── archived/YYYY-MM-DD-NNN-{task}.md
```

Task 与 Issue 使用互不外溢的命名空间：`YYYY-MM-DD-NNN-{task}.md` 只属于 `tasks/archived/`。普通 Issue 和 `ff` 必须直接以带序号的单文件放在所属 `issues/` 树下；不得按日期或 Task 另建目录，也不得在正本旁复制 `fix-note`、`report` 或 `analysis`。只有 Explore Issue 使用 `{NNN}-o|x-{name}/index.md` 目录。历史非规范目录可以检索，但不能作为新产物的命名样例。

Lite 采用单写者 Task 模型，不生成 locks、staging、tombstones 或 conflicts。runtime 通过 SHA-256 陈旧快照保护拒绝旧内容覆盖，以独占原子发布完成归档；Git 负责长期历史审计。

- `NNN` 在 issues、epics、notes、talks 各自的树内独立递增，`done/` 中的项目也参与编号计算。
- 关闭时只把路径中的 `-o-` 改为 `-x-`；名称和编号不变。
- 用户主动要求整理时，已关闭的 Issue 或 Epic 才会移入各自的 `done/`；它们仍参与检索。
- Talk 在讨论收束并准备推进或明确要求整理时落盘；Vision 的目标改写、Epic 关闭和危险操作在实际写入或执行前保留人为授权。Task 创建后，普通执行分叉不再反复确认，必要澄清与授权仍可询问。
- 旧 `.cs/` 工作区不会被静默复制。确认迁移后运行 `python skills/cs/scripts/init_codestable.py --migrate-legacy`；若 `.cs/` 与 `codestable/` 同时存在，先人工整理。

## 人始终掌握状态迁移

CodeStable 不是用文档替代工程判断，也不把计划确定前的人机澄清视为失败。Agent 可以承担检索、实现、验证、修复和回写；人保留对目标、计划边界、关闭、发布与危险操作的控制权。计划确定后，范围内的普通取舍由 Agent 无人值守完成，不再把机械下一步交还给人。

它追求的不是“让 AI 自动跑完更多步骤”，而是让软件在不断获得新事实的过程中，仍保持可理解、可验证、可控制、可演进。

## 缘起

CodeStable 起源于 [MA](https://github.com/liuzhengdongfortest/MA) 的真实开发。早期 Vibe Coding 足以支撑许多功能；当同一处问题反复出现、历史取舍无法被稳定召回时，显露出的并不是单纯的模型能力问题，而是项目缺少一套能保存当前理解、控制变化和沉淀新认识的机制。

因此它借鉴了规格、设计、探索和 Issue 的实践，但不以生成更多 artifact 为成功标准。先判断这次变化需要多少管理，再选择最小但足够的行动与记录。

## Roadmap

- [ ] 继续打磨 Vision 整理与开发切片体验
- [ ] 继续打磨直接变化、Issue、Epic 与 Explore 之间的自适应判断
- [ ] 以真实项目使用反馈校准文档、模板和行动规则

欢迎在 Issue 区分享真实的开发困境、重构经验和使用反馈。

---

## Star History
<div align="center">
MIT License · 作者 [@liuzhengdong](https://github.com/liuzhengdongfortest)
</div>
