"""Planning engine for 儿童成长档案 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        ArchiveStatistics, GrowthRecord, ArchiveData
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        ArchiveStatistics, GrowthRecord, ArchiveData
    )

SKILL_FLOW = ['汇总照片、体检、学习记录、趣事', '按年龄阶段整理', '生成成长时间线', '输出月度/年度成长报告']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['成长档案', '年度报告', '纪念册文案']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文"""
    context = get_or_create_context(session_id)
    context.add_interaction(role, content, metadata)


def analyze_growth_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析成长趋势"""
    trends = []

    if not records:
        return trends

    records_by_date = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("record_date"), str):
                record_date = datetime.fromisoformat(record["record_date"]).date()
            elif isinstance(record.get("record_date"), (datetime, date)):
                record_date = record["record_date"] if isinstance(record["record_date"], date) else record["record_date"].date()
            else:
                continue
            records_by_date[record_date].append(record)
        except (ValueError, AttributeError):
            continue

    if not records_by_date:
        return trends

    sorted_dates = sorted(records_by_date.keys())
    if len(sorted_dates) > days:
        sorted_dates = sorted_dates[-days:]

    daily_counts = []
    milestone_counts = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        count = len(day_records)
        milestones = sum(1 for r in day_records if r.get("is_milestone", False))

        daily_counts.append(count)
        milestone_counts.append(milestones)
        dates.append(d.isoformat())

    if daily_counts:
        count_trend = TrendData(
            metric_name="每日记录数量",
            data_points=[float(c) for c in daily_counts],
            dates=dates
        )
        count_trend.calculate_trend()
        trends.append(count_trend)

    if milestone_counts:
        milestone_trend = TrendData(
            metric_name="每日里程碑数量",
            data_points=[float(m) for m in milestone_counts],
            dates=dates
        )
        milestone_trend.calculate_trend()
        trends.append(milestone_trend)

    return trends


def analyze_category_distribution(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """分析记录分类分布"""
    distribution = defaultdict(int)

    for record in records:
        category = record.get("category", "other")
        distribution[category] += 1

    return dict(distribution)


def detect_growth_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测成长异常情况"""
    alerts = []

    if not records:
        return alerts

    total_records = len(records)
    records_by_date = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("record_date"), str):
                record_date = datetime.fromisoformat(record["record_date"]).date()
            elif isinstance(record.get("record_date"), (datetime, date)):
                record_date = record["record_date"] if isinstance(record["record_date"], date) else record["record_date"].date()
            else:
                continue
            records_by_date[record_date].append(record)
        except (ValueError, AttributeError):
            continue

    if total_records > 0:
        date_range = (max(records_by_date.keys()) - min(records_by_date.keys())).days + 1 if records_by_date else 1
        avg_per_day = total_records / date_range

        if avg_per_day < 0.1:
            alerts.append(Alert(
                alert_type="记录频率偏低",
                severity="warning",
                message=f"平均每 {10/avg_per_day:.0f} 天才记录一次，频率偏低",
                recommendation="建议增加记录频率，保持成长档案的完整性"
            ))

    for trend in trends:
        if trend.metric_name == "每日记录数量":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -50:
                alerts.append(Alert(
                    alert_type="记录频率下降",
                    severity="info",
                    message=f"成长记录频率较之前下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="建议保持记录习惯，及时记录孩子的成长点滴"
                ))

    milestone_count = sum(1 for r in records if r.get("is_milestone", False))
    if milestone_count < total_records * 0.1:
        alerts.append(Alert(
            alert_type="里程碑记录偏少",
            severity="info",
            message=f"里程碑记录仅占 {(milestone_count/total_records)*100:.0f}%，可能遗漏重要时刻",
            recommendation="建议为孩子的重要时刻（如生日、第一次走路等）标记为里程碑"
        ))

    return alerts


def generate_personalized_recommendations(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成个性化推荐"""
    recommendations = []

    age = child_profile.get("age", 0)
    age_months = child_profile.get("age_months", 0)

    if 12 <= age_months < 36:
        recommendations.append(Recommendation(
            category="成长记录",
            priority=1,
            title="关注学步期发展",
            description=f"孩子目前{age_months}个月大，处于学步和语言发展关键期",
            action_items=[
                "记录孩子走路的进步过程",
                "记录新学会的词语和表达",
                "关注社交能力的发展"
            ],
            rationale="这个阶段的成长变化非常快，需要及时记录",
            expected_outcome="建立完整的学步期成长档案"
        ))

    category_dist = analyze_category_distribution(records)
    if category_dist.get("health", 0) < category_dist.get("learning", 0):
        recommendations.append(Recommendation(
            category="档案均衡",
            priority=2,
            title="增加健康记录",
            description="健康类记录偏少，建议增加体检、疫苗等健康记录",
            action_items=[
                "整理孩子的体检记录",
                "记录疫苗接种情况",
                "记录身高体重变化"
            ],
            rationale="健康成长是全面发展的基础",
            expected_outcome="成长档案更加全面均衡"
        ))

    milestone_count = sum(1 for r in records if r.get("is_milestone", False))
    if milestone_count < 5:
        recommendations.append(Recommendation(
            category="里程碑标记",
            priority=3,
            title="标记重要成长时刻",
            description=f"目前只有 {milestone_count} 个里程碑记录，建议增加重要时刻的标记",
            action_items=[
                "回顾孩子的成长历程",
                "标记重要的'第一次'",
                "记录生日、节日等特殊时刻"
            ],
            rationale="里程碑是成长档案最有价值的部分",
            expected_outcome="突出成长中的重要节点"
        ))

    if not alerts:
        recommendations.append(Recommendation(
            category="记录习惯",
            priority=4,
            title="保持良好的记录习惯",
            description="继续保持记录，有助于建立完整的成长档案",
            action_items=[
                "每周至少记录2-3次",
                "及时记录孩子的新表现",
                "定期整理和回顾记录"
            ],
            rationale="持续记录让档案更有价值",
            expected_outcome="建立井井有条的成长档案"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_growth_statistics(records: List[Dict[str, Any]], archives: List[Dict[str, Any]]) -> Optional[ArchiveStatistics]:
    """聚合成长统计数据"""
    if not records:
        return None

    stats = ArchiveStatistics()

    stats.total_records = len(records)

    stats.records_by_category = analyze_category_distribution(records)

    by_year = defaultdict(int)
    by_month = defaultdict(int)

    for record in records:
        try:
            if isinstance(record.get("record_date"), str):
                ts = datetime.fromisoformat(record["record_date"])
            elif isinstance(record.get("record_date"), datetime):
                ts = record["record_date"]
            else:
                continue

            by_year[ts.year] += 1
            by_month[f"{ts.year}-{ts.month:02d}"] += 1
        except (ValueError, AttributeError):
            continue

    stats.records_by_year = dict(by_year)

    stats.milestone_count = sum(1 for r in records if r.get("is_milestone", False))
    stats.archive_count = len(archives)

    records_with_attachments = sum(1 for r in records if r.get("attachments"))
    stats.records_with_attachments = records_with_attachments

    records_with_tags = sum(1 for r in records if r.get("tags"))
    stats.records_with_tags = records_with_tags

    if by_month:
        sorted_months = sorted(by_month.items(), key=lambda x: x[1], reverse=True)
        stats.most_active_month = sorted_months[0][0] if sorted_months else None

        total_months = len(by_month)
        total_records = sum(by_month.values())
        stats.average_records_per_month = total_records / total_months if total_months > 0 else 0

    return stats


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})

    if child:
        facts.append(f"孩子画像：{child}")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")

    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")

    archives = payload.get("archives") or []
    if archives:
        facts.append(f"已收到 {len(archives)} 个成长档案。")

    if records:
        trends = analyze_growth_trends(records, payload.get("history_days", 7))
        if trends:
            for trend in trends:
                facts.append(
                    f"{trend.metric_name}：平均 {trend.average:.1f}，"
                    f"趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）"
                )

        category_dist = analyze_category_distribution(records)
        if category_dist:
            total = sum(category_dist.values())
            top_categories = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            top_str = "、".join([f"{cat}({count}条)" for cat, count in top_categories])
            facts.append(f"记录分类：{top_str}，共{total}条")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})
    archives = payload.get("archives") or []

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的成长基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_growth_trends(records, history_days)
        alerts = detect_growth_anomalies(records, trends)
        stats = aggregate_growth_statistics(records, archives)

        if alerts:
            analysis.append("")
            analysis.append("⚠️ 检测到的异常：")
            for alert in alerts:
                analysis.append(f"  - [{alert.severity}] {alert.message}")

        recommendations = generate_personalized_recommendations(records, trends, child_profile, alerts)
        if recommendations:
            analysis.append("")
            analysis.append("📋 个性化建议：")
            for rec in recommendations[:3]:
                analysis.append(f"  - {rec.title}：{rec.description}")

        if stats:
            analysis.append("")
            analysis.append("📊 成长统计：")
            analysis.append(f"  - 总记录数：{stats.total_records}条")
            analysis.append(f"  - 里程碑：{stats.milestone_count}个")
            analysis.append(f"  - 分类数：{len(stats.records_by_category)}种")
            if stats.average_records_per_month > 0:
                analysis.append(f"  - 月均记录：{stats.average_records_per_month:.1f}条")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "整理最近的成长记录",
        "为记录添加分类和标签",
        "标记重要里程碑",
        "创建或更新成长档案",
    ]

    records = payload.get("raw_records") or []
    if records:
        base_tasks.insert(0, f"分析最近 {len(records)} 条成长记录的趋势")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "记录数量、分类完成度、里程碑数量",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "记录数量", "分类", "里程碑", "备注"],
            "category_review": ["分类", "数量", "占比", "质量评估"]
        },
        "templates": {
            "daily_log": "今天发生了什么？孩子有哪些新表现？有哪些值得记录的成长点滴？",
            "archive_intro": "这本档案收录了[时间范围]的成长记录，记录了[孩子名字]的成长故事。"
        }
    }

    records = payload.get("raw_records") or []
    if records:
        trends = analyze_growth_trends(records, payload.get("history_days", 7))
        if trends:
            deliverables["analysis_charts"] = {
                "trend_summary": [
                    {
                        "metric": t.metric_name,
                        "average": round(t.average, 2),
                        "trend": t.trend_direction,
                        "change_percent": round(t.trend_percentage, 2)
                    }
                    for t in trends
                ]
            }

        category_dist = analyze_category_distribution(records)
        if category_dist:
            deliverables["category_distribution"] = category_dist

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "新增记录数量",
        "记录分类完成度",
        "档案更新情况",
        "里程碑数量",
        "记录过程中遇到的问题",
        "孩子/家人反馈"
    ]


def generate_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """生成会话摘要"""
    if session_id not in _context_store:
        return None

    context = _context_store[session_id]
    return {
        "session_id": session_id,
        "created_at": context.created_at.isoformat() if isinstance(context.created_at, datetime) else context.created_at,
        "last_updated": context.last_updated.isoformat() if isinstance(context.last_updated, datetime) else context.last_updated,
        "total_interactions": len(context.conversation_history),
        "accumulated_data_keys": list(context.accumulated_data.keys())
    }


def clear_context(session_id: str) -> bool:
    """清除会话上下文"""
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
