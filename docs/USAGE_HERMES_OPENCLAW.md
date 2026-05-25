# Hermes / OpenClaw 使用说明

## 1. 注册 Skill

- OpenClaw：参考 `adapters/openclaw_skill_registry.yaml`，把每个 `folder` 注册为一个可调用 Skill。
- Hermes：参考 `adapters/hermes_tool_registry.json`，把每个 Skill 暴露为工具或长 Agent 工作流。

## 2. 推荐调用协议

上游 Agent 接收用户自然语言后，先做路由：

1. 判断是否属于育儿、学习、家庭运营、亲子沟通或消费决策。
2. 在 `catalog.json` 中选择最匹配的 `skill_id`。
3. 读取该 Skill 的 `SKILL.md` 作为执行说明。
4. 将用户输入整理成 `schemas/input.schema.json` 兼容的 payload。
5. 调用 `src/runner.py` 或将其替换为生产 Runtime。
6. 返回结构化 JSON 与 Markdown 报告。

## 3. 长链路闭环

每个 Skill 都按以下闭环设计：

`输入采集 → 结构化 → 风险分层 → 个性化基线 → 计划生成 → 执行陪跑 → 记录沉淀 → 趋势复盘 → 动态调整 → 报告输出`

## 4. 生产增强点

- OCR：错题、体检单、合同、绘本封面、照片整理类 Skill。
- ASR：背诵检查、哭闹记录、睡前故事、家长话术类 Skill。
- 日历：疫苗、体检、家庭日程、习惯养成类 Skill。
- 数据库：成长档案、库存、预算、阅读计划、错题本类 Skill。
- 本地搜索/联网：择校、课外班、亲子旅行、周末活动、图书/玩具推荐类 Skill。
