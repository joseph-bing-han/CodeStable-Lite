<div align="center">

# CodeStable

![CodeStable: from complex workflow orchestration to a clear software evolution path](./asset/CodeStableCover-v6.png)

**English** · [中文](./README.md)

**Help people and agents manage software uncertainty and state evolution together.**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-1-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/license-MIT-10B981?style=flat-square" alt="License"/>
</p>

</div>

---

CodeStable is a **controlled software-evolution framework** for AI-assisted development. It does not make people choose Talk, Design, or Do for an agent, and it does not force every request through a Spec–Plan–Task pipeline. Instead, it helps people and agents continually judge:

- what the project knows now and what it is trying to become;
- how much management this change deserves;
- whether the missing piece is requirement convergence, current-state understanding, or feasibility evidence;
- when a new fact means continue, write back, or explicitly change course; and
- which conclusions are stable enough to become context for the next round of work.

Those judgments and their evidence live in a project-readable `codestable/` workspace, so a long-lived project does not depend on the memory of one conversation or one agent.

## Install

Install with the Skills CLI:

```bash
npx skills add codestable/CodeStable-Lite
```

Installation is project-local by default. Add `-g` to make it available across projects:

```bash
npx skills add codestable/CodeStable-Lite -g
```

For local development, verify discovery from the repository root:

```bash
npx skills add . --list
```

Onboard a project through the single entry:

```bash
/cs onboard CodeStable in this project
```

Use that same entry afterwards:

```bash
/cs
```

You can say “let's clarify this change,” “how does this path work?”, “make a quick fix,” “design the implementation,” “work on this issue,” or “close and capture the result.” `cs` selects the understanding and action that the present intent needs; you do not have to memorize a catalog of commands.

The repository distributes one Skill at `skills/cs/`. Shared contracts live in `SKILL.md`; scenario-specific rules load progressively from `references/`; templates and initialization scripts stay in the same package. The released version lives in `VERSION`, with release notes in `CHANGELOG.md`.

## It solves more than “how can agents take more steps?”

An AI that can write code does not automatically know a long-lived project's current boundaries, historical trade-offs, or the real home of a change. Typical failures are not just missing plans:

- a question that has not formed is disguised as a detailed task;
- an agent loads too much irrelevant context or misses the constraint that matters;
- code, specifications, and design history exist separately, but no one knows which conclusion still governs the present;
- implementation disproves its design but continues along the old plan; or
- completed work never returns its useful learning to where the next round will read it.

CodeStable centers the software's state, understanding, and changes—not agent orchestration. It can work with any agent, model, or collaboration style; its job is to make the project those executors face understandable and able to evolve.

## A system of judgment, not a fixed pipeline

### Identify the posture, then load only the context it needs

Within one conversation, a user may be discussing, understanding current behavior, designing, making a quick change, advancing managed work, or closing it out. `cs` identifies the primary posture first, then reads the smallest set of rules and project material for that posture. Material already read and unchanged is reused instead of being pushed into context again.

Users therefore do not need to choose a sub-skill, and the system does not load workflows that have not happened. For an agent, the right context matters more than a larger context.

### Locate change in a four-layer world model

```text
Vision Spec ──extract target slice──> Epic Spec ──advance──> Issues (including ff quick-change records)
     │                                │                           │
     │                                └──close and graduate───────┤
     └──target world                         Project Spec (current stable understanding)
```

| Layer | Question it answers | What belongs there |
|---|---|---|
| Vision | What kind of world should the application become? | User journeys, capability maps, candidate and mutually exclusive directions |
| Project Spec | Which understandings and boundaries currently hold? | Current capabilities, long-lived constraints, shared language, architectural trade-offs |
| Epic Spec | How is this bounded larger change progressing? | Living specification, current advance, blockers, graduation candidates |
| Issue | What must this closeable evolution accomplish? | Goal, evidence, design, implementation, verification, and write-back |

The Project Spec is the **authoritative entry point** for current stable understanding, not unquestionable absolute truth. A user's newest confirmation takes precedence, and code or other evidence can show that a record is stale. On conflict, investigate and correct, preserve history, or explicitly change course—never silently let one overwrite the other.

### Use different techniques for different unknowns

Unknowns are normal. They should not be hidden by splitting work into tasks too early.

| What is unknown | First technique | Stop when |
|---|---|---|
| The real problem, boundary, or trade-off | Talk | The problem, boundary, and largest unknown can be stated clearly |
| How the current system reaches a result from a trigger | Current-state explanation / Explore | A causal model is sufficient for action and remaining unknowns are explicit |
| Whether a future design can work | Spike | The highest-risk path has real evidence; if it fails, address the design first |

Design does not write unread areas as settled conclusions. Do writes back small deviations; when a goal, boundary, or key design view no longer holds, it stops and returns to Design, Talk, or a new work item. **A change of course must be explicit.**

### Match management strength to the change

| Situation | Default response |
|---|---|
| Small, clear, one-session, or explicitly urgent | Implement and verify directly; leave a compact `ff` quick-change record by default |
| Scope trade-offs, multiple rounds, handoff, or material risk | Ordinary Issue |
| Cross-module or multi-batch change with an evolving bounded specification | Epic Spec; clear slices may advance directly inside it or use Issues when useful |
| Complex current path, conflicting evidence, or understanding worth reusing | Explore Issue |

Management is not ceremony. A user can explicitly request no trace and omit `ff`; a user can also request tracking for work that looks small. Completing implementation is not closing work; closing requires user authorization, and it is not the same as moving something to `done/`.

### Graduate reusable understanding to the right layer

An Issue is not merely a to-do. It is a reviewable software-evolution transaction with a defined cognitive starting point, limited attention boundary, and end condition. It keeps investigation, design, implementation, and verification inside one change boundary.

At close, process, failed attempts, and evidence remain with the Issue or Epic. Only verified conclusions that still hold graduate:

```text
Independent Issue   → Project Spec
Issue inside Epic   → Its Epic Spec
Explore Issue      → Stable current-state explanation in Project Spec
Closed Epic        → Project Spec, then check realization state in Vision
```

The next round therefore reads usable current understanding rather than guessing what remains valid from old history.

## Quality, implementation economy, and UI

CodeStable uses the nine product-quality characteristics of [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) as a shared vocabulary, not as a certification checklist. Only objectives that change design or acceptance are selected; once selected, Design must address them, Do must provide proportionate evidence, and Close can confirm them only on that evidence.

Implementation follows a **minimum sufficient change**: understand the real trigger-to-result path, prefer reuse at the correct responsibility boundary or removing and narrowing unnecessary work, and add new code last. A small diff placed beside the symptom is not economical if it belongs elsewhere.

When spatial relationships, information hierarchy, or multi-state interaction change what a UI requirement means, Vision or the relevant Spec uses versionable ASCII wireframes, Mermaid, or another suitable diagram. Screenshots and high-fidelity designs can be evidence; they cannot be the only specification.

## The `codestable/` workspace

After onboarding, the project root contains the following workspace. It is the institutional memory that people and agents search and maintain together:

```text
your-project/
└── codestable/
    ├── talks/                  # Confirmed discussion synthesis
    │   └── {NNN}-{name}.md
    ├── vision/                 # Target application world
    │   └── index.md
    ├── spec/                   # Current stable understanding
    │   └── index.md
    ├── epics/                  # Bounded larger changes
    │   └── {NNN}-o|x-{name}/
    │       └── spec.md
    ├── issues/                 # Closeable work, ff, and Explore
    │   ├── {NNN}-o|x-{name}.md
    │   ├── {NNN}-o|x-ff-{name}.md
    │   └── {NNN}-o|x-{name}/   # Explore: index.md and path articles
    ├── notes/                  # Reusable knowledge
    │   └── {NNN}-{name}.md
    └── tools/                  # Stable tools for proven workflows
```

- `NNN` increments independently within the issues, epics, notes, and talks trees. Items under `done/` count too.
- Closing changes only `-o-` to `-x-`; the number and name remain unchanged.
- A closed Issue or Epic moves to its `done/` subdirectory only when the user explicitly requests organization; it remains searchable.
- A Talk is not written before the user confirms it. Vision target content, Epic closing, and dangerous operations also retain explicit human authorization.
- A legacy `.cs/` workspace is never silently copied. After confirming migration, run `python skills/cs/scripts/init_codestable.py --migrate-legacy`; if both `.cs/` and `codestable/` exist, reconcile them manually first.

## People retain control of state transitions

CodeStable does not replace engineering judgment with documents, and it does not treat human intervention as failure. Agents can search, implement, verify, and write back. People retain control of goals, consequential trade-offs, material costs, compatibility policy, closing, publishing, and dangerous operations.

The aim is not to make AI run more steps automatically. It is to keep software understandable, verifiable, controllable, and evolvable as it encounters new facts.

## Origin

CodeStable grew out of real development on [MA](https://github.com/liuzhengdongfortest/MA). Early vibe coding carried many features. When the same problem recurred and historical trade-offs could not be recalled reliably, the failure was not only model capability: the project lacked a way to preserve current understanding, control change, and capture new learning.

It borrows practices from specifications, design, exploration, and Issues, but does not measure success by producing more artifacts. First judge how much management the change needs; then choose the smallest action and record that are sufficient.

## Roadmap

- [ ] Continue improving Vision shaping and extraction into development slices
- [ ] Continue improving adaptive judgment among direct changes, Issues, Epics, and Explore
- [ ] Use real-project feedback to calibrate documentation, templates, and action rules

Issues and feedback from real development and refactoring work are welcome.

---

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=codestable/CodeStable-Lite&type=date&legend=top-left)](https://www.star-history.com/?repos=codestable%2FCodeStable-Lite&type=date&legend=top-left)

<div align="center">

MIT License · by [@liuzhengdong](https://github.com/liuzhengdongfortest)

</div>
