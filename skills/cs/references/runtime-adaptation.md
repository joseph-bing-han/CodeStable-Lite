# 宿主适配

GPT-6 Astra 的模型能力不等于当前 Agent 宿主已经暴露同名工具。开始使用并行、原生 Todo、后台任务、实时引导或异步工具前，先检查当前宿主实际提供的工具 schema、返回值和生命周期；没有工具就采用串行或本地可观察替代，不能从模型名称推导工具可用，也不在 Prompt 中假装具备该能力。

## 能力映射

- **原生 Tasks / Todo**：把 Task Markdown 正本作为唯一真相，原生列表只做镜像。宿主不支持 `blocked`、依赖或恢复时，不损坏 Task 正本，也不把 pending 镜像声称为真实 blocked。
- **子代理**：只有宿主实际提供并且 schema 可用时才委派。互不依赖的调查、只读 Review、资料核对优先并行；父代理保留共享文档和 Task 的唯一写入权。后台子代理必须回收结果并核验范围、时效和证据，失败或中断不算交付。
- **异步工具调用**：只有工具声明可异步且宿主负责后台作业、结果回传和错误处理时才使用。Skill 不能把同步命令改成异步，也不能把启动成功当成业务结果。
- **中途引导**：只有宿主/API 支持在途 response steering 且能说明已完成工作与未完成副作用时才接受。新用户消息仍优先更新 Task；工具已执行的写入不会自动回滚。
- **推理强度、缓存和监控**：它们属于具体模型/API 配置，不能由 `cs` 文字启用。不存在实际配置入口时不声称已经切换 reasoning、保留缓存或启用偏离监控；监控告警不能替代授权、回滚和验证。

## 与 GPT-6 Astra 适配的提示原则

明确告诉模型何时主动推进、何时必须停在授权边界；把“普通推进不询问”和“必要澄清/授权可询问”同时写清，避免一条绝对规则压过另一条。说明用户最新消息如何覆盖受影响方向、如何判断是否委派以及小改验证的停止条件。宿主能力变化时改本文件与元数据，不把论坛文章中对行为的观察当成 API 保证。

官方依据（访问时核验，不当作本地能力证明）：

- GPT-6 Astra guidance：<https://developers.openai.com/api/docs/guides/latest-model>
- Async tool calling：<https://developers.openai.com/api/docs/guides/async-tool-calling>
- Mid-turn steering：<https://developers.openai.com/api/docs/guides/steering>
- Misalignment monitoring：<https://developers.openai.com/api/docs/guides/safety-checks/misalignment-monitoring>
