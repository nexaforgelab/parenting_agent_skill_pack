"""Planning engine for 家庭照片整理 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        PhotoStatistics, PhotoRecord, AlbumData, TimelineEvent
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        PhotoStatistics, PhotoRecord, AlbumData, TimelineEvent
    )

SKILL_FLOW = ['读取照片文件夹', '按时间、人物、场景分类', '识别生日、旅行、节日', '自动生成成长相册', '输出年度回忆']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['分类相册', '成长时间线', '年度照片书文案']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文

    Args:
        session_id: 会话ID

    Returns:
        会话上下文对象
    """
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文

    Args:
        session_id: 会话ID
        role: 角色（user/assistant）
        content: 内容
        metadata: 额外元数据
    """
    context = get_or_create_context(session_id)
    context.add_interaction(role, content, metadata)


def analyze_photo_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析照片趋势

    Args:
        records: 照片记录列表
        days: 分析天数

    Returns:
        趋势数据列表
    """
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

    daily_counts = []
    daily_favorites = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        count = len(day_records)
        favorites = sum(1 for r in day_records if r.get("is_favorite", False))

        daily_counts.append(count)
        daily_favorites.append(favorites)
        dates.append(d.isoformat())

    if daily_counts:
        count_trend = TrendData(
            metric_name="每日照片数量",
            data_points=[float(c) for c in daily_counts],
            dates=dates
        )
        count_trend.calculate_trend()
        trends.append(count_trend)

    if daily_favorites:
        favorite_trend = TrendData(
            metric_name="每日精选数量",
            data_points=[float(f) for f in daily_favorites],
            dates=dates
        )
        favorite_trend.calculate_trend()
        trends.append(favorite_trend)

    return trends


def analyze_category_distribution(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """分析照片分类分布

    Args:
        records: 照片记录列表

    Returns:
        分类分布字典
    """
    distribution = defaultdict(int)

    for record in records:
        category = record.get("category", "other")
        distribution[category] += 1

    return dict(distribution)


def detect_photo_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测照片异常情况

    Args:
        records: 照片记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

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

    total_records = len(records)
    date_range = (max(records_by_date.keys()) - min(records_by_date.keys())).days + 1 if records_by_date else 1
    avg_per_day = total_records / date_range

    if avg_per_day > 50:
        alerts.append(Alert(
            alert_type="照片过多",
            severity="warning",
            message=f"平均每天拍摄 {avg_per_day:.1f} 张照片，可能需要整理筛选",
            recommendation="建议每天选择最有意义的照片保存，避免存储空间浪费"
        ))

    for trend in trends:
        if trend.metric_name == "每日照片数量":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -50:
                alerts.append(Alert(
                    alert_type="拍摄频率下降",
                    severity="info",
                    message=f"照片拍摄频率较之前下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="这可能是正常的生活节奏变化，继续保持记录习惯即可"
                ))

    quality_counts = Counter()
    for record in records:
        quality = record.get("quality", "good")
        quality_counts[quality] += 1

    if quality_counts.get("poor", 0) > total_records * 0.3:
        alerts.append(Alert(
            alert_type="照片质量偏低",
            severity="info",
            message=f"约 {quality_counts['poor'] / total_records * 100:.0f}% 的照片质量较低",
            recommendation="建议提高拍摄技巧或检查设备设置"
        ))

    return alerts


def generate_personalized_recommendations(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成个性化推荐

    Args:
        records: 照片记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age = child_profile.get("age", 0)
    age_months = child_profile.get("age_months", 0)

    if age_months >= 12 and age_months < 36:
        recommendations.append(Recommendation(
            category="成长记录",
            priority=1,
            title="捕捉学步期精彩瞬间",
            description=f"孩子目前{age_months}个月大，正是学步和语言快速发展的时期",
            action_items=[
                "多拍摄孩子走路的视频",
                "记录孩子学会的新词语",
                "捕捉与同龄人玩耍的场景"
            ],
            rationale="这个阶段的发展变化很快，需要及时记录",
            expected_outcome="建立完整的成长档案"
        ))

    category_dist = analyze_category_distribution(records)
    if category_dist.get("daily", 0) > category_dist.get("milestone", 0) * 3:
        recommendations.append(Recommendation(
            category="相册整理",
            priority=2,
            title="增加里程碑时刻记录",
            description="日常照片较多，但里程碑时刻记录不足",
            action_items=[
                "为每个重要时刻创建专属相册",
                "标记重要的生日、节日照片",
                "整理旅行和聚会的特别回忆"
            ],
            rationale="里程碑照片更有纪念意义",
            expected_outcome="相册结构更清晰，更有价值"
        ))

    favorite_count = sum(1 for r in records if r.get("is_favorite", False))
    if favorite_count < len(records) * 0.1:
        recommendations.append(Recommendation(
            category="照片筛选",
            priority=3,
            title="标记精选照片",
            description="精选照片较少，建议增加精选比例以便后续整理",
            action_items=[
                "回顾近期照片，选择最喜欢的",
                "为每个月份标记5-10张精选",
                "考虑创建'最佳照片集锦'"
            ],
            rationale="适度的精选有助于长期保存和分享",
            expected_outcome="建立高质量的照片精选库"
        ))

    if not alerts:
        recommendations.append(Recommendation(
            category="整理习惯",
            priority=4,
            title="保持良好的照片整理习惯",
            description="继续保持记录，有助于建立完整的成长档案",
            action_items=[
                "每周整理一次本周照片",
                "及时添加标签和描述",
                "定期备份重要照片"
            ],
            rationale="持续的整理习惯让相册更有价值",
            expected_outcome="建立井井有条的照片档案"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_photo_statistics(records: List[Dict[str, Any]], albums: List[Dict[str, Any]]) -> Optional[PhotoStatistics]:
    """聚合照片统计数据

    Args:
        records: 照片记录列表
        albums: 相册列表

    Returns:
        照片统计数据对象
    """
    if not records:
        return None

    stats = PhotoStatistics()

    stats.total_photos = len(records)

    stats.photos_by_category = analyze_category_distribution(records)

    by_year = defaultdict(int)
    by_month = defaultdict(int)

    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                ts = datetime.fromisoformat(record["timestamp"])
            elif isinstance(record.get("timestamp"), datetime):
                ts = record["timestamp"]
            else:
                continue

            by_year[ts.year] += 1
            by_month[f"{ts.year}-{ts.month:02d}"] += 1
        except (ValueError, AttributeError):
            continue

    stats.photos_by_year = dict(by_year)
    stats.photos_by_month = dict(by_month)

    stats.favorite_count = sum(1 for r in records if r.get("is_favorite", False))
    stats.albums_count = len(albums)

    photos_with_location = sum(1 for r in records if r.get("location"))
    stats.photos_with_location = photos_with_location

    photos_with_tags = sum(1 for r in records if r.get("tags"))
    stats.photos_with_tags = photos_with_tags

    if by_month:
        sorted_months = sorted(by_month.items(), key=lambda x: x[1], reverse=True)
        stats.most_active_month = sorted_months[0][0] if sorted_months else None
        stats.least_active_month = sorted_months[-1][0] if sorted_months else None

        total_months = len(by_month)
        total_photos = sum(by_month.values())
        stats.average_photos_per_month = total_photos / total_months if total_months > 0 else 0

    return stats


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表

    Args:
        payload: 输入数据

    Returns:
        事实列表
    """
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

    albums = payload.get("albums") or []
    if albums:
        facts.append(f"已收到 {len(albums)} 个相册。")

    if records:
        trends = analyze_photo_trends(records, payload.get("history_days", 7))
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
            top_str = "、".join([f"{cat}({count}张)" for cat, count in top_categories])
            facts.append(f"照片分类：{top_str}，共{total}张")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容

    Args:
        payload: 输入数据

    Returns:
        分析内容列表
    """
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})
    albums = payload.get("albums") or []

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的照片基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_photo_trends(records, history_days)
        alerts = detect_photo_anomalies(records, trends)
        stats = aggregate_photo_statistics(records, albums)

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
            analysis.append("📊 照片统计：")
            analysis.append(f"  - 总照片数：{stats.total_photos}张")
            analysis.append(f"  - 精选照片：{stats.favorite_count}张")
            analysis.append(f"  - 分类数：{len(stats.photos_by_category)}种")
            if stats.average_photos_per_month > 0:
                analysis.append(f"  - 月均拍摄：{stats.average_photos_per_month:.1f}张")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划

    Args:
        payload: 输入数据

    Returns:
        行动计划列表
    """
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "整理今天的照片",
        "为照片添加标签和分类",
        "选择精选照片",
        "创建或更新相册",
    ]

    records = payload.get("raw_records") or []
    if records:
        base_tasks.insert(0, f"分析最近 {len(records)} 条照片记录的趋势")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "照片数量、分类、完成度",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物

    Args:
        payload: 输入数据

    Returns:
        交付物字典
    """
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "照片数量", "分类", "精选", "备注"],
            "category_review": ["分类", "数量", "占比", "质量评估"]
        },
        "templates": {
            "daily_log": "今天拍了什么？有哪些值得保存的精彩瞬间？需要整理哪些照片？",
            "album_intro": "这本相册收录了[时间范围]的精彩照片，记录了[孩子名字]的成长故事。"
        }
    }

    records = payload.get("raw_records") or []
    if records:
        trends = analyze_photo_trends(records, payload.get("history_days", 7))
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
    """获取下次追踪字段

    Returns:
        字段列表
    """
    return [
        "新增照片数量",
        "照片分类完成度",
        "相册更新情况",
        "精选照片数量",
        "整理过程中遇到的问题",
        "孩子/家人反馈"
    ]


def generate_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """生成会话摘要

    Args:
        session_id: 会话ID

    Returns:
        会话摘要字典
    """
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
    """清除会话上下文

    Args:
        session_id: 会话ID

    Returns:
        是否成功清除
    """
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
