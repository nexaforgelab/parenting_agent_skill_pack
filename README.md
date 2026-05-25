# Parenting Agent Skill Pack（50 个育儿类 Agent Skill）

本包根据用户提供的 50 个育儿 Agent 清单生成。每个 Skill 独立成文件夹，包含 `SKILL.md`、manifest、schema、Python 执行骨架、示例输入和测试。

详细的中英文使用、测试、集成指南见 [docs/GUIDE_ZH_EN.md](docs/GUIDE_ZH_EN.md)。

## 目录结构

```text
parenting_agent_skill_pack/
  skills/
    01_newborn_feeding_tracker/
      SKILL.md
      manifest.json
      config/defaults.yaml
      schemas/input.schema.json
      schemas/output.schema.json
      src/runner.py
      src/planner.py
      src/reporting.py
      src/models.py
      src/validators.py
      tests/test_runner.py
      examples/sample_input.json
  adapters/
  docs/
  scripts/
  catalog.json
```

## 运行单个 Skill

```bash
cd skills/01_newborn_feeding_tracker
python3 src/runner.py --input examples/sample_input.json --output outputs/report.json
```

## 全量验证

```bash
python3 scripts/validate_pack.py
python3 scripts/test_all_skills.py
python3 scripts/test_all_skills_e2e.py
python3 scripts/test_all_skills_cli_e2e.py
pytest -q
```

## 生产集成建议

1. 将每个 `SKILL.md` 作为长 Agent 的系统级技能说明。
2. 将 `manifest.json` 注册到 OpenClaw / Hermes 的技能目录。
3. 将 `schemas/input.schema.json` 和 `schemas/output.schema.json` 用作工具调用边界。
4. 将 `src/runner.py` 对接真实 OCR、语音识别、日历提醒、表格数据库、向量记忆和可视化图表。
5. 对健康相关 Skill 只做记录、提醒、沟通摘要，不做诊断或治疗。

## License

Apache License 2.0. See `LICENSE`.

## Skill 清单

- 01. `newborn_feeding_tracker` — 新生儿喂养记录 Agent｜婴幼儿照护与健康记录
- 02. `baby_routine_builder` — 宝宝作息规律培养 Agent｜婴幼儿照护与健康记录
- 03. `baby_sleep_coach` — 宝宝睡眠陪跑 Agent｜婴幼儿照护与健康记录
- 04. `solid_food_planner` — 辅食添加规划 Agent｜婴幼儿照护与健康记录
- 05. `baby_allergy_food_log` — 宝宝过敏食材记录 Agent｜婴幼儿照护与健康记录
- 06. `development_milestone_tracker` — 月龄发育里程碑 Agent｜婴幼儿照护与健康记录
- 07. `vaccination_reminder` — 疫苗接种提醒 Agent｜婴幼儿照护与健康记录
- 08. `well_child_checkup_manager` — 宝宝体检记录管理 Agent｜婴幼儿照护与健康记录
- 09. `baby_crying_troubleshooter` — 宝宝哭闹原因排查 Agent｜婴幼儿照护与健康记录
- 10. `diaper_formula_inventory` — 尿布奶粉库存 Agent｜婴幼儿照护与健康记录
- 11. `picture_book_reading` — 绘本共读 Agent｜启蒙教育、行为习惯与安全
- 12. `bedtime_story_generator` — 睡前故事生成 Agent｜启蒙教育、行为习惯与安全
- 13. `preschool_chinese_literacy` — 幼儿识字启蒙 Agent｜启蒙教育、行为习惯与安全
- 14. `pinyin_phonics_starter` — 拼音启蒙 Agent｜启蒙教育、行为习惯与安全
- 15. `preschool_english_starter` — 幼儿英语启蒙 Agent｜启蒙教育、行为习惯与安全
- 16. `preschool_math_sense` — 幼儿数学启蒙 Agent｜启蒙教育、行为习惯与安全
- 17. `focus_training` — 专注力训练 Agent｜启蒙教育、行为习惯与安全
- 18. `toddler_emotion_labeling` — 幼儿情绪识别 Agent｜启蒙教育、行为习惯与安全
- 19. `habit_builder` — 幼儿习惯养成 Agent｜启蒙教育、行为习惯与安全
- 20. `child_safety_education` — 儿童安全教育 Agent｜启蒙教育、行为习惯与安全
- 21. `primary_homework_companion` — 小学作业陪伴 Agent｜小学学习陪伴
- 22. `primary_mistake_notebook` — 小学错题本 Agent｜小学学习陪伴
- 23. `primary_math_word_problem` — 小学数学应用题 Agent｜小学学习陪伴
- 24. `mental_arithmetic_trainer` — 小学口算训练 Agent｜小学学习陪伴
- 25. `picture_writing_coach` — 小学看图写话 Agent｜小学学习陪伴
- 26. `primary_composition_coach` — 小学作文陪练 Agent｜小学学习陪伴
- 27. `primary_chinese_reading_comprehension` — 小学语文阅读理解 Agent｜小学学习陪伴
- 28. `classical_poem_recitation_checker` — 古诗背诵检查 Agent｜小学学习陪伴
- 29. `primary_english_vocabulary` — 小学英语单词 Agent｜小学学习陪伴
- 30. `student_reading_plan` — 小学生阅读计划 Agent｜小学学习陪伴
- 31. `parent_tutoring_phrases` — 家长辅导话术 Agent｜家长沟通与升学规划
- 32. `parent_child_conflict_review` — 亲子冲突复盘 Agent｜家长沟通与升学规划
- 33. `screen_time_management` — 手机使用管理 Agent｜家长沟通与升学规划
- 34. `middle_school_exam_goal_breakdown` — 中考目标拆解 Agent｜家长沟通与升学规划
- 35. `adolescent_parent_communication` — 青春期亲子沟通 Agent｜家长沟通与升学规划
- 36. `family_schedule_manager` — 家庭日程管理 Agent｜家庭运营与成长档案
- 37. `child_nutrition_meal_planner` — 儿童营养餐 Agent｜家庭运营与成长档案
- 38. `family_grocery_list` — 家庭买菜清单 Agent｜家庭运营与成长档案
- 39. `family_travel_planner` — 亲子旅行规划 Agent｜家庭运营与成长档案
- 40. `weekend_family_activity` — 周末亲子活动 Agent｜家庭运营与成长档案
- 41. `family_photo_organizer` — 家庭照片整理 Agent｜家庭运营与成长档案
- 42. `child_growth_archive` — 儿童成长档案 Agent｜家庭运营与成长档案
- 43. `kindergarten_selection` — 幼儿园择校 Agent｜择校消费与家庭财务
- 44. `extracurricular_class_selection` — 兴趣班选择 Agent｜择校消费与家庭财务
- 45. `after_school_class_risk_checker` — 课外班避坑 Agent｜择校消费与家庭财务
- 46. `child_book_recommender` — 儿童图书推荐 Agent｜择校消费与家庭财务
- 47. `child_toy_purchase_advisor` — 儿童玩具选购 Agent｜择校消费与家庭财务
- 48. `family_education_budget_planner` — 家庭教育支出规划 Agent｜择校消费与家庭财务
- 49. `parent_emotion_management` — 父母情绪管理 Agent｜父母情绪与家庭治理
- 50. `family_meeting_facilitator` — 家庭会议主持 Agent｜父母情绪与家庭治理
