"""成长等级与奖励"""
from ..models.checkin import GrowthGoalConfig

LEVEL_ORDER = ['newbie', 'beginner', 'advanced', 'expert', 'master']

LEVEL_LABELS = {
    'newbie': '新人',
    'beginner': '入门',
    'advanced': '进阶',
    'expert': '达人',
    'master': '大师',
}

MAX_DIFFICULTY_BY_LEVEL = {
    'newbie': 1,
    'beginner': 2,
    'advanced': 3,
    'expert': 4,
    'master': 5,
}


def level_rank(level):
    try:
        return LEVEL_ORDER.index(level)
    except ValueError:
        return 0


def max_difficulty(growth_level):
    return MAX_DIFFICULTY_BY_LEVEL.get(growth_level or 'newbie', 1)


def compute_target_level(total_days):
    """根据累计打卡天数计算应达到的成长等级"""
    configs = GrowthGoalConfig.query.filter_by(is_active=True)\
        .order_by(GrowthGoalConfig.required_days.desc()).all()
    target = 'newbie'
    for cfg in configs:
        if total_days >= cfg.required_days:
            target = cfg.goal_level
            break
    return target


def apply_growth_rewards(user):
    """
    检查并应用成长目标奖励，返回新达成的目标（用于前端弹窗）
    仅当等级提升时发放对应 extra_quota
    """
    from ..extensions import db
    from ..models.user import UserQuota

    old_level = user.growth_level or 'newbie'
    new_level = compute_target_level(user.total_days or 0)
    newly_achieved = []

    if level_rank(new_level) <= level_rank(old_level):
        return newly_achieved

    configs = GrowthGoalConfig.query.filter_by(is_active=True)\
        .order_by(GrowthGoalConfig.required_days.asc()).all()

    quota = user.quota
    if not quota:
        quota = UserQuota(user_id=user.id)
        db.session.add(quota)

    for cfg in configs:
        if level_rank(cfg.goal_level) <= level_rank(old_level):
            continue
        if level_rank(cfg.goal_level) > level_rank(new_level):
            continue
        if (user.total_days or 0) < cfg.required_days:
            continue
        extra = cfg.reward_extra_ai or 0
        if extra > 0:
            quota.extra_quota = (quota.extra_quota or 0) + extra
        elif extra == -1:
            quota.daily_ai_quota = max(quota.daily_ai_quota or 3, 99)
        newly_achieved.append({
            'level': cfg.goal_level,
            'name': cfg.goal_name,
            'badge': {'icon': cfg.badge_icon or '🎯', 'name': cfg.badge_name or cfg.goal_name},
            'reward_extra_ai': extra,
            'reward_level': cfg.reward_level,
        })

    user.growth_level = new_level
    return newly_achieved
