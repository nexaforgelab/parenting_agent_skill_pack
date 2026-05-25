"""家长辅导话术 Agent - 沟通策略模块

增强版本：提供场景化沟通策略、话术组合建议、情绪应对方案
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class CommunicationScenario(Enum):
    """沟通场景枚举"""
    HOMEWORK_STRUGGLE = "homework_struggle"
    EXAM_ANXIETY = "exam_anxiety"
    RESISTANCE_TO_LEARNING = "resistance_to_learning"
    LOW_CONFIDENCE = "low_confidence"
    BOREDOM = "boredom"
    PARENT_CHILD_CONFLICT = "parent_child_conflict"
    ROUTINE_TUTORING = "routine_tutoring"
    NEW_TOPIC_INTRODUCTION = "new_topic_introduction"
    ERROR_ANALYSIS = "error_analysis"
    SESSION_WRAP_UP = "session_wrap_up"


class StrategyBuilder:
    """策略构建器"""

    @staticmethod
    def get_scenario_strategy(
        scenario: CommunicationScenario,
        child_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取场景化沟通策略

        Args:
            scenario: 沟通场景
            child_profile: 孩子画像

        Returns:
            策略字典
        """
        strategies = {
            CommunicationScenario.HOMEWORK_STRUGGLE: {
                "phase": "开始",
                "goal": "降低焦虑，建立信心",
                "opening_phrase": "这道题确实有点难度，妈妈/爸爸小时候也遇到过类似的问题。",
                "approach": [
                    "先认可孩子的努力",
                    "将难题拆分为小步骤",
                    "使用引导式提问",
                    "设置可达成的子目标"
                ],
                "recommended_categories": ["comfort", "guidance", "encouragement"],
                "warning": "避免直接给出答案，保持耐心"
            },
            CommunicationScenario.EXAM_ANXIETY: {
                "phase": "开始",
                "goal": "缓解紧张情绪",
                "opening_phrase": "考试只是检验学习的一种方式，不管结果如何，我们都为你骄傲。",
                "approach": [
                    "正常化考试焦虑",
                    "帮助孩子区分“担忧”和“准备”",
                    "回顾过去的成功经验",
                    "制定考前准备计划"
                ],
                "recommended_categories": ["comfort", "encouragement", "emotion_coaching"],
                "warning": "不要增加额外压力"
            },
            CommunicationScenario.RESISTANCE_TO_LEARNING: {
                "phase": "开始",
                "goal": "重新建立学习意愿",
                "opening_phrase": "妈妈/爸爸理解你累了，我们可以先休息5分钟再继续。",
                "approach": [
                    "承认孩子的感受",
                    "提供有限的选择",
                    "关联学习内容到生活实际",
                    "使用奖励机制（精神奖励优先）"
                ],
                "recommended_categories": ["limit_setting", "comfort", "guidance"],
                "warning": "不要强迫，但也不轻易妥协"
            },
            CommunicationScenario.LOW_CONFIDENCE: {
                "phase": "进行中",
                "goal": "建立成长型思维",
                "opening_phrase": "你上次做这道题的时候还很陌生，现在已经好多了！",
                "approach": [
                    "强调进步而非完美",
                    "展示努力与结果的关联",
                    "分享科学家的失败故事",
                    "设置略高于当前水平的挑战"
                ],
                "recommended_categories": ["encouragement", "praise", "guidance"],
                "warning": "不要使用“聪明”等固定型思维语言"
            },
            CommunicationScenario.BOREDOM: {
                "phase": "进行中",
                "goal": "增加学习趣味性",
                "opening_phrase": "我们来玩个游戏怎么样？看谁先解出这道题！",
                "approach": [
                    "引入游戏化元素",
                    "设置计时挑战",
                    "使用竞赛机制",
                    "关联兴趣领域"
                ],
                "recommended_categories": ["praise", "guidance", "limit_setting"],
                "warning": "确保游戏目标仍然是学习"
            },
            CommunicationScenario.PARENT_CHILD_CONFLICT: {
                "phase": "开始",
                "goal": "修复关系，继续学习",
                "opening_phrase": "刚才妈妈/爸爸说话的语气可能太急了，对不起。",
                "approach": [
                    "家长先道歉（如果有过激行为）",
                    "使用“我感受到...”而非“你总是...”",
                    "共同制定下次规则",
                    "简短休整后继续"
                ],
                "recommended_categories": ["comfort", "emotion_coaching", "limit_setting"],
                "warning": "必要时暂停辅导，避免关系恶化"
            },
            CommunicationScenario.ROUTINE_TUTORING: {
                "phase": "进行中",
                "goal": "保持稳定节奏",
                "opening_phrase": "今天我们继续上次的内容，先来回顾一下上次的重点。",
                "approach": [
                    "建立固定的学习流程",
                    "适时变换科目顺序",
                    "使用多样化的话术",
                    "记录每个环节的时间"
                ],
                "recommended_categories": ["guidance", "questioning", "praise"],
                "warning": "保持新鲜感，避免机械化"
            },
            CommunicationScenario.NEW_TOPIC_INTRODUCTION: {
                "phase": "开始",
                "goal": "激发好奇心",
                "opening_phrase": "今天我们要学一个很有趣的东西，你知道...吗？",
                "approach": [
                    "从生活实例引入",
                    "提出引发思考的问题",
                    "降低初学者的预期",
                    "预告这个知识的实用价值"
                ],
                "recommended_categories": ["guidance", "questioning", "encouragement"],
                "warning": "不要一次引入过多新概念"
            },
            CommunicationScenario.ERROR_ANALYSIS: {
                "phase": "进行中",
                "goal": "从错误中学习",
                "opening_phrase": "这道题做错了很有意思，说明我们发现了进步的空间！",
                "approach": [
                    "先找对的部分",
                    "引导自我发现错误",
                    "分析错误原因（粗心/概念不清/理解偏差）",
                    "总结防止类似错误的方法"
                ],
                "recommended_categories": ["error_handling", "questioning", "comfort"],
                "warning": "不要指责或惩罚错误"
            },
            CommunicationScenario.SESSION_WRAP_UP: {
                "phase": "结束",
                "goal": "总结收获，肯定进步",
                "opening_phrase": "今天我们学到了什么？来一起回顾一下吧。",
                "approach": [
                    "让孩子自己总结",
                    "强调今天的进步",
                    "预告下次内容（保持期待）",
                    "设置具体的家庭作业或练习"
                ],
                "recommended_categories": ["praise", "encouragement", "guidance"],
                "warning": "不要在结束时批评或施压"
            }
        }

        return strategies.get(scenario, {})

    @staticmethod
    def build_phrase_sequence(
        scenario: CommunicationScenario,
        session_length: int = 30
    ) -> List[Dict[str, Any]]:
        """构建话术序列

        Args:
            scenario: 沟通场景
            session_length: 预计会话时长（分钟）

        Returns:
            话术序列列表
        """
        sequence = []

        phase_templates = {
            CommunicationScenario.HOMEWORK_STRUGGLE: [
                {"timing": "0-2分钟", "category": "comfort", "action": "建立情感连接"},
                {"timing": "2-5分钟", "category": "guidance", "action": "问题拆解"},
                {"timing": "5-20分钟", "category": "questioning", "action": "引导思考"},
                {"timing": "20-25分钟", "category": "encouragement", "action": "巩固信心"},
                {"timing": "25-30分钟", "category": "praise", "action": "总结肯定"}
            ],
            CommunicationScenario.SESSION_WRAP_UP: [
                {"timing": "0-5分钟", "category": "questioning", "action": "引导回顾"},
                {"timing": "5-10分钟", "category": "praise", "action": "肯定进步"},
                {"timing": "10-15分钟", "category": "guidance", "action": "布置任务"}
            ]
        }

        return phase_templates.get(scenario, [])

    @staticmethod
    def combine_phrases_for_effect(
        categories: List[str],
        child_profile: Dict[str, Any]
    ) -> List[str]:
        """组合话术以增强效果

        Args:
            categories: 话术类别列表
            child_profile: 孩子画像

        Returns:
            组合话术列表
        """
        combined = []

        if "comfort" in categories and "encouragement" in categories:
            combined.append("共情+鼓励组合：先认可感受，再肯定努力")

        if "guidance" in categories and "questioning" in categories:
            combined.append("引导+提问组合：用问题引导思考方向")

        if "praise" in categories and "encouragement" in categories:
            combined.append("表扬+鼓励组合：强化正面行为")

        if "emotion_coaching" in categories and "comfort" in categories:
            combined.append("情绪引导+安慰：先处理情绪再处理任务")

        return combined


class EmotionResponseManager:
    """情绪响应管理器"""

    EMOTION_KEYWORDS = {
        "frustrated": ["不会", "太难了", "不想做", "烦"],
        "anxious": ["害怕", "担心", "紧张", "考不好"],
        "bored": ["无聊", "没意思", "不想学", "困"],
        "resistant": ["不要", "偏不", "就是不想", "强迫"],
        "confident": ["我会", "太简单了", "没问题", "容易"]
    }

    @staticmethod
    def detect_emotion_from_text(text: str) -> Dict[str, float]:
        """从文本检测情绪

        Args:
            text: 输入文本

        Returns:
            情绪及其置信度字典
        """
        text_lower = text.lower()
        scores = {}

        for emotion, keywords in EmotionResponseManager.EMOTION_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                scores[emotion] = min(count / len(keywords) * 100, 100)

        return scores

    @staticmethod
    def get_emotion_response_sequence(
        detected_emotion: str
    ) -> List[Dict[str, str]]:
        """获取情绪响应序列

        Args:
            detected_emotion: 检测到的情绪

        Returns:
            响应序列
        """
        responses = {
            "frustrated": [
                {"step": 1, "action": "暂停任务", "phrase": "我们先停一下，深呼吸。" },
                {"step": 2, "action": "共情", "phrase": "我能感觉到你很沮丧。" },
                {"step": 3, "action": "降低难度", "phrase": "我们来做一个更简单的。" },
                {"step": 4, "action": "重新开始", "phrase": "准备好了吗？我们再试一次。" }
            ],
            "anxious": [
                {"step": 1, "action": "正常化", "phrase": "紧张是正常的，说明你在乎。" },
                {"step": 2, "action": "分享经验", "phrase": "妈妈/爸爸考试前也会紧张。" },
                {"step": 3, "action": "聚焦当下", "phrase": "我们只看眼前的这道题。" },
                {"step": 4, "action": "建立信心", "phrase": "你已经准备得很充分了。" }
            ],
            "bored": [
                {"step": 1, "action": "引入变化", "phrase": "我们来换个方式试试。" },
                {"step": 2, "action": "增加互动", "phrase": "你来当小老师怎么样？" },
                {"step": 3, "action": "设置挑战", "phrase": "试试能不能在5分钟内完成。" },
                {"step": 4, "action": "提供选择", "phrase": "你想先做哪一科？" }
            ],
            "resistant": [
                {"step": 1, "action": "给予空间", "phrase": "好的，我们等一下再开始。" },
                {"step": 2, "action": "解释原因", "phrase": "我理解你的感受，但完成作业后我们可以..." },
                {"step": 3, "action": "提供选择", "phrase": "你想先休息5分钟还是先做作业？" },
                {"step": 4, "action": "坚守底线", "phrase": "作业是必须完成的，我们可以选择怎么完成。" }
            ]
        }

        return responses.get(detected_emotion, [])


class PhraseTemplateEngine:
    """话术模板引擎"""

    @staticmethod
    def fill_template(
        template: str,
        context: Dict[str, Any]
    ) -> str:
        """填充话术模板

        Args:
            template: 模板字符串
            context: 上下文数据

        Returns:
            填充后的话术
        """
        result = template

        placeholders = {
            "{child_name}": context.get("child_name", "孩子"),
            "{subject}": context.get("subject", "这门课"),
            "{topic}": context.get("topic", "这个内容"),
            "{time}": context.get("time", "现在"),
            "{goal}": context.get("goal", "目标")
        }

        for placeholder, value in placeholders.items():
            result = result.replace(placeholder, value)

        return result

    @staticmethod
    def generate_customized_phrase(
        category: str,
        child_profile: Dict[str, Any],
        situation: Dict[str, Any]
    ) -> str:
        """生成定制化话术

        Args:
            category: 话术类别
            child_profile: 孩子画像
            situation: 当前情境

        Returns:
            定制化话术
        """
        templates = {
            "encouragement": [
                "你已经比之前进步很多了，继续加油！",
                "妈妈/爸爸看到你很努力，这很重要。",
                "遇到困难是正常的，你正在变得更强。"
            ],
            "guidance": [
                "让我们一起来看看这道题。",
                "你能告诉妈妈/爸爸，这道题在问什么吗？",
                "如果把这个问题拆成小部分，会更容易。"
            ],
            "comfort": [
                "没关系，我们慢慢来。",
                "妈妈/爸爸理解你的感受。",
                "错了也没关系，这是在学习。"
            ]
        }

        age = child_profile.get("age", 10)
        phrases = templates.get(category, [])

        if age < 10:
            return phrases[0] if phrases else ""
        else:
            return phrases[-1] if phrases else ""


def adapt_phrase_for_child(
    phrase: str,
    child_profile: Dict[str, Any]
) -> str:
    """根据孩子特点调整话术

    Args:
        phrase: 原始话术
        child_profile: 孩子画像

    Returns:
        调整后的话术
    """
    age = child_profile.get("age", 10)
    interests = child_profile.get("interests", [])

    if age < 8:
        phrase = phrase.replace("妈妈/爸爸", "妈妈")
        if len(phrase) > 30:
            phrase = phrase[:30] + "哦。"

    if interests:
        if "游戏" in interests and "游戏" not in phrase:
            phrase = phrase.replace("，", "，就像玩游戏一样，")

    return phrase
