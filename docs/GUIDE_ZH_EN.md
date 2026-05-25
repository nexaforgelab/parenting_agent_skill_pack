# Parenting Agent Skill Pack Guide / 育儿 Agent Skill Pack 指南

This guide explains how to understand, run, test, and integrate the 50 parenting agent skills in this repository.

本文档说明如何理解、运行、测试和集成本仓库中的 50 个育儿类 Agent Skill。

## 1. 中文指南

### 1.1 项目定位

Parenting Agent Skill Pack 是一组面向家庭育儿、儿童学习陪伴、家庭运营和教育消费决策的 Agent Skill 模板。每个 skill 都是一个独立目录，包含技能说明、输入输出 schema、示例输入、Python runner、规划逻辑、报告生成逻辑和测试。

这套 skill 适合用于：

- 长链路 Agent 的系统技能库。
- OpenClaw、Hermes 或其他 Agent Runtime 的工具注册目录。
- 育儿产品、家庭管理产品、教育陪伴产品的原型验证。
- 对用户输入进行结构化整理、行动计划生成、风险提示和复盘字段设计。

### 1.2 重要安全边界

本项目中的 skill 只提供家庭记录、观察整理、沟通材料、行动计划和一般性建议，不提供诊断、治疗、用药、法律、财务投资或升学承诺。

对于婴幼儿健康、疫苗、过敏、发育、营养、睡眠等场景，输出必须提醒用户以当地儿科医生、公卫机构或专业人员意见为准。出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，应立即联系医生或急救服务。

### 1.3 仓库结构

```text
parenting_agent_skill_pack/
  skills/
    01_newborn_feeding_tracker/
      SKILL.md
      README.md
      manifest.json
      config/defaults.yaml
      schemas/input.schema.json
      schemas/output.schema.json
      examples/sample_input.json
      src/
        runner.py
        planner.py
        reporting.py
        models.py
        validators.py
      tests/test_runner.py
  adapters/
    hermes_tool_registry.json
    openclaw_skill_registry.yaml
  docs/
  scripts/
  catalog.json
  catalog.csv
```

关键文件说明：

| 文件 | 用途 |
|---|---|
| `SKILL.md` | 给 Agent 使用的技能说明，包含适用场景、输入要求、输出要求和安全边界。 |
| `manifest.json` | skill 的注册元数据，包括 `skill_id`、名称、分类、入口、schema 路径等。 |
| `schemas/input.schema.json` | 输入数据结构约束。 |
| `schemas/output.schema.json` | 输出数据结构约束。 |
| `examples/sample_input.json` | 可直接运行的示例输入。 |
| `src/runner.py` | skill 的 CLI 和 Python 调用入口。 |
| `src/planner.py` | 分析、行动计划、交付物和追踪字段生成逻辑。 |
| `src/reporting.py` | Markdown 报告渲染逻辑。 |
| `tests/test_runner.py` | 单个 skill 的 smoke test。 |

### 1.4 运行单个 Skill

进入任意 skill 目录后，可直接运行：

```bash
cd skills/01_newborn_feeding_tracker
python3 src/runner.py --input examples/sample_input.json --output outputs/report.json
```

如果不传 `--output`，runner 会把 JSON 输出到标准输出：

```bash
python3 src/runner.py --input examples/sample_input.json
```

Python 代码中也可以直接调用：

```python
from pathlib import Path
import importlib.util
import json

skill_dir = Path("skills/01_newborn_feeding_tracker")
runner_path = skill_dir / "src" / "runner.py"
payload = json.loads((skill_dir / "examples/sample_input.json").read_text(encoding="utf-8"))

spec = importlib.util.spec_from_file_location("runner_under_test", runner_path)
runner = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runner)

result = runner.run(payload)
print(result["markdown_report"])
```

### 1.5 全量测试

推荐在提交或集成前运行：

```bash
python3 -m compileall -q scripts skills
pytest -q
python3 scripts/validate_pack.py
python3 scripts/test_all_skills.py
python3 scripts/test_all_skills_e2e.py
python3 scripts/test_all_skills_cli_e2e.py
```

各脚本用途：

| 脚本 | 说明 |
|---|---|
| `validate_pack.py` | 使用每个 skill 的 `sample_input.json` 做基础运行校验。 |
| `test_all_skills.py` | 为每个 skill 生成 5 个泛化测试用例，覆盖空记录、多记录、边界年龄和长周期。 |
| `test_all_skills_e2e.py` | 使用真实用户问题或 skill 自带示例做端到端语义测试。 |
| `test_all_skills_cli_e2e.py` | 逐个执行 CLI 输入输出闭环，并校验输出 JSON 的必备字段。 |
| `pytest -q` | 运行每个 skill 的独立 smoke test。 |

### 1.6 输入输出契约

大多数 skill 接受以下通用输入字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `child_profile` | object | 孩子的年龄、昵称、年级、兴趣等画像信息。 |
| `family_context` | object | 照护人、可用时间、家庭背景、预算等上下文。 |
| `current_problem` | string | 当前要解决的问题。 |
| `goal` | string | 用户希望达成的目标。 |
| `raw_records` | array | 家庭记录、学习记录、消费候选项或观察数据。 |
| `preferences` | object | 语气、预算、优先级、偏好等。 |
| `history_days` | integer | 分析历史周期。 |
| `privacy_mode` | string | 隐私处理偏好。 |

通用输出字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `skill_id` | string | skill 标识。 |
| `skill_name` | string | skill 名称。 |
| `summary` | array | 摘要。 |
| `known_facts` | array | 已知事实整理。 |
| `analysis` | array | 分析结果。 |
| `action_plan` | array | 可执行行动计划。 |
| `deliverables` | object | 表格、清单、模板等交付物。 |
| `risk_notes` | array | 安全边界和风险提示。 |
| `next_tracking_fields` | array | 后续建议记录的字段。 |
| `markdown_report` | string | 面向用户的 Markdown 报告。 |

部分增强 skill 还会输出 `trends`、`alerts`、`recommendations`、`weekly_stats`、`validation_errors`、`metadata` 等字段。

### 1.7 集成建议

1. 将 `catalog.json` 作为 skill 索引入口。
2. 将每个 `manifest.json` 注册到你的 Agent Runtime。
3. 使用 `schemas/input.schema.json` 和 `schemas/output.schema.json` 做调用边界校验。
4. 将 `SKILL.md` 作为模型系统级技能说明或工具说明。
5. 将 `runner.py` 封装成工具函数、HTTP endpoint、队列任务或本地插件入口。
6. 对健康、财务、教育政策等高风险场景增加人工复核。
7. 在生产环境接入真实数据源时，对用户隐私信息做最小化采集、脱敏、授权和本地优先处理。

## 2. English Guide

### 2.1 What This Pack Is For

Parenting Agent Skill Pack is a collection of 50 modular agent skills for parenting, early learning, primary school support, family operations, school selection, educational spending, and parent wellbeing.

Each skill is self-contained and includes a skill prompt, manifest, schemas, sample input, Python runner, planning logic, reporting logic, and tests.

This pack can be used as:

- A skill library for long-running agents.
- A tool registry source for OpenClaw, Hermes, or other agent runtimes.
- A prototype foundation for parenting, family operations, or education-support products.
- A structured workflow layer that turns user context into facts, analysis, action plans, deliverables, risk notes, and follow-up tracking fields.

### 2.2 Safety Boundary

The skills provide household record keeping, observation summaries, communication support, planning assistance, and general educational guidance. They do not provide diagnosis, treatment, medication advice, legal advice, investment advice, or guaranteed admissions outcomes.

For health-adjacent topics such as infant feeding, vaccination, allergy, development, nutrition, and sleep, outputs should tell caregivers to verify with local pediatricians, public health authorities, or qualified professionals. Emergency symptoms such as breathing difficulty, persistent high fever, severe allergic reactions, abnormal mental status, dehydration, severe vomiting/diarrhea, or injury should be escalated to medical care immediately.

### 2.3 Repository Layout

```text
parenting_agent_skill_pack/
  skills/
    01_newborn_feeding_tracker/
      SKILL.md
      README.md
      manifest.json
      config/defaults.yaml
      schemas/input.schema.json
      schemas/output.schema.json
      examples/sample_input.json
      src/
        runner.py
        planner.py
        reporting.py
        models.py
        validators.py
      tests/test_runner.py
  adapters/
  docs/
  scripts/
  catalog.json
  catalog.csv
```

Key files:

| File | Purpose |
|---|---|
| `SKILL.md` | Skill instructions for agents, including scenarios, inputs, outputs, and safety limits. |
| `manifest.json` | Registry metadata such as `skill_id`, name, category, entrypoint, and schema paths. |
| `schemas/input.schema.json` | Input contract. |
| `schemas/output.schema.json` | Output contract. |
| `examples/sample_input.json` | Runnable sample payload. |
| `src/runner.py` | CLI and Python entrypoint. |
| `src/planner.py` | Facts, analysis, action plan, deliverables, and tracking-field logic. |
| `src/reporting.py` | Markdown report renderer. |
| `tests/test_runner.py` | Per-skill smoke test. |

### 2.4 Run One Skill

```bash
cd skills/01_newborn_feeding_tracker
python3 src/runner.py --input examples/sample_input.json --output outputs/report.json
```

Without `--output`, the runner prints JSON to stdout:

```bash
python3 src/runner.py --input examples/sample_input.json
```

### 2.5 Run the Full Test Suite

```bash
python3 -m compileall -q scripts skills
pytest -q
python3 scripts/validate_pack.py
python3 scripts/test_all_skills.py
python3 scripts/test_all_skills_e2e.py
python3 scripts/test_all_skills_cli_e2e.py
```

Test scripts:

| Script | Purpose |
|---|---|
| `validate_pack.py` | Runs every skill with its own sample input. |
| `test_all_skills.py` | Runs 5 generated cases per skill, including empty records, multiple records, edge ages, and longer history windows. |
| `test_all_skills_e2e.py` | Runs semantic end-to-end cases using realistic user questions or the skill's sample input. |
| `test_all_skills_cli_e2e.py` | Executes each CLI entrypoint with file input/output and validates the output JSON. |
| `pytest -q` | Runs every per-skill smoke test. |

### 2.6 Input and Output Contract

Common input fields:

| Field | Type | Description |
|---|---|---|
| `child_profile` | object | Child age, nickname, grade, interests, and profile data. |
| `family_context` | object | Caregivers, available time, family context, and budget. |
| `current_problem` | string | The current issue to solve. |
| `goal` | string | Desired outcome. |
| `raw_records` | array | Household records, learning records, candidate options, or observations. |
| `preferences` | object | Tone, budget, priorities, and other preferences. |
| `history_days` | integer | Analysis window. |
| `privacy_mode` | string | Privacy preference. |

Common output fields:

| Field | Type | Description |
|---|---|---|
| `skill_id` | string | Skill identifier. |
| `skill_name` | string | Skill name. |
| `summary` | array | High-level summary. |
| `known_facts` | array | Extracted facts. |
| `analysis` | array | Analysis. |
| `action_plan` | array | Practical next steps. |
| `deliverables` | object | Tables, checklists, templates, or other artifacts. |
| `risk_notes` | array | Safety and risk notes. |
| `next_tracking_fields` | array | Suggested fields for future tracking. |
| `markdown_report` | string | User-facing Markdown report. |

Some enhanced skills also return fields such as `trends`, `alerts`, `recommendations`, `weekly_stats`, `validation_errors`, and `metadata`.

### 2.7 Integration Recommendations

1. Use `catalog.json` as the top-level skill index.
2. Register every `manifest.json` in your agent runtime.
3. Validate tool calls with `schemas/input.schema.json` and `schemas/output.schema.json`.
4. Use each `SKILL.md` as model-facing skill or tool instructions.
5. Wrap `runner.py` as a tool function, HTTP endpoint, queue job, or local plugin.
6. Add human review for health, finance, legal, school-policy, and other high-stakes workflows.
7. Apply privacy-by-design: collect only necessary data, sanitize sensitive fields, request consent, and prefer local-first processing where possible.

## 3. Categories / 分类

| 中文分类 | English Category | Skill Range |
|---|---|---|
| 婴幼儿照护与健康记录 | Infant Care & Health Records | 01-10 |
| 启蒙教育、行为习惯与安全 | Early Learning, Habits & Safety | 11-20 |
| 小学学习陪伴 | Primary School Learning Support | 21-30 |
| 家长沟通与升学规划 | Parent Communication & Education Planning | 31-35 |
| 家庭运营与成长档案 | Family Operations & Growth Archives | 36-42 |
| 择校消费与家庭财务 | School Selection, Purchases & Family Finance | 43-48 |
| 父母情绪与家庭治理 | Parent Wellbeing & Family Governance | 49-50 |

## 4. Full Skill Catalog / 全部 Skill 清单

| # | Skill ID | Skill Name / 技能名称 | Category / 分类 |
|---:|---|---|---|
| 1 | `newborn_feeding_tracker` | 新生儿喂养记录 Agent | 婴幼儿照护与健康记录 |
| 2 | `baby_routine_builder` | 宝宝作息规律培养 Agent | 婴幼儿照护与健康记录 |
| 3 | `baby_sleep_coach` | 宝宝睡眠陪跑 Agent | 婴幼儿照护与健康记录 |
| 4 | `solid_food_planner` | 辅食添加规划 Agent | 婴幼儿照护与健康记录 |
| 5 | `baby_allergy_food_log` | 宝宝过敏食材记录 Agent | 婴幼儿照护与健康记录 |
| 6 | `development_milestone_tracker` | 月龄发育里程碑 Agent | 婴幼儿照护与健康记录 |
| 7 | `vaccination_reminder` | 疫苗接种提醒 Agent | 婴幼儿照护与健康记录 |
| 8 | `well_child_checkup_manager` | 宝宝体检记录管理 Agent | 婴幼儿照护与健康记录 |
| 9 | `baby_crying_troubleshooter` | 宝宝哭闹原因排查 Agent | 婴幼儿照护与健康记录 |
| 10 | `diaper_formula_inventory` | 尿布奶粉库存 Agent | 婴幼儿照护与健康记录 |
| 11 | `picture_book_reading` | 绘本共读 Agent | 启蒙教育、行为习惯与安全 |
| 12 | `bedtime_story_generator` | 睡前故事生成 Agent | 启蒙教育、行为习惯与安全 |
| 13 | `preschool_chinese_literacy` | 幼儿识字启蒙 Agent | 启蒙教育、行为习惯与安全 |
| 14 | `pinyin_phonics_starter` | 拼音启蒙 Agent | 启蒙教育、行为习惯与安全 |
| 15 | `preschool_english_starter` | 幼儿英语启蒙 Agent | 启蒙教育、行为习惯与安全 |
| 16 | `preschool_math_sense` | 幼儿数学启蒙 Agent | 启蒙教育、行为习惯与安全 |
| 17 | `focus_training` | 专注力训练 Agent | 启蒙教育、行为习惯与安全 |
| 18 | `toddler_emotion_labeling` | 幼儿情绪识别 Agent | 启蒙教育、行为习惯与安全 |
| 19 | `habit_builder` | 幼儿习惯养成 Agent | 启蒙教育、行为习惯与安全 |
| 20 | `child_safety_education` | 儿童安全教育 Agent | 启蒙教育、行为习惯与安全 |
| 21 | `primary_homework_companion` | 小学作业陪伴 Agent | 小学学习陪伴 |
| 22 | `primary_mistake_notebook` | 小学错题本 Agent | 小学学习陪伴 |
| 23 | `primary_math_word_problem` | 小学数学应用题 Agent | 小学学习陪伴 |
| 24 | `mental_arithmetic_trainer` | 小学口算训练 Agent | 小学学习陪伴 |
| 25 | `picture_writing_coach` | 小学看图写话 Agent | 小学学习陪伴 |
| 26 | `primary_composition_coach` | 小学作文陪练 Agent | 小学学习陪伴 |
| 27 | `primary_chinese_reading_comprehension` | 小学语文阅读理解 Agent | 小学学习陪伴 |
| 28 | `classical_poem_recitation_checker` | 古诗背诵检查 Agent | 小学学习陪伴 |
| 29 | `primary_english_vocabulary` | 小学英语单词 Agent | 小学学习陪伴 |
| 30 | `student_reading_plan` | 小学生阅读计划 Agent | 小学学习陪伴 |
| 31 | `parent_tutoring_phrases` | 家长辅导话术 Agent | 家长沟通与升学规划 |
| 32 | `parent_child_conflict_review` | 亲子冲突复盘 Agent | 家长沟通与升学规划 |
| 33 | `screen_time_management` | 手机使用管理 Agent | 家长沟通与升学规划 |
| 34 | `middle_school_exam_goal_breakdown` | 中考目标拆解 Agent | 家长沟通与升学规划 |
| 35 | `adolescent_parent_communication` | 青春期亲子沟通 Agent | 家长沟通与升学规划 |
| 36 | `family_schedule_manager` | 家庭日程管理 Agent | 家庭运营与成长档案 |
| 37 | `child_nutrition_meal_planner` | 儿童营养餐 Agent | 家庭运营与成长档案 |
| 38 | `family_grocery_list` | 家庭买菜清单 Agent | 家庭运营与成长档案 |
| 39 | `family_travel_planner` | 亲子旅行规划 Agent | 家庭运营与成长档案 |
| 40 | `weekend_family_activity` | 周末亲子活动 Agent | 家庭运营与成长档案 |
| 41 | `family_photo_organizer` | 家庭照片整理 Agent | 家庭运营与成长档案 |
| 42 | `child_growth_archive` | 儿童成长档案 Agent | 家庭运营与成长档案 |
| 43 | `kindergarten_selection` | 幼儿园择校 Agent | 择校消费与家庭财务 |
| 44 | `extracurricular_class_selection` | 兴趣班选择 Agent | 择校消费与家庭财务 |
| 45 | `after_school_class_risk_checker` | 课外班避坑 Agent | 择校消费与家庭财务 |
| 46 | `child_book_recommender` | 儿童图书推荐 Agent | 择校消费与家庭财务 |
| 47 | `child_toy_purchase_advisor` | 儿童玩具选购 Agent | 择校消费与家庭财务 |
| 48 | `family_education_budget_planner` | 家庭教育支出规划 Agent | 择校消费与家庭财务 |
| 49 | `parent_emotion_management` | 父母情绪管理 Agent | 父母情绪与家庭治理 |
| 50 | `family_meeting_facilitator` | 家庭会议主持 Agent | 父母情绪与家庭治理 |

## 5. License / 许可证

This project is licensed under the Apache License 2.0.

本项目使用 Apache License 2.0 开源许可证。
