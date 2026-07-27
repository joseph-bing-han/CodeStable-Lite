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

CodeStable 是面向 AI 辅助开发的**可控软件演进框架**。它不要求人替 Agent 选择 Talk、Design 或 Do，也不要求每个需求都经过一套 Spec–Plan–Task 流水线；它帮助人和 Agent 持续判断：

- 项目现在已知什么，目标又是什么；
- 这次变化值得多强的管理；
- 还缺的是需求收束、现状理解，还是可行性证据；
- 新事实出现后，应继续、回写，还是明确转向；
- 哪些结论足够稳定，能成为下一轮工作的上下文。

它把这些判断与证据放在项目可读的 `codestable/` 工作区中，让长期项目不会只依赖某一次对话或某个 Agent 的记忆。

## 安装

使用 Skills CLI 安装：

```bash
npx skills add codestable/CodeStable-Lite
```

默认安装到当前项目；希望所有项目都能使用时加 `-g`：

```bash
npx skills add codestable/CodeStable-Lite -g
```

本地开发时，在仓库根目录验证安装发现：

```bash
npx skills add . --list
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

### 先判断姿态，再只加载需要的上下文

同一个会话中，用户可能在讨论、理解现状、设计、快改、推进受管理事项，或收尾沉淀。`cs` 先识别此刻的主姿态，再读取对应的最小规则和项目材料；已经读过且未变化的内容会复用，而非重复塞进上下文。

这使用户不必判断“现在应调用哪个子技能”，也避免把尚未发生的流程提前加载。对 Agent 而言，正确上下文比更大上下文重要。

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

Project Spec 是当前稳定理解的**权威入口**，不是不可质疑的绝对真理。用户的新确认优先；代码和其他证据可以证明记录已过期。遇到冲突时，先调查并修正、保留历史，或正式转向，而不是静默让任一方覆盖另一方。

### 用不同手法处理不同的未知

未知是正常状态，不应靠过早拆 Task 来假装消失。

| 不知道什么 | 优先手法 | 停止条件 |
|---|---|---|
| 真问题、边界或取舍 | Talk | 已能说清问题、边界与最大未知 |
| 当前系统怎样从触发走到结果 | 现状说明 / Explore | 已有足够行动的因果模型，未知被显式标出 |
| 未来方案能否成立 | 穿刺 | 最高风险路径已获得真实证据；不通就先处理方案 |

Design 不会把未读懂的部分写成确定结论；Do 遇到小偏差会回写，发现目标、边界或关键设计视图不成立时则停止并回到 Design、Talk 或新的事项。**转向必须显式发生。**

### 让管理强度匹配变化

| 情况 | 默认处理 |
|---|---|
| 小、明确、一次完成，或用户要求快 | 直接实现与验证；默认留下紧凑的 `ff` 快改记录 |
| 有范围取舍、多轮推进、交接或显著风险 | 常规 Issue |
| 跨模块、多批推进、规格在边界内持续演化 | Epic Spec；清楚切片可在 Epic 内直接推进，也可按需开 Issue |
| 现状链路复杂、证据冲突或理解值得复用 | Explore Issue |

管理不是仪式：用户明确不要留痕时可以不建 `ff`；用户明确要跟踪时也不因“看起来很小”而绕开 Issue。完成实现不等于关闭；关闭需要用户授权，也不等于移动到 `done/`。

### 把可复用的认识毕业到正确层级

Issue 不是普通待办，而是一次有明确认知起点、有限注意力范围和结束条件的软件演进事务。它把调查、设计、实现与验证放在能被审查的同一变化边界中。

关闭时，过程、失败尝试和证据保留在 Issue 或 Epic 中；只有经过验证且仍成立的结论才“毕业”：

```text
独立 Issue        → Project Spec
Epic 内 Issue      → 对应 Epic Spec
Explore Issue      → Project Spec 中的稳定现状说明
关闭 Epic          → Project Spec，并检查 Vision 的实现状态
```

这样下一轮工作读取的是当前可用理解，而不是从历史记录中猜测什么仍有效。

## 质量、实现经济性与 UI

CodeStable 使用 [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) 的九项产品质量特征作为共同语言，而非认证清单。只有会改变设计或验收的质量目标才被选中；一旦选中，Design 必须响应，Do 必须提供相称证据，Close 才能确认它已达成。

实现遵循“最小充分变化”：先理解真实的触发—结果路径，再优先复用正确责任边界、删除或收窄不必要部分，最后才增加新代码。小 diff 如果落在错误归属处，不算经济。

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
    └── tools/                  # 已跑通并稳定的流程工具
```

- `NNN` 在 issues、epics、notes、talks 各自的树内独立递增，`done/` 中的项目也参与编号计算。
- 关闭时只把路径中的 `-o-` 改为 `-x-`；名称和编号不变。
- 用户主动要求整理时，已关闭的 Issue 或 Epic 才会移入各自的 `done/`；它们仍参与检索。
- Talk 在用户确认前不落盘；Vision 的目标内容、Epic 关闭和危险操作也都保留人为授权。
- 旧 `.cs/` 工作区不会被静默复制。确认迁移后运行 `python skills/cs/scripts/init_codestable.py --migrate-legacy`；若 `.cs/` 与 `codestable/` 同时存在，先人工整理。

## 人始终掌握状态迁移

CodeStable 不是用文档替代工程判断，也不把人介入视为失败。Agent 可以承担检索、实现、验证和回写；人保留对目标、重要取舍、显著成本、兼容策略、关闭、发布与危险操作的控制权。

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

[![Star History Chart](https://api.star-history.com/chart?repos=codestable/CodeStable-Lite&type=date&legend=top-left)](https://www.star-history.com/?repos=codestable%2FCodeStable-Lite&type=date&legend=top-left)

<div align="center">

MIT License · 作者 [@liuzhengdong](https://github.com/liuzhengdongfortest)

</div>
