---
kind: issue
title: "恢复 Issue 扁平文件结构"
type: ff
status: closed
created: 2026-08-10
---

# 恢复 Issue 扁平文件结构

## 做了什么

明确 Task 每日归档序号只属于 `tasks/archived/`；普通 Issue 与 `ff` 继续使用所属 issues 树下的单一编号文件，只有 Explore Issue 可以使用目录。

## 改了哪些

- 同步 `SKILL.md`、Task/Fast/Complain/Explore references、四类相关模板、Agent 元数据与双语 README。
- 增加临时工作区行为测试，以普通 Issue、`ff` 和 Explore 哨兵树验证初始化及完整 Task 生命周期不会改动 `issues/` 的路径、类型或文件字节。
- 精简文案 marker 检查，仓库 checker 直接复用行为测试；`ff` 模板完整禁止 `fix-note`、`report`、`analysis` 等重复产物。
- Task runtime 与 initializer 保持不变；Task 实例模板不再承载 runtime 不会生成的全局路径政策。

## 怎么验证的

13 个 Skill 契约测试与 62 个 Task runtime 测试通过；仓库检查、Python 语法检查、`git diff --check` 和 IDE lint 均通过；两轮审查 findings 全部关闭，独立终审结论为 PASS。

## 对 `codestable/` 的影响

已同步 CodeStable 的核心实体路径契约；不自动迁移其他项目中已有的历史非规范 Issue 目录。

顺手发现：KCPortal 的 `AGENTS.md` 仍保留旧版“修 bug 必须写 fix-note”规则，是截图中重复目录继续出现的直接项目级来源；本次未跨仓库修改。
