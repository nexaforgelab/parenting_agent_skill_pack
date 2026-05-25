"""学习数据分析模块 for 小学作业陪伴 Agent.

提供高级数据分析、趋势识别和预测功能。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from .models import ProgressStats, KnowledgePoint, MistakeRecord
import statistics


class LearningAnalytics:
    """学习数据分析器"""

    def __init__(self, homework_records: List[Dict[str, Any]]):
        """初始化分析器

        Args:
            homework_records: 作业记录列表
        """
        self.records = homework_records
        self.stats = self._calculate_basic_stats()

    def _calculate_basic_stats(self) -> Dict[str, Any]:
        """计算基础统计信息"""
        if not self.records:
            return {}

        stats = {
            "total_records": len(self.records),
            "subjects": defaultdict(list),
            "daily_records": defaultdict(list),
            "weekly_records": defaultdict(int)
        }

        for record in self.records:
            subject = record.get("subject", "未知")
            stats["subjects"][subject].append(record)

            if "timestamp" in record:
                try:
                    dt = datetime.fromisoformat(record["timestamp"])
                    stats["daily_records"][dt.date()].append(record)
                    week_key = dt.isocalendar()[:2]
                    stats["weekly_records"][week_key] += 1
                except (ValueError, TypeError):
                    pass

        return stats

    def analyze_subject_performance(self) -> Dict[str, Dict[str, Any]]:
        """分析各科目表现

        Returns:
            科目表现分析字典
        """
        if not self.stats or "subjects" not in self.stats:
            return {}

        subject_analysis = {}

        for subject, records in self.stats["subjects"].items():
            if not records:
                continue

            total = len(records)
            completed = sum(1 for r in records if r.get("status") == "已完成")
            completion_rates = [r.get("completion_rate", 0) for r in records]
            durations = [r.get("duration_minutes", 0) for r in records if r.get("duration_minutes", 0) > 0]

            subject_analysis[subject] = {
                "total": total,
                "completed": completed,
                "completion_rate": sum(completion_rates) / len(completion_rates) if completion_rates else 0,
                "average_duration": sum(durations) / len(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "difficulty_distribution": self._analyze_difficulty(records)
            }

        return subject_analysis

    def _analyze_difficulty(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析难度分布

        Args:
            records: 记录列表

        Returns:
            难度分布字典
        """
        distribution = {"简单": 0, "中等": 0, "困难": 0}
        for record in records:
            difficulty = record.get("difficulty", "中等")
            if difficulty in distribution:
                distribution[difficulty] += 1
        return distribution

    def identify_learning_trends(self) -> List[Dict[str, Any]]:
        """识别学习趋势

        Returns:
            趋势分析列表
        """
        trends = []

        if not self.records:
            return trends

        sorted_records = sorted(self.records, key=lambda x: x.get("timestamp", ""))
        if len(sorted_records) < 3:
            return trends

        completion_rates = [r.get("completion_rate", 0) for r in sorted_records]

        if len(completion_rates) >= 3:
            first_half_avg = sum(completion_rates[:len(completion_rates)//2]) / (len(completion_rates)//2)
            second_half_avg = sum(completion_rates[len(completion_rates)//2:]) / (len(completion_rates) - len(completion_rates)//2)

            if second_half_avg > first_half_avg * 1.1:
                trends.append({
                    "type": "improvement",
                    "direction": "上升",
                    "magnitude": f"{(second_half_avg - first_half_avg):.1f}%",
                    "description": "学习表现呈上升趋势"
                })
            elif second_half_avg < first_half_avg * 0.9:
                trends.append({
                    "type": "decline",
                    "direction": "下降",
                    "magnitude": f"{(first_half_avg - second_half_avg):.1f}%",
                    "description": "学习表现需要关注"
                })

        durations = [r.get("duration_minutes", 0) for r in sorted_records if r.get("duration_minutes", 0) > 0]
        if len(durations) >= 3:
            first_half_avg = sum(durations[:len(durations)//2]) / (len(durations)//2)
            second_half_avg = sum(durations[len(durations)//2:]) / (len(durations) - len(durations)//2)

            if second_half_avg < first_half_avg * 0.9:
                trends.append({
                    "type": "efficiency",
                    "direction": "提升",
                    "magnitude": f"{((first_half_avg - second_half_avg) / first_half_avg * 100):.1f}%",
                    "description": "作业效率有所提升"
                })
            elif second_half_avg > first_half_avg * 1.2:
                trends.append({
                    "type": "efficiency",
                    "direction": "下降",
                    "magnitude": f"{((second_half_avg - first_half_avg) / first_half_avg * 100):.1f}%",
                    "description": "作业用时增加，需要关注"
                })

        return trends

    def detect_study_patterns(self) -> Dict[str, Any]:
        """检测学习模式

        Returns:
            学习模式分析结果
        """
        patterns = {
            "best_time": None,
            "preferred_subjects": [],
            "study_frequency": {},
            "consistency_score": 0.0
        }

        if not self.records:
            return patterns

        time_distribution = defaultdict(int)
        for record in self.records:
            if "timestamp" in record:
                try:
                    dt = datetime.fromisoformat(record["timestamp"])
                    hour = dt.hour
                    if 6 <= hour < 12:
                        time_distribution["上午"] += 1
                    elif 12 <= hour < 18:
                        time_distribution["下午"] += 1
                    elif 18 <= hour < 22:
                        time_distribution["晚上"] += 1
                except (ValueError, TypeError):
                    pass

        if time_distribution:
            patterns["best_time"] = max(time_distribution.items(), key=lambda x: x[1])[0]

        subject_completion = defaultdict(lambda: {"total": 0, "completed": 0})
        for record in self.records:
            subject = record.get("subject", "未知")
            subject_completion[subject]["total"] += 1
            if record.get("status") == "已完成":
                subject_completion[subject]["completed"] += 1

        for subject, data in subject_completion.items():
            if data["total"] > 0:
                rate = data["completed"] / data["total"]
                if rate >= 0.8:
                    patterns["preferred_subjects"].append(subject)

        patterns["study_frequency"] = dict(time_distribution)

        if "daily_records" in self.stats:
            dates = list(self.stats["daily_records"].keys())
            if len(dates) > 1:
                consistency = len(dates) / max(1, (max(dates) - min(dates)).days + 1)
                patterns["consistency_score"] = min(100, consistency * 100)

        return patterns

    def generate_insights(self) -> List[str]:
        """生成洞察建议

        Returns:
            洞察建议列表
        """
        insights = []

        subject_analysis = self.analyze_subject_performance()
        if subject_analysis:
            weak_subjects = [s for s, data in subject_analysis.items() if data["completion_rate"] < 70]
            if weak_subjects:
                insights.append(f"建议重点关注 {', '.join(weak_subjects)} 的学习，这些科目完成率较低")

            strong_subjects = [s for s, data in subject_analysis.items() if data["completion_rate"] >= 85]
            if strong_subjects:
                insights.append(f"表现优秀的科目: {', '.join(strong_subjects)}，可以考虑适当挑战更高难度")

        trends = self.identify_learning_trends()
        for trend in trends:
            insights.append(f"趋势发现: {trend['description']}，{trend['direction']}幅度 {trend['magnitude']}")

        patterns = self.detect_study_patterns()
        if patterns["best_time"]:
            insights.append(f"学习效率最高的时间段是 {patterns['best_time']}，建议在此时安排重点学习")

        if patterns["consistency_score"] < 50:
            insights.append("学习规律性较低，建议建立固定的学习时间表")

        if patterns["preferred_subjects"]:
            insights.append(f"孩子对 {', '.join(patterns['preferred_subjects'])} 有较好的掌握，可以作为学习的切入点")

        return insights


class PerformancePredictor:
    """学习表现预测器"""

    def __init__(self, historical_records: List[Dict[str, Any]]):
        """初始化预测器

        Args:
            historical_records: 历史记录列表
        """
        self.records = historical_records

    def predict_next_week_performance(self) -> Dict[str, Any]:
        """预测下周表现

        Returns:
            预测结果
        """
        if not self.records or len(self.records) < 3:
            return {
                "prediction": "数据不足",
                "confidence": 0.0,
                "expected_completion_rate": 0.0,
                "expected_daily_tasks": 0
            }

        recent_records = self.records[-7:] if len(self.records) >= 7 else self.records
        avg_completion = sum(r.get("completion_rate", 0) for r in recent_records) / len(recent_records)

        trend = self._calculate_trend()
        predicted_completion = max(0, min(100, avg_completion + trend * 3))

        daily_task_count = len(recent_records) / 7

        return {
            "prediction": "基于历史表现预测",
            "confidence": min(0.9, 0.5 + len(self.records) * 0.05),
            "expected_completion_rate": predicted_completion,
            "expected_daily_tasks": round(daily_task_count, 1),
            "trend": "上升" if trend > 0 else "下降" if trend < 0 else "稳定"
        }

    def _calculate_trend(self) -> float:
        """计算趋势

        Returns:
            趋势斜率
        """
        if len(self.records) < 2:
            return 0.0

        sorted_records = sorted(self.records, key=lambda x: x.get("timestamp", ""))
        n = len(sorted_records)
        x_vals = list(range(n))
        y_vals = [r.get("completion_rate", 0) for r in sorted_records]

        if len(set(y_vals)) == 1:
            return 0.0

        try:
            x_mean = sum(x_vals) / n
            y_mean = sum(y_vals) / n

            numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
            denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))

            if denominator == 0:
                return 0.0

            slope = numerator / denominator
            return slope
        except:
            return 0.0

    def identify_risk_factors(self) -> List[Dict[str, Any]]:
        """识别风险因素

        Returns:
            风险因素列表
        """
        risk_factors = []

        if not self.records:
            return risk_factors

        recent = self.records[-5:] if len(self.records) >= 5 else self.records

        low_completion_count = sum(1 for r in recent if r.get("completion_rate", 100) < 60)
        if low_completion_count >= len(recent) * 0.4:
            risk_factors.append({
                "factor": "持续低完成率",
                "severity": "high",
                "description": "近期有多次作业完成率较低",
                "suggestion": "需要分析原因，可能是难度过高或注意力问题"
            })

        avg_duration = sum(r.get("duration_minutes", 0) for r in recent if r.get("duration_minutes", 0) > 0)
        if avg_duration > 90:
            risk_factors.append({
                "factor": "作业用时过长",
                "severity": "medium",
                "description": "平均作业用时超过90分钟",
                "suggestion": "建议使用番茄工作法，提高专注力"
            })

        help_request_count = sum(r.get("help_requests", 0) for r in recent)
        if help_request_count > 15:
            risk_factors.append({
                "factor": "频繁请求帮助",
                "severity": "high",
                "description": "近期请求帮助次数过多",
                "suggestion": "可能存在知识盲点，建议系统复习基础知识"
            })

        distraction_count = sum(len(r.get("distractions", [])) for r in recent)
        if distraction_count > 10:
            risk_factors.append({
                "factor": "学习干扰多",
                "severity": "medium",
                "description": "学习过程中分心事件较多",
                "suggestion": "建议改善学习环境，减少干扰"
            })

        return risk_factors


def analyze_homework_effectiveness(homework_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析作业效果

    Args:
        homework_records: 作业记录列表

    Returns:
        效果分析结果
    """
    if not homework_records:
        return {"status": "no_data"}

    analytics = LearningAnalytics(homework_records)

    subject_performance = analytics.analyze_subject_performance()
    trends = analytics.identify_learning_trends()
    patterns = analytics.detect_study_patterns()
    insights = analytics.generate_insights()

    predictor = PerformancePredictor(homework_records)
    prediction = predictor.predict_next_week_performance()
    risk_factors = predictor.identify_risk_factors()

    return {
        "status": "success",
        "subject_performance": subject_performance,
        "trends": trends,
        "patterns": patterns,
        "insights": insights,
        "prediction": prediction,
        "risk_factors": risk_factors,
        "overall_score": calculate_overall_score(homework_records)
    }


def calculate_overall_score(homework_records: List[Dict[str, Any]]) -> float:
    """计算综合评分

    Args:
        homework_records: 作业记录列表

    Returns:
        综合评分 (0-100)
    """
    if not homework_records:
        return 0.0

    score = 0.0

    completion_rates = [r.get("completion_rate", 0) for r in homework_records]
    avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    score += avg_completion * 0.4

    durations = [r.get("duration_minutes", 0) for r in homework_records if r.get("duration_minutes", 0) > 0]
    if durations:
        avg_duration = sum(durations) / len(durations)
        ideal_duration = 45
        duration_score = max(0, 100 - abs(avg_duration - ideal_duration) / ideal_duration * 100)
        score += duration_score * 0.2

    completed = sum(1 for r in homework_records if r.get("status") == "已完成")
    completion_rate = completed / len(homework_records) if homework_records else 0
    score += completion_rate * 100 * 0.3

    total_help = sum(r.get("help_requests", 0) for r in homework_records)
    help_score = max(0, 100 - total_help * 5)
    score += help_score * 0.1

    return min(100, max(0, score))


def generate_learning_report(homework_records: List[Dict[str, Any]]) -> str:
    """生成学习报告

    Args:
        homework_records: 作业记录列表

    Returns:
        Markdown格式报告
    """
    analysis = analyze_homework_effectiveness(homework_records)

    lines = []
    lines.append("# 📊 学习效果分析报告")
    lines.append("")
    lines.append(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## 📈 综合评分")
    lines.append("")
    overall_score = analysis.get("overall_score", 0)
    score_grade = "优秀" if overall_score >= 85 else "良好" if overall_score >= 70 else "一般" if overall_score >= 60 else "需改进"
    lines.append(f"**评分**: {overall_score:.1f} 分 ({score_grade})")
    lines.append("")

    if "subject_performance" in analysis and analysis["subject_performance"]:
        lines.append("## 📚 科目表现")
        lines.append("")
        for subject, data in analysis["subject_performance"].items():
            lines.append(f"### {subject}")
            lines.append(f"- 完成率: {data['completion_rate']:.1f}%")
            lines.append(f"- 平均用时: {data['average_duration']:.1f}分钟")
            lines.append("")

    if "trends" in analysis and analysis["trends"]:
        lines.append("## 📉 学习趋势")
        lines.append("")
        for trend in analysis["trends"]:
            icon = "📈" if trend["direction"] in ["上升", "提升"] else "📉"
            lines.append(f"{icon} **{trend['description']}**: {trend['direction']} {trend['magnitude']}")
        lines.append("")

    if "patterns" in analysis and analysis["patterns"]:
        lines.append("## 🎯 学习模式")
        lines.append("")
        patterns = analysis["patterns"]
        if patterns["best_time"]:
            lines.append(f"- 最佳学习时段: {patterns['best_time']}")
        lines.append(f"- 学习规律性: {patterns['consistency_score']:.1f}%")
        lines.append("")

    if "insights" in analysis and analysis["insights"]:
        lines.append("## 💡 洞察建议")
        lines.append("")
        for insight in analysis["insights"]:
            lines.append(f"- {insight}")
        lines.append("")

    if "risk_factors" in analysis and analysis["risk_factors"]:
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        for risk in analysis["risk_factors"]:
            severity_icon = "🔴" if risk["severity"] == "high" else "🟡"
            lines.append(f"{severity_icon} **{risk['factor']}**: {risk['description']}")
            lines.append(f"  - 建议: {risk['suggestion']}")
        lines.append("")

    if "prediction" in analysis and analysis["prediction"]:
        lines.append("## 🔮 预测")
        lines.append("")
        pred = analysis["prediction"]
        lines.append(f"- 预期完成率: {pred['expected_completion_rate']:.1f}%")
        lines.append(f"- 预期每日任务: {pred['expected_daily_tasks']:.1f} 项")
        lines.append(f"- 趋势: {pred['trend']}")
        lines.append(f"- 预测置信度: {pred['confidence']:.0%}")
        lines.append("")

    return "\n".join(lines)
