"""初始化打卡/AI配置默认值"""
from app import create_app
from app.extensions import db
from app.models.checkin import DailyTaskConfig, GrowthGoalConfig
from app.models.ai import AiConfig

app = create_app()

DEFAULT_TASKS = [
    {'task_index': 1, 'title': '跟读朗读', 'subtitle': '晨间新闻跟读 3min',
     'min_duration': 60, 'source_type': 'random', 'source_category': 'basic',
     'source_difficulty_min': 1, 'source_difficulty_max': 2, 'is_active': True},
    {'task_index': 2, 'title': '短句表达', 'subtitle': '给定场景组织语言 5min',
     'min_duration': 30, 'source_type': 'random', 'source_category': 'improv',
     'source_difficulty_min': 1, 'source_difficulty_max': 2, 'is_active': True},
    {'task_index': 3, 'title': '即兴口述', 'subtitle': '随机话题即兴发挥 5min',
     'min_duration': 30, 'source_type': 'random', 'source_category': 'improv',
     'source_difficulty_min': 1, 'source_difficulty_max': 2, 'is_active': True},
]

DEFAULT_GOALS = [
    {'goal_level': 'beginner', 'goal_name': '7天入门', 'required_days': 7,
     'reward_level': '中级', 'reward_extra_ai': 1, 'badge_icon': '🏅', 'badge_name': '口才新星'},
    {'goal_level': 'advanced', 'goal_name': '30天进阶', 'required_days': 30,
     'reward_level': '高级', 'reward_extra_ai': 3, 'badge_icon': '🥈', 'badge_name': '表达达人'},
    {'goal_level': 'expert', 'goal_name': '60天达人', 'required_days': 60,
     'reward_level': '大师', 'reward_extra_ai': 5, 'badge_icon': '🥇', 'badge_name': '演讲大师'},
    {'goal_level': 'master', 'goal_name': '100天大师', 'required_days': 100,
     'reward_level': '全解锁', 'reward_extra_ai': -1, 'badge_icon': '👑', 'badge_name': '口才王者'},
]

with app.app_context():
    db.create_all()

    # 每日任务配置
    if DailyTaskConfig.query.count() == 0:
        for t in DEFAULT_TASKS:
            db.session.add(DailyTaskConfig(**t))
        print('✅ 每日任务配置已初始化')

    # 成长目标配置
    if GrowthGoalConfig.query.count() == 0:
        for g in DEFAULT_GOALS:
            db.session.add(GrowthGoalConfig(**g))
        print('✅ 成长目标配置已初始化')

    # AI配置
    if AiConfig.query.count() == 0:
        db.session.add(AiConfig())
        print('✅ AI配置已初始化（使用默认值）')

    db.session.commit()
    print('🎉 种子数据初始化完成')
