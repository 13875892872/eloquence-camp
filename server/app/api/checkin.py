"""
打卡模块 — 今日任务 / 完成任务 / 日历 / 成长目标 / 每日一句 / 推送模板ID
"""
import random
import logging
from datetime import date, datetime
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..extensions import db
from ..models.user import User
from ..models.checkin import DailyTaskConfig, CheckinRecord, GrowthGoalConfig
from ..models.training import TrainingItem
from ..models.admin import PushTemplate
from ..utils import ok, fail

logger = logging.getLogger(__name__)
bp = Blueprint('checkin', __name__)

# 每日一句缓存
_cached_quote = None
_quote_date = None


def _get_daily_quote():
    """获取每日一句（带日期缓存，快速返回）"""
    global _cached_quote, _quote_date
    today = date.today()
    if _cached_quote and _quote_date == today:
        return _cached_quote

    # 降级默认值（始终可用）
    _cached_quote = {
        'content': '千里之行，始于足下。每天练习，成就更好的自己！',
        'source': '每日金句'
    }
    _quote_date = today

    # 异步获取远程名言（后台线程，不阻塞请求）
    def _fetch_remote():
        try:
            from scheduler.sources.quotes import QuotesSource
            source = QuotesSource({})
            items = source.fetch()
            if items:
                _cached_quote['content'] = items[0].get('content', '')
                _cached_quote['source'] = items[0].get('source_name', '')
        except Exception:
            pass

    import threading
    t = threading.Thread(target=_fetch_remote, daemon=True)
    t.start()

    return _cached_quote


def _get_user():
    """从JWT获取当前用户"""
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user_id = int(identity) if identity else None
    return User.query.get(user_id) if user_id else None


@bp.route('/today', methods=['GET'])
def get_today_status():
    """获取今日打卡状态（含3个任务 + 每日一句）"""
    user = _get_user()
    today = date.today()

    # 获取活跃的任务配置
    task_configs = DailyTaskConfig.query.filter_by(is_active=True)\
        .order_by(DailyTaskConfig.task_index).limit(3).all()

    # 默认任务模板（数据库无配置时使用）
    default_tasks = [
        {'task_index': 1, 'title': '朗读练习', 'subtitle': '跟读范本练习发音', 'min_duration': 30},
        {'task_index': 2, 'title': '即兴演讲', 'subtitle': '随机主题3分钟演讲', 'min_duration': 60},
        {'task_index': 3, 'title': '自由练习', 'subtitle': '自选题目进行录音', 'min_duration': 60},
    ]

    # 查询用户今日打卡记录
    today_record = None
    completed_task_indices = []
    if user:
        today_record = CheckinRecord.query.filter_by(
            user_id=user.id, task_date=today
        ).first()
        if today_record and today_record.completed_tasks:
            completed_task_indices = today_record.completed_tasks

    # 构建任务列表
    tasks = []
    for i, cfg in enumerate(task_configs):
        # 为每个任务抽取一个训练题
        training_item = None
        if cfg.source_type == 'random' and cfg.source_category:
            items = TrainingItem.query.filter_by(
                category=cfg.source_category, status='online'
            ).all()
            if items:
                training_item = random.choice(items)

        status = 'locked'
        if i == 0 or (i > 0 and (i) in completed_task_indices):
            status = 'pending'
        if (cfg.task_index) in completed_task_indices:
            status = 'completed'

        tasks.append({
            'task_index': cfg.task_index,
            'title': cfg.title,
            'subtitle': cfg.subtitle,
            'min_duration': cfg.min_duration,
            'status': status,
            'training_item': training_item.to_dict() if training_item else None,
            'my_record': None
        })

    # 无配置时使用默认模板
    if not tasks:
        for i, dt in enumerate(default_tasks):
            status = 'locked'
            if i == 0:
                status = 'pending'
            if (dt['task_index']) in completed_task_indices:
                status = 'completed'
            tasks.append({**dt, 'status': status, 'training_item': None, 'my_record': None})

    all_completed = len(completed_task_indices) >= len(tasks)

    # 用户统计
    stats = {}
    if user:
        stats = {
            'continuous_days': user.continuous_days,
            'total_days': user.total_days,
            'total_minutes': user.total_practice_minutes
        }

    return ok({
        'date': str(today),
        'is_checked_in': len(completed_task_indices) > 0,
        'tasks': tasks,
        'all_completed': all_completed,
        'stats': stats,
        'daily_quote': _get_daily_quote()
    })


@bp.route('/complete-task', methods=['POST'])
def complete_task():
    """完成单个打卡任务"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    data = request.get_json()
    task_index = data.get('task_index')
    if not task_index:
        return fail(400, 'task_index不能为空')

    today = date.today()

    # 查找或创建今日打卡记录
    record = CheckinRecord.query.filter_by(
        user_id=user.id, task_date=today
    ).first()

    if not record:
        record = CheckinRecord(
            user_id=user.id,
            task_date=today,
            completed_tasks=[]
        )
        db.session.add(record)

    completed = record.completed_tasks or []
    if task_index not in completed:
        completed.append(task_index)
        record.completed_tasks = completed

    db.session.commit()

    # 检查是否全部完成
    task_configs = DailyTaskConfig.query.filter_by(is_active=True).all()
    total_tasks = len(task_configs) if task_configs else 3
    all_completed = len(completed) >= total_tasks

    return ok({
        'task_completed': True,
        'all_completed': all_completed,
        'completed_tasks': completed
    })


@bp.route('/calendar', methods=['GET'])
def get_calendar():
    """获取打卡日历"""
    user = _get_user()
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    days = []
    if user:
        records = CheckinRecord.query.filter(
            CheckinRecord.user_id == user.id,
            db.func.strftime('%Y', CheckinRecord.task_date) == str(year),
            db.func.strftime('%m', CheckinRecord.task_date) == f'{month:02d}'
        ).all()
        days = [str(r.task_date) for r in records]

    return ok({
        'year': year,
        'month': month,
        'days': days,
        'summary': {'total': len(days)}
    })


@bp.route('/push-template-ids', methods=['GET'])
def get_push_template_ids():
    """返回需要用户授权的微信订阅消息模板ID列表"""
    try:
        tpls = PushTemplate.query.filter_by(is_active=True).all()
        tmpl_ids = [t.wx_template_id for t in tpls if t.wx_template_id]
        return ok({'tmpl_ids': tmpl_ids})
    except Exception as e:
        return ok({'tmpl_ids': []})


@bp.route('/growth-progress', methods=['GET'])
def growth_progress():
    """成长目标进度"""
    user = _get_user()

    # 获取所有活跃的成长目标
    configs = GrowthGoalConfig.query.filter_by(is_active=True)\
        .order_by(GrowthGoalConfig.required_days).all()

    current_level = user.growth_level if user else 'newbie'
    total_days = user.total_days if user else 0

    goals = []
    for cfg in configs:
        achieved = total_days >= cfg.required_days
        progress = min(100, round(total_days / cfg.required_days * 100)) if cfg.required_days > 0 else 100

        goals.append({
            'level': cfg.goal_level,
            'name': cfg.goal_name,
            'required_days': cfg.required_days,
            'badge': {'icon': cfg.badge_icon or '🎯', 'name': cfg.badge_name or cfg.goal_name},
            'my_days': total_days,
            'progress': progress,
            'achieved': achieved,
            'reward_extra_ai': cfg.reward_extra_ai
        })

    # 数据库无配置时提供默认目标
    if not goals:
        default_goals = [
            {'level': 'newbie', 'name': '新人起步', 'required_days': 7, 'icon': '🌱', 'name_cn': '口才新人'},
            {'level': 'beginner', 'name': '初入门径', 'required_days': 21, 'icon': '🌿', 'name_cn': '入门学员'},
            {'level': 'advanced', 'name': '进阶提升', 'required_days': 50, 'icon': '🌳', 'name_cn': '进阶达人'},
            {'level': 'expert', 'name': '口才达人', 'required_days': 100, 'icon': '🏆', 'name_cn': '口才专家'},
        ]
        for dg in default_goals:
            achieved = total_days >= dg['required_days']
            progress = min(100, round(total_days / dg['required_days'] * 100)) if dg['required_days'] > 0 else 100
            goals.append({
                'level': dg['level'],
                'name': dg['name'],
                'required_days': dg['required_days'],
                'badge': {'icon': dg['icon'], 'name': dg['name_cn']},
                'my_days': total_days,
                'progress': progress,
                'achieved': achieved,
                'reward_extra_ai': 0
            })

    return ok({
        'current_level': current_level,
        'goals': goals
    })
