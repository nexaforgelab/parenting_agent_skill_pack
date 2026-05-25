"""Planning engine for 课外班避坑 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
try:
    from .models import TrendData, Alert, Recommendation, SessionContext
except ImportError:
    from models import TrendData, Alert, Recommendation, SessionContext

SKILL_FLOW = ['收集课外班信息', '识别潜在风险', '评估机构信誉', '输出避坑建议']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['风险评估报告', '避坑清单', '机构信誉对比']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def assess_risks(
    classes: List[Dict[str, Any]],
    child_profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """评估课外班风险"""
    risk_assessments = []

    if not classes:
        return risk_assessments

    for cls in classes:
        assessment = {
            "class_id": cls.get("class_id", ""),
            "class_name": cls.get("name", "未知"),
            "institution": cls.get("institution", ""),
            "risk_level": "low",
            "risks": [],
            "warnings": [],
            "recommendations": []
        }

        institution = cls.get("institution", "")
        years_in_business = cls.get("years_in_business", 0)
        if years_in_business < 2:
            assessment["risks"].append("机构运营时间较短，可能存在经营风险")
            assessment["risk_level"] = "high"
        elif years_in_business < 5:
            assessment["warnings"].append("机构运营时间较短，建议谨慎选择")

        accreditation = cls.get("accreditation", [])
        if not accreditation or len(accreditation) == 0:
            assessment["warnings"].append("机构缺乏官方资质认证")
            assessment["risk_level"] = "medium" if assessment["risk_level"] == "low" else assessment["risk_level"]

        refund_policy = cls.get("refund_policy", "")
        if not refund_policy or "不可退" in refund_policy:
            assessment["risks"].append("退款政策不明确或不支持退款")
            assessment["risk_level"] = "high"

        contract_required = cls.get("contract_required", False)
        if not contract_required:
            assessment["warnings"].append("未要求签订正式合同，存在风险")
            assessment["risk_level"] = "medium" if assessment["risk_level"] == "low" else assessment["risk_level"]

        tuition = cls.get("tuition", 0)
        if tuition > 20000 and not cls.get("installment_available", False):
            assessment["warnings"].append("学费较高且不支持分期付款")

        teacher_qualification = cls.get("teacher_qualification", "")
        if not teacher_qualification or teacher_qualification == "不明":
            assessment["warnings"].append("教师资质不明确")

        class_size = cls.get("class_size", 0)
        if class_size > 20:
            assessment["warnings"].append(f"班级人数较多（{class_size}人），可能影响教学质量")

        risk_assessments.append(assessment)

    return risk_assessments


def detect_common_schemes(
    classes: List[Dict[str, Any]]
) -> List[Alert]:
    """检测常见套路"""
    alerts = []

    if not classes:
        return alerts

    for cls in classes:
        red_flags = cls.get("red_flags", [])

        if "限时优惠" in red_flags or "名额有限" in red_flags:
            alerts.append(Alert(
                alert_type="促销套路",
                severity="warning",
                message=f"{cls.get('name', '该课程')}可能使用限时优惠等促销套路",
                recommendation="遇到此类促销要冷静判断，避免冲动报名"
            ))

        if "名师推荐" in red_flags or "升学保障" in red_flags:
            alerts.append(Alert(
                alert_type="虚假宣传",
                severity="warning",
                message=f"{cls.get('name', '该课程')}可能存在虚假宣传",
                recommendation="要求机构提供真实的成功案例和证明材料"
            ))

        if "转账私人账户" in red_flags:
            alerts.append(Alert(
                alert_type="资金风险",
                severity="critical",
                message=f"{cls.get('name', '该课程')}要求转账到私人账户",
                recommendation="绝对不要向私人账户转账，正规机构使用对公账户"
            ))

    return alerts


def generate_risk_recommendations(
    classes: List[Dict[str, Any]],
    assessments: List[Dict[str, Any]],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成避坑建议"""
    recommendations = []

    recommendations.append(Recommendation(
        category="避坑建议",
        priority=1,
        title="报名前必查清单",
        description="在报名任何课外班之前，请务必完成以下检查",
        action_items=[
            "核实机构营业执照和办学资质",
            "要求查看教师资格证书",
            "仔细阅读合同条款，特别关注退款政策",
            "不要被促销活动冲昏头脑",
            "优先选择支持退款的机构"
        ],
        rationale="充分了解才能避免损失",
        expected_outcome="降低选错课外班的风险"
    ))

    high_risk_classes = [a for a in assessments if a.get("risk_level") == "high"]
    if high_risk_classes:
        recommendations.append(Recommendation(
            category="高风险提醒",
            priority=1,
            title="发现高风险课外班",
            description=f"有 {len(high_risk_classes)} 个课外班存在较高风险，建议谨慎选择",
            action_items=[
                "暂缓报名，深入了解",
                "寻找替代方案",
                "向已报名的家长了解真实情况"
            ],
            rationale="高风险机构可能带来经济损失和时间浪费",
            expected_outcome="避开潜在风险"
        ))

    recommendations.append(Recommendation(
        category="选择建议",
        priority=2,
        title="选择机构的黄金法则",
        description="根据多年经验，总结出以下选择机构的黄金法则",
        action_items=[
            "选择运营5年以上的机构",
            "优先选择有官方认证的机构",
            "选择支持分期付款的机构",
            "选择退款政策明确的机构",
            "实地考察后再做决定"
        ],
        rationale="经验证的法则能有效降低风险",
        expected_outcome="找到靠谱的课外班"
    ))

    return recommendations


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

    classes = payload.get("classes") or []
    facts.append(f"已收到 {len(classes)} 个课外班的信息。")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    classes = payload.get("classes") or []
    child_profile = payload.get("child_profile", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        "建议从机构资质、合同条款、退款政策等方面评估风险。",
        "本 Skill 会优先输出可执行动作、风险评估和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if classes:
        assessments = assess_risks(classes, child_profile)
        alerts = detect_common_schemes(classes)

        high_risk_count = sum(1 for a in assessments if a.get("risk_level") == "high")
        medium_risk_count = sum(1 for a in assessments if a.get("risk_level") == "medium")

        analysis.append("")
        analysis.append(f"📊 风险评估结果：")
        analysis.append(f"  - 高风险：{high_risk_count}个")
        analysis.append(f"  - 中风险：{medium_risk_count}个")
        analysis.append(f"  - 低风险：{len(assessments) - high_risk_count - medium_risk_count}个")

        if alerts:
            analysis.append("")
            analysis.append("⚠️ 检测到的套路：")
            for alert in alerts:
                analysis.append(f"  - [{alert.severity}] {alert.alert_type}：{alert.message[:30]}...")

        recommendations = generate_risk_recommendations(classes, assessments, child_profile, alerts)
        if recommendations:
            analysis.append("")
            analysis.append("📋 避坑建议：")
            for rec in recommendations[:3]:
                analysis.append(f"  - {rec.title}：{rec.description[:30]}...")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "核实目标课外班的机构资质",
        "仔细阅读合同条款",
        "特别关注退款政策",
        "向在读学员家长了解真实情况",
        "综合评估后做决定",
    ]

    classes = payload.get("classes") or []
    if classes:
        base_tasks.insert(0, f"评估 {len(classes)} 个课外班的风险")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长",
            "evidence_to_record": "核实结果、合同分析、家长反馈",
            "difficulty": "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "risk_assessment": ["课外班", "机构", "风险等级", "主要风险", "建议"],
            "checklist": ["检查项", "标准", "是否通过", "备注"]
        },
        "templates": {
            "contract_review": "退款政策、违约金条款、转让条款、终止条款",
            "institution_review": "营业执照、办学资质、教师资质、教学环境"
        }
    }

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "核实结果",
        "合同审查情况",
        "家长反馈收集",
        "最终选择决定",
        "报名后跟踪"
    ]


def clear_context(session_id: str) -> bool:
    """清除会话上下文"""
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
