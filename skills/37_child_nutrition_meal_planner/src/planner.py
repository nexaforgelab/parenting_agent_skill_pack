"""Planning engine for 儿童营养餐 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import TrendData, Alert, Recommendation, SessionContext, WeeklyStats
except ImportError:
    from models import TrendData, Alert, Recommendation, SessionContext, WeeklyStats

SKILL_FLOW = ['输入年龄、忌口、过敏、预算', '生成一周菜单', '自动生成买菜清单', '记录孩子接受度', '下周优化']
SAFETY_NOTES = ['本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。', '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。', '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。']
DEFAULT_DELIVERABLES = ['一周食谱', '采购清单', '营养搭配说明']

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


def analyze_meal_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析营养餐趋势"""
    trends = []
    if not records:
        return trends

    records_by_date = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
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

    daily_calories = []
    daily_proteins = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        total_cal = sum(r.get("calories", 0) or 0 for r in day_records)
        total_prot = sum(r.get("protein_g", 0) or 0 for r in day_records)
        daily_calories.append(float(total_cal))
        daily_proteins.append(total_prot)
        dates.append(d.isoformat())

    if daily_calories:
        cal_trend = TrendData(metric_name="每日总热量", data_points=daily_calories, dates=dates)
        cal_trend.calculate_trend()
        trends.append(cal_trend)

    if daily_proteins:
        prot_trend = TrendData(metric_name="每日蛋白质摄入", data_points=daily_proteins, dates=dates)
        prot_trend.calculate_trend()
        trends.append(prot_trend)

    return trends


def detect_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测营养异常"""
    alerts = []
    if not records:
        return alerts

    for trend in trends:
        if trend.metric_name == "每日总热量":
            if trend.average < 800:
                alerts.append(Alert(
                    alert_type="热量摄入偏低",
                    severity="warning",
                    message=f"平均每日热量仅为{trend.average:.0f}kcal，可能不足",
                    recommendation="建议增加主食和优质蛋白摄入，确保孩子能量充足"
                ))
            elif trend.average > 1500:
                alerts.append(Alert(
                    alert_type="热量摄入偏高",
                    severity="info",
                    message=f"平均每日热量{trend.average:.0f}kcal，需注意控制",
                    recommendation="适当减少高热量食物，增加蔬果比例"
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
    age_months = child_profile.get("age_months", 0)

    if age_months < 24:
        recommendations.append(Recommendation(
            category="辅食添加建议",
            priority=1,
            title="幼儿辅食营养重点",
            description=f"根据孩子月龄（{age_months}个月），建议注重铁质摄入和食物多样性",
            action_items=[
                "每天摄入富含铁的食物如红肉、蛋黄",
                "逐步引入不同质地的食物",
                "保持奶量在500ml左右"
            ],
            rationale="幼儿期是辅食添加关键期，营养均衡很重要",
            expected_outcome="孩子获得全面营养，健康成长"
        ))
    elif age_months < 72:
        recommendations.append(Recommendation(
            category="学龄前营养建议",
            priority=1,
            title="学龄前儿童营养重点",
            description=f"根据孩子月龄（{age_months}个月），建议保证三餐规律，减少零食",
            action_items=[
                "每天摄入至少5种蔬菜水果",
                "控制甜食和饮料摄入",
                "保证每天1小时户外活动"
            ],
            rationale="学龄前儿童需要均衡营养培养良好饮食习惯",
            expected_outcome="养成健康饮食习惯"
        ))

    if not alerts and not recommendations:
        recommendations.append(Recommendation(
            category="营养管理习惯",
            priority=3,
            title="保持良好的饮食记录习惯",
            description="当前营养摄入合理，继续坚持记录",
            action_items=["每天记录三餐饮食", "定期评估营养均衡", "根据季节调整食材"],
            rationale="持续的记录有助于发现营养问题",
            expected_outcome="建立科学的营养管理体系"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据"""
    if not records:
        return None

    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday + week_offset * 7)
    week_end = week_start + timedelta(days=6)

    week_records = []
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue
            if week_start <= record_date <= week_end:
                week_records.append(record)
        except (ValueError, AttributeError, TypeError):
            continue

    if not week_records:
        return None

    total_cal = sum(r.get("calories", 0) or 0 for r in week_records)
    total_prot = sum(r.get("protein_g", 0) or 0 for r in week_records)
    days = len(set(datetime.fromisoformat(r["timestamp"]).date() if isinstance(r.get("timestamp"), str) else r["timestamp"].date() for r in week_records if r.get("timestamp")))

    stats = WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_meals=len(week_records),
        avg_calories_per_day=total_cal / 7 if days == 0 else total_cal / days,
        avg_protein_g_per_day=total_prot / 7 if days == 0 else total_prot / days,
        variety_score=0.0
    )
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

    if records:
        trends = analyze_meal_trends(records, payload.get("history_days", 7))
        if trends:
            for trend in trends:
                facts.append(f"{trend.metric_name}：平均 {trend.average:.1f}，趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]
    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_meal_trends(records, history_days)
        alerts = detect_anomalies(records, trends)
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
    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "补齐孩子画像和营养需求",
        "记录最近一周的饮食情况",
        "根据分析结果调整食谱",
        "执行新的食谱计划并记录孩子反应",
        "一周后复盘效果并调整"
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "食物名称、摄入量、孩子反应",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "餐次", "食物", "摄入量", "孩子反应", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"]
        },
        "templates": {
            "daily_log": "今天三餐吃了什么？孩子的接受度如何？有没有过敏反应？",
            "handoff_summary": "给医生/营养师的沟通摘要：饮食习惯、已尝试食物、营养摄入情况。"
        }
    }
    records = payload.get("raw_records") or []
    if records:
        trends = analyze_meal_trends(records, payload.get("history_days", 7))
        if trends:
            deliverables["analysis_charts"] = {"trend_summary": [{"metric": t.metric_name, "average": round(t.average, 2), "trend": t.trend_direction, "change_percent": round(t.trend_percentage, 2)} for t in trends]}
    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "孩子年龄/月龄",
        "今天饮食记录",
        "孩子接受度",
        "过敏情况",
        "家长观察",
        "需要调整的食物"
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
