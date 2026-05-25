"""Progress tracking module for 绘本共读 Agent.

提供学习进度追踪功能，包括里程碑管理、成就系统和进度报告。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid


class Milestone:
    """学习里程碑类"""
    def __init__(
        self,
        milestone_id: str,
        title: str,
        description: str,
        target_value: int,
        current_value: int = 0,
        milestone_type: str = "sessions",
        awarded_at: Optional[str] = None
    ):
        self.milestone_id = milestone_id
        self.title = title
        self.description = description
        self.target_value = target_value
        self.current_value = current_value
        self.milestone_type = milestone_type
        self.awarded_at = awarded_at

    def is_achieved(self) -> bool:
        """检查里程碑是否达成"""
        return self.current_value >= self.target_value

    def progress_percentage(self) -> float:
        """计算进度百分比"""
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "milestone_id": self.milestone_id,
            "title": self.title,
            "description": self.description,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "milestone_type": self.milestone_type,
            "progress_percentage": self.progress_percentage(),
            "is_achieved": self.is_achieved(),
            "awarded_at": self.awarded_at
        }


class Achievement:
    """成就类"""
    def __init__(
        self,
        achievement_id: str,
        name: str,
        description: str,
        icon: str = "🏆",
        points: int = 10,
        unlocked_at: Optional[str] = None
    ):
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.icon = icon
        self.points = points
        self.unlocked_at = unlocked_at

    def is_unlocked(self) -> bool:
        """检查成就是否解锁"""
        return self.unlocked_at is not None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "points": self.points,
            "unlocked_at": self.unlocked_at,
            "is_unlocked": self.is_unlocked()
        }


def create_default_milestones() -> List[Milestone]:
    """创建默认里程碑列表

    Returns:
        默认里程碑列表
    """
    return [
        Milestone("first_session", "初次尝试", "完成第一次绘本共读", 1, 0, "sessions"),
        Milestone("week_streak", "一周坚持", "连续学习7天", 7, 0, "streak"),
        Milestone("month_streak", "一月坚持", "连续学习30天", 30, 0, "streak"),
        Milestone("ten_sessions", "十次学习", "累计完成10次学习", 10, 0, "sessions"),
        Milestone("fifty_sessions", "五十次学习", "累计完成50次学习", 50, 0, "sessions"),
        Milestone("hundred_sessions", "百次学习", "累计完成100次学习", 100, 0, "sessions"),
        Milestone("ten_books", "十本绘本", "阅读10本不同绘本", 10, 0, "books"),
        Milestone("fifty_books", "五十本绘本", "阅读50本不同绘本", 50, 0, "books"),
        Milestone("hundred_books", "百本绘本", "阅读100本不同绘本", 100, 0, "books"),
        Milestone("total_hours", "学习达人", "累计学习100小时", 6000, 0, "minutes")
    ]


def create_default_achievements() -> List[Achievement]:
    """创建默认成就列表

    Returns:
        默认成就列表
    """
    return [
        Achievement("early_bird", "早起鸟", "早晨进行学习", icon="🌅", points=20),
        Achievement("night_owl", "夜猫子", "晚间进行学习", icon="🦉", points=20),
        Achievement("consistency", "持之以恒", "保持30天学习", icon="⭐", points=50),
        Achievement("explorer", "探索者", "尝试3种不同主题", icon="🔍", points=30),
        Achievement("question_master", "提问达人", "累计提问超过100个", icon="❓", points=40),
        Achievement("creative", "创意无限", "完成创意互动10次", icon="💡", points=30),
        Achievement("speed_reader", "快速阅读", "10分钟内完成学习", icon="⚡", points=20),
        Achievement("focused", "专注学习", "单次投入度超过8分", icon="🎯", points=25),
        Achievement("social_sharing", "分享达人", "分享学习成果", icon="📤", points=15),
        Achievement("perfect_score", "完美表现", "获得10次满分投入度", icon="💯", points=50)
    ]


def update_milestones(
    milestones: List[Milestone],
    records: List[Dict[str, Any]]
) -> List[Milestone]:
    """更新里程碑进度

    Args:
        milestones: 里程碑列表
        records: 学习记录列表

    Returns:
        更新后的里程碑列表
    """
    total_sessions = len(records)
    total_minutes = sum(r.get("duration_minutes", 0) for r in records)
    unique_books = len(set(r.get("book_title", "") for r in records))

    dates = [datetime.fromisoformat(r.get("timestamp", "2000-01-01")) for r in records if r.get("timestamp")]
    if dates:
        sorted_dates = sorted(dates)
        current_streak = 1
        max_streak = 1
        temp_streak = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                temp_streak += 1
                if temp_streak > max_streak:
                    max_streak = temp_streak
            else:
                temp_streak = 1
        current_streak = temp_streak
    else:
        current_streak = 0
        max_streak = 0

    for milestone in milestones:
        if milestone.is_achieved() and milestone.awarded_at:
            continue

        if milestone.milestone_type == "sessions":
            milestone.current_value = total_sessions
        elif milestone.milestone_type == "streak":
            milestone.current_value = max(current_streak, max_streak)
        elif milestone.milestone_type == "minutes":
            milestone.current_value = total_minutes
        elif milestone.milestone_type == "books":
            milestone.current_value = unique_books

        if milestone.is_achieved() and not milestone.awarded_at:
            milestone.awarded_at = datetime.now().isoformat()

    return milestones


def check_achievements(
    achievements: List[Achievement],
    records: List[Dict[str, Any]],
    existing_achievements: List[str]
) -> List[Achievement]:
    """检查成就解锁情况

    Args:
        achievements: 成就列表
        records: 学习记录列表
        existing_achievements: 已解锁成就ID列表

    Returns:
        更新后的成就列表
    """
    now = datetime.now().isoformat()

    dates = [datetime.fromisoformat(r.get("timestamp", "2000-01-01")) for r in records if r.get("timestamp")]

    for achievement in achievements:
        if achievement.achievement_id in existing_achievements:
            continue

        if achievement.achievement_id == "early_bird":
            morning_hours = [datetime.fromisoformat(r.get("timestamp")).hour for r in records if r.get("timestamp")]
            if any(5 <= h < 9 for h in morning_hours):
                achievement.unlocked_at = now

        elif achievement.achievement_id == "night_owl":
            night_hours = [datetime.fromisoformat(r.get("timestamp")).hour for r in records if r.get("timestamp")]
            if any(20 <= h or h < 2 for h in night_hours):
                achievement.unlocked_at = now

        elif achievement.achievement_id == "consistency":
            dates = sorted(dates)
            if len(dates) >= 30:
                achievement.unlocked_at = now

        elif achievement.achievement_id == "explorer":
            topics = set()
            for r in records:
                topics.update(r.get("topics_covered", []))
            if len(topics) >= 3:
                achievement.unlocked_at = now

        elif achievement.achievement_id == "question_master":
            total_questions = sum(r.get("questions_asked", 0) for r in records)
            if total_questions >= 100:
                achievement.unlocked_at = now

        elif achievement.achievement_id == "creative":
            creative_count = sum(1 for r in records if r.get("interaction_type") == "创意")
            if creative_count >= 10:
                achievement.unlocked_at = now

        elif achievement.achievement_id == "speed_reader":
            short_sessions = sum(1 for r in records if r.get("duration_minutes", 0) <= 10 and r.get("duration_minutes", 0) > 0)
            if short_sessions >= 5:
                achievement.unlocked_at = now

        elif achievement.achievement_id == "focused":
            high_engagement = sum(1 for r in records if r.get("engagement_score", 0) >= 8.0)
            if high_engagement >= 5:
                achievement.unlocked_at = now

        elif achievement.achievement_id == "perfect_score":
            perfect_scores = sum(1 for r in records if r.get("engagement_score", 0) >= 10.0)
            if perfect_scores >= 10:
                achievement.unlocked_at = now

    return achievements


def calculate_streak(dates: List[str]) -> Tuple[int, int]:
    """计算连续学习天数

    Args:
        dates: 日期字符串列表

    Returns:
        (当前连续天数, 最长连续天数)
    """
    if not dates:
        return 0, 0

    parsed_dates = sorted(set(datetime.strptime(d, "%Y-%m-%d") for d in dates))

    current_streak = 1
    longest_streak = 1
    temp_streak = 1

    for i in range(1, len(parsed_dates)):
        if (parsed_dates[i] - parsed_dates[i-1]).days == 1:
            temp_streak += 1
        else:
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            temp_streak = 1

    if temp_streak > longest_streak:
        longest_streak = temp_streak

    today = datetime.now().date()
    if parsed_dates and (today - parsed_dates[-1].date()).days <= 1:
        current_streak = temp_streak
    else:
        current_streak = 0

    return current_streak, longest_streak


def generate_progress_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成进度摘要

    Args:
        records: 学习记录列表

    Returns:
        进度摘要字典
    """
    if not records:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "milestones": [],
            "achievements": [],
            "level": 1,
            "points": 0
        }

    total_sessions = len(records)
    total_minutes = sum(r.get("duration_minutes", 0) for r in records)
    unique_books = len(set(r.get("book_title", "") for r in records))

    dates = [r.get("timestamp", "").split("T")[0] for r in records if r.get("timestamp")]
    current_streak, longest_streak = calculate_streak(dates)

    milestones = create_default_milestones()
    milestones = update_milestones(milestones, records)

    achievements = create_default_achievements()
    existing_achievements = [a.achievement_id for a in achievements if a.unlocked_at]
    achievements = check_achievements(achievements, records, existing_achievements)

    total_points = sum(a.points for a in achievements if a.unlocked_at)
    level = max(1, total_points // 100 + 1)

    recent_records = records[-7:] if len(records) >= 7 else records
    recent_avg = sum(r.get("engagement_score", 0.0) for r in recent_records) / len(recent_records) if recent_records else 0.0

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "unique_books": unique_books,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "milestones": [m.to_dict() for m in milestones],
        "achievements": [a.to_dict() for a in achievements],
        "level": level,
        "points": total_points,
        "recent_average_engagement": round(recent_avg, 2)
    }


def generate_detailed_report(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成详细进度报告

    Args:
        records: 学习记录列表

    Returns:
        详细进度报告字典
    """
    summary = generate_progress_summary(records)

    daily_stats = defaultdict(lambda: {"sessions": 0, "minutes": 0, "engagement": []})
    for record in records:
        date = record.get("timestamp", "").split("T")[0]
        if date:
            daily_stats[date]["sessions"] += 1
            daily_stats[date]["minutes"] += record.get("duration_minutes", 0)
            daily_stats[date]["engagement"].append(record.get("engagement_score", 0.0))

    weekly_data = []
    current_date = datetime.now()
    for i in range(4):
        week_start = current_date - timedelta(weeks=i+1)
        week_end = week_start + timedelta(days=7)
        week_records = [
            r for r in records
            if r.get("timestamp") and
            week_start <= datetime.fromisoformat(r.get("timestamp")) < week_end
        ]
        if week_records:
            weekly_data.append({
                "week": f"第{i+1}周前",
                "sessions": len(week_records),
                "minutes": sum(r.get("duration_minutes", 0) for r in week_records),
                "engagement": sum(r.get("engagement_score", 0.0) for r in week_records) / len(week_records)
            })

    return {
        "summary": summary,
        "daily_breakdown": dict(daily_stats),
        "weekly_trend": weekly_data,
        "generated_at": datetime.now().isoformat()
    }


def export_progress_csv(records: List[Dict[str, Any]]) -> str:
    """导出进度数据为CSV

    Args:
        records: 学习记录列表

    Returns:
        CSV格式字符串
    """
    lines = ["日期,绘本,时长(分钟),投入度,理解程度,互动类型"]

    for record in records:
        date = record.get("timestamp", "").split("T")[0]
        book = record.get("book_title", "")
        duration = record.get("duration_minutes", 0)
        engagement = record.get("engagement_score", 0.0)
        comprehension = record.get("comprehension_level", "")
        interaction = record.get("interaction_type", "")

        lines.append(f"{date},{book},{duration},{engagement},{comprehension},{interaction}")

    return "\n".join(lines)


def track_session_completion(
    records: List[Dict[str, Any]],
    session_data: Dict[str, Any]
) -> Dict[str, Any]:
    """追踪会话完成情况

    Args:
        records: 学习记录列表
        session_data: 会话数据

    Returns:
        追踪结果
    """
    session_id = str(uuid.uuid4())[:8]

    record = {
        "record_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "book_title": session_data.get("book_title", ""),
        "duration_minutes": session_data.get("duration_minutes", 0),
        "engagement_score": session_data.get("engagement_score", 0.0),
        "questions_asked": session_data.get("questions_asked", 0),
        "questions_answered": session_data.get("questions_answered", 0),
        "comprehension_level": session_data.get("comprehension_level", "学习中"),
        "interaction_type": session_data.get("interaction_type", "提问"),
        "topics_covered": session_data.get("topics_covered", []),
        "child_reaction": session_data.get("child_reaction", ""),
        "parent_observation": session_data.get("parent_observation", "")
    }

    records.append(record)

    milestones = create_default_milestones()
    milestones = update_milestones(milestones, records)

    newly_achieved = [m for m in milestones if m.is_achieved() and m.awarded_at]

    return {
        "record": record,
        "total_records": len(records),
        "new_milestones": [m.to_dict() for m in newly_achieved]
    }