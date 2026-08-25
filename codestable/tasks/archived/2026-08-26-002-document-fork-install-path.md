---
doc_type: task-list
task: document-fork-install-path
goal: 将公开安装说明统一指向当前修改版 CodeStable-Lite 仓库
status: archived
workflow: fast
owner_skill: cs
created: 2026-08-26
updated: 2026-08-26
archived: 2026-08-26
related_docs:
  - README.md
  - README.en.md
  - tools/check-skill-repository.py
  - tests/test_skill_contracts.py
---

# 将公开安装说明统一指向当前修改版 CodeStable-Lite 仓库

## 1. 任务目标

将公开安装说明统一指向当前修改版 CodeStable-Lite 仓库

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 更新中英文 README 的安装命令与仓库说明，明确使用 joseph-bing-han/CodeStable-Lite 修改版
- [x] 同步仓库检查器与契约测试，防止 README 回退到原版安装路径
- [x] 运行文档、测试、编译与 Task scan 验证并记录结果

## 4. CodeStable 文档索引

- `README.md`
- `README.en.md`
- `tools/check-skill-repository.py`
- `tests/test_skill_contracts.py`

## 5. 执行步骤

### 1. 更新中英文 README 的安装命令与仓库说明，明确使用 joseph-bing-han/CodeStable-Lite 修改版

- 状态：done

### 2. 同步仓库检查器与契约测试，防止 README 回退到原版安装路径

- 状态：done

### 3. 运行文档、测试、编译与 Task scan 验证并记录结果

- 状态：done

## 6. 中断恢复提示

从第一个未完成步骤继续，并先以 Task 正本恢复 Agent 原生 Tasks。计划确定后按 references/autonomy.md 自动择优，不再请求路线确认。

## 7. 完成与归档记录

2026-08-26：Task 已创建。

2026-08-26：完成第一批：已更新中英文 README、仓库检查器、契约测试和 Unreleased 说明，安装入口统一指向当前维护的修改版仓库。

2026-08-26：完成第一、二步：中英文 README 已明确指向当前维护修改版；仓库检查器与契约测试已拒绝原版安装命令。

2026-08-26：根据独立复核补强防回退检查：仓库检查器和契约测试现在分别精确校验项目级、全局安装命令及完整修改版仓库 URL。

2026-08-26：完成第三步：78 项测试通过，仓库契约检查通过，Python 编译通过，IDE lint 无诊断，git diff --check 通过。

2026-08-26：Task 已标记 completed，等待归档。

2026-08-26：Task 已原子移动到 archived，active 正本已移除。 源快照 SHA-256：15bd7f87561fbb7a841b04ccdd609508c9d20635bdd4765326e1ef12e2097f2c
