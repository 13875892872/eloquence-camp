"""后台管理 — 打卡配置（每日任务 + 成长目标）"""
from flask import request
from . import admin_bp
from ...extensions import db
from ...models.checkin import DailyTaskConfig, GrowthGoalConfig
from ...utils import ok, fail


# ==================== 每日任务配置 ====================

@admin_bp.route('/checkin-config', methods=['GET'])
def get_checkin_config():
    """获取打卡配置"""
    tasks = DailyTaskConfig.query.order_by(DailyTaskConfig.task_index.asc()).all()
    sequential = True  # 可在数据库中存储或硬编码

    return ok({
        'task_count': len(tasks),
        'sequential_mode': sequential,
        'refresh_hour': 0,
        'tasks': [
            {
                'task_index': t.task_index,
                'title': t.title,
                'subtitle': t.subtitle,
                'min_duration': t.min_duration,
                'source_type': t.source_type,
                'source_category': t.source_category,
                'source_difficulty_min': t.source_difficulty_min,
                'source_difficulty_max': t.source_difficulty_max,
                'is_active': t.is_active
            } for t in tasks
        ],
        'special_dates': []
    })


@admin_bp.route('/checkin-config', methods=['PUT'])
def update_checkin_config():
    """更新打卡配置"""
    data = request.get_json()
    tasks = data.get('tasks', [])

    for t in tasks:
        config = DailyTaskConfig.query.filter_by(task_index=t['task_index']).first()
        if config:
            config.title = t.get('title', config.title)
            config.subtitle = t.get('subtitle', config.subtitle)
            config.min_duration = t.get('min_duration', config.min_duration)
            config.source_type = t.get('source_type', config.source_type)
            config.source_category = t.get('source_category', config.source_category)
            config.source_difficulty_min = t.get('source_difficulty_min', 1)
            config.source_difficulty_max = t.get('source_difficulty_max', 3)
            config.is_active = t.get('is_active', True)

    db.session.commit()
    return ok({'message': '打卡配置已保存'})


# ==================== 成长目标配置 ====================

@admin_bp.route('/growth-config', methods=['GET'])
def get_growth_config():
    """获取成长目标配置"""
    goals = GrowthGoalConfig.query.order_by(GrowthGoalConfig.required_days.asc()).all()
    return ok({
        'goals': [
            {
                'goal_level': g.goal_level,
                'goal_name': g.goal_name,
                'required_days': g.required_days,
                'reward_level': g.reward_level,
                'reward_extra_ai': g.reward_extra_ai,
                'badge_icon': g.badge_icon,
                'badge_name': g.badge_name,
                'is_active': g.is_active
            } for g in goals
        ]
    })


@admin_bp.route('/growth-config', methods=['PUT'])
def update_growth_config():
    """更新成长目标配置"""
    data = request.get_json()
    goals = data.get('goals', [])

    for g in goals:
        config = GrowthGoalConfig.query.filter_by(goal_level=g['goal_level']).first()
        if config:
            config.goal_name = g.get('goal_name', config.goal_name)
            config.required_days = g.get('required_days', config.required_days)
            config.reward_level = g.get('reward_level', config.reward_level)
            config.reward_extra_ai = g.get('reward_extra_ai', config.reward_extra_ai)
            config.badge_icon = g.get('badge_icon', config.badge_icon)
            config.badge_name = g.get('badge_name', config.badge_name)
            config.is_active = g.get('is_active', True)

    db.session.commit()
    return ok({'message': '成长目标配置已保存'})
