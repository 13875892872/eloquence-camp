"""
打卡模块 — 今日任务 / 完成任务 / 日历 / 成长目标 / 补签 / 7天入门
"""
import random
import logging
from datetime import date, timedelta
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..extensions import db
from ..models.user import User
from ..models.checkin import DailyTaskConfig, CheckinRecord, GrowthGoalConfig
from ..models.training import TrainingItem
from ..models.common import PracticeRecord
from ..models.admin import PushTemplate
from ..services.checkin_service import (
    validate_practice_for_task, can_unlock_task, finalize_daily_checkin,
    min_duration_for, get_task_config,
)
from ..services.growth import max_difficulty, LEVEL_LABELS, apply_growth_rewards
from ..data.beginner_course import BEGINNER_COURSE
from ..utils import ok, fail

logger = logging.getLogger(__name__)
bp = Blueprint('checkin', __name__)

_cached_quote = None
_quote_date = None


def _get_daily_quote():
    global _cached_quote, _quote_date
    today = date.today()
    if _cached_quote and _quote_date == today:
        return _cached_quote

    _cached_quote = {
        'content': '千里之行，始于足下。每天练习，成就更好的自己！',
        'source': '每日金句'
    }
    _quote_date = today

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
    threading.Thread(target=_fetch_remote, daemon=True).start()
    return _cached_quote


def _get_user():
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user_id = int(identity) if identity else None
    return User.query.get(user_id) if user_id else None


def _get_user_optional():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = int(identity) if identity else None
        return User.query.get(user_id) if user_id else None
    except Exception:
        return None


def _pick_training_item(category, user):
    """按分类抽题，并考虑用户等级解锁难度"""
    max_d = max_difficulty(user.growth_level if user else 'newbie')
    q = TrainingItem.query.filter_by(category=category, status='online')\
        .filter(TrainingItem.difficulty <= max_d)\
        .filter(db.or_(TrainingItem.owner_user_id.is_(None), TrainingItem.owner_user_id == (user.id if user else -1)))
    items = q.all()
    return random.choice(items) if items else None


def _attach_task_records(user, tasks, today):
    """为任务附加今日练习记录摘要"""
    if not user:
        return
    records = PracticeRecord.query.filter(
        PracticeRecord.user_id == user.id,
        db.func.date(PracticeRecord.created_at) == str(today)
    ).order_by(PracticeRecord.created_at.desc()).all()
    for t in tasks:
        item_id = (t.get('training_item') or {}).get('id')
        for r in records:
            if item_id and r.training_item_id == item_id:
                t['my_record'] = {'score': r.ai_score, 'duration': r.duration, 'id': r.id}
                break


@bp.route('/today', methods=['GET'])
def get_today_status():
    user = _get_user_optional()
    today = date.today()

    task_configs = DailyTaskConfig.query.filter_by(is_active=True)\
        .order_by(DailyTaskConfig.task_index).limit(3).all()

    completed_task_indices = []
    today_record = None
    if user:
        today_record = CheckinRecord.query.filter_by(user_id=user.id, task_date=today).first()
        if today_record and today_record.completed_tasks:
            completed_task_indices = list(today_record.completed_tasks)

    tasks = []
    prev_task_index = None
    for i, cfg in enumerate(task_configs):
        training_item = None
        if cfg.source_type == 'random' and cfg.source_category:
            training_item = _pick_training_item(cfg.source_category, user)

        status = 'locked'
        if i == 0:
            status = 'pending'
        elif prev_task_index is not None and prev_task_index in completed_task_indices:
            status = 'pending'
        if cfg.task_index in completed_task_indices:
            status = 'completed'

        prev_task_index = cfg.task_index
        tasks.append({
            'task_index': cfg.task_index,
            'title': cfg.title,
            'subtitle': cfg.subtitle,
            'min_duration': cfg.min_duration,
            'status': status,
            'training_item': training_item.to_dict() if training_item else None,
            'my_record': None,
        })

    if not tasks:
        default_tasks = [
            {'task_index': 1, 'title': '朗读练习', 'subtitle': '跟读范本练习发音', 'min_duration': 30},
            {'task_index': 2, 'title': '即兴演讲', 'subtitle': '随机主题3分钟演讲', 'min_duration': 60},
            {'task_index': 3, 'title': '自由练习', 'subtitle': '自选题目进行录音', 'min_duration': 60},
        ]
        for i, dt in enumerate(default_tasks):
            status = 'locked'
            if i == 0:
                status = 'pending'
            if dt['task_index'] in completed_task_indices:
                status = 'completed'
            tasks.append({**dt, 'status': status, 'training_item': None, 'my_record': None})

    _attach_task_records(user, tasks, today)

    total_tasks = len(task_configs) if task_configs else 3
    all_completed = today_record and today_record.status in ('completed', 'makeup') \
        and len(completed_task_indices) >= total_tasks

    stats = {}
    if user:
        stats = {
            'continuous_days': user.continuous_days,
            'total_days': user.total_days,
            'total_minutes': user.total_practice_minutes,
        }

    return ok({
        'date': str(today),
        'is_checked_in': bool(today_record and today_record.status in ('completed', 'makeup')),
        'checkin_status': today_record.status if today_record else None,
        'tasks': tasks,
        'all_completed': all_completed,
        'stats': stats,
        'daily_quote': _get_daily_quote(),
    })


@bp.route('/complete-task', methods=['POST'])
def complete_task():
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    data = request.get_json() or {}
    task_index = data.get('task_index')
    if not task_index:
        return fail(400, 'task_index不能为空')

    task_index = int(task_index)
    task_configs = DailyTaskConfig.query.filter_by(is_active=True).order_by(DailyTaskConfig.task_index).all()
    completed_before = []

    today = date.today()
    record = CheckinRecord.query.filter_by(user_id=user.id, task_date=today).first()
    if record and record.completed_tasks:
        completed_before = list(record.completed_tasks)

    if not can_unlock_task(task_index, completed_before, task_configs or None):
        if task_index != 1 and (task_index - 1) not in completed_before:
            return fail(400, '请先完成前一个任务')

    ok_practice, err, _rec = validate_practice_for_task(
        user, task_index,
        practice_record_id=data.get('practice_record_id'),
        duration=data.get('duration'),
    )
    if not ok_practice:
        return fail(400, err)

    if not record:
        record = CheckinRecord(user_id=user.id, task_date=today, status='pending', completed_tasks=[])
        db.session.add(record)

    completed = record.completed_tasks or []
    if task_index not in completed:
        completed.append(task_index)
        record.completed_tasks = completed

    total_tasks = len(task_configs) if task_configs else 3
    all_completed = len(completed) >= total_tasks
    goal_achieved = []
    stats = None

    if all_completed and record.status not in ('completed', 'makeup'):
        goal_achieved, stats = finalize_daily_checkin(user, record, total_tasks)
    else:
        db.session.commit()

    today_records = PracticeRecord.query.filter(
        PracticeRecord.user_id == user.id,
        db.func.date(PracticeRecord.created_at) == str(today)
    ).all()
    today_seconds = sum(r.duration or 0 for r in today_records)

    return ok({
        'task_completed': True,
        'all_completed': all_completed,
        'completed_tasks': completed,
        'today_seconds': today_seconds,
        'goal_achieved': goal_achieved[0] if len(goal_achieved) == 1 else (goal_achieved if goal_achieved else None),
        'goals_achieved': goal_achieved,
        'stats': stats or ({
            'continuous_days': user.continuous_days,
            'total_days': user.total_days,
            'total_minutes': user.total_practice_minutes,
        } if all_completed else None),
    })


@bp.route('/makeup', methods=['POST'])
def makeup_checkin():
    """补签昨日打卡"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    data = request.get_json() or {}
    yesterday = date.today() - timedelta(days=1)

    existing = CheckinRecord.query.filter_by(user_id=user.id, task_date=yesterday).first()
    if existing and existing.status in ('completed', 'makeup'):
        return fail(400, '昨日已打卡，无需补签')

    min_dur = 60
    practice_record_id = data.get('practice_record_id')
    duration = data.get('duration')

    rec = None
    if practice_record_id:
        rec = PracticeRecord.query.filter_by(id=practice_record_id, user_id=user.id).first()
        if not rec:
            return fail(400, '练习记录不存在')
        rec_date = rec.created_at.date() if rec.created_at else date.today()
        if rec_date not in (yesterday, date.today()):
            return fail(400, '请使用最近练习记录补签')
        if (rec.duration or 0) < min_dur:
            return fail(400, f'补签需至少{min_dur}秒练习记录')
    elif not duration or duration < min_dur:
        return fail(400, f'补签需至少完成{min_dur}秒练习')

    if not existing:
        existing = CheckinRecord(
            user_id=user.id,
            task_date=yesterday,
            status='makeup',
            completed_tasks=[1, 2, 3],
        )
        db.session.add(existing)
    else:
        existing.status = 'makeup'
        existing.completed_tasks = [1, 2, 3]

    user.total_days = (user.total_days or 0) + 1
    goal_achieved = apply_growth_rewards(user)

    db.session.commit()

    return ok({
        'makeup_success': True,
        'date': str(yesterday),
        'status': 'makeup',
        'stats': {
            'continuous_days': user.continuous_days,
            'total_days': user.total_days,
            'total_minutes': user.total_practice_minutes,
        },
        'goal_achieved': goal_achieved[0] if len(goal_achieved) == 1 else goal_achieved or None,
    })


@bp.route('/rest', methods=['POST'])
def rest_day():
    """今日休息（不计漏打卡）"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    today = date.today()
    record = CheckinRecord.query.filter_by(user_id=user.id, task_date=today).first()
    if record and record.status in ('completed', 'makeup'):
        return fail(400, '今日已完成打卡，无法设置休息')

    if not record:
        record = CheckinRecord(user_id=user.id, task_date=today, status='rest', completed_tasks=[])
        db.session.add(record)
    else:
        record.status = 'rest'
        record.completed_tasks = []

    db.session.commit()
    return ok({'status': 'rest', 'date': str(today)})


@bp.route('/calendar', methods=['GET'])
def get_calendar():
    user = _get_user()
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    day_entries = []
    summary = {'total': 0, 'completed': 0, 'makeup': 0, 'rest': 0, 'missed': 0}

    if user:
        records = CheckinRecord.query.filter(
            CheckinRecord.user_id == user.id,
            db.func.strftime('%Y', CheckinRecord.task_date) == str(year),
            db.func.strftime('%m', CheckinRecord.task_date) == f'{month:02d}'
        ).all()
        for r in records:
            status = r.status or 'completed'
            day_entries.append({'date': str(r.task_date), 'status': status})
            summary['total'] += 1
            if status == 'completed':
                summary['completed'] += 1
            elif status == 'makeup':
                summary['makeup'] += 1
            elif status == 'rest':
                summary['rest'] += 1

    return ok({
        'year': year,
        'month': month,
        'days': day_entries,
        'summary': summary,
    })


@bp.route('/beginner-course', methods=['GET'])
def beginner_course():
    """7天入门课程进度"""
    user = _get_user_optional()
    if not user:
        return ok({'days': BEGINNER_COURSE, 'current_day': 1, 'is_new_user': True})

    reg_date = user.created_at.date() if user.created_at else date.today()
    days_since = (date.today() - reg_date).days + 1
    current_day = min(max(days_since, 1), 7)
    is_new = days_since <= 7

    days = []
    for item in BEGINNER_COURSE:
        day_num = item['day']
        status = 'locked'
        if day_num < current_day:
            status = 'completed'
        elif day_num == current_day:
            status = 'active'

        training_item = None
        items = TrainingItem.query.filter_by(category=item['category'], status='online')\
            .filter(TrainingItem.owner_user_id.is_(None))\
            .order_by(TrainingItem.sort_order.asc()).offset(day_num - 1).limit(1).all()
        if items:
            training_item = items[0].to_dict()

        days.append({**item, 'status': status, 'training_item': training_item})

    return ok({
        'days': days,
        'current_day': current_day,
        'is_new_user': is_new,
        'days_since_register': days_since,
    })


@bp.route('/push-template-ids', methods=['GET'])
def get_push_template_ids():
    try:
        tpls = PushTemplate.query.filter_by(is_active=True).all()
        tmpl_ids = [t.wx_template_id for t in tpls if t.wx_template_id]
        return ok({'tmpl_ids': tmpl_ids})
    except Exception:
        return ok({'tmpl_ids': []})


@bp.route('/growth-progress', methods=['GET'])
def growth_progress():
    user = _get_user_optional()
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
            'reward_extra_ai': cfg.reward_extra_ai,
            'reward_level': cfg.reward_level,
        })

    if not goals:
        default_goals = [
            {'level': 'beginner', 'name': '7天入门', 'required_days': 7, 'icon': '🏅', 'name_cn': '口才新星'},
            {'level': 'advanced', 'name': '30天进阶', 'required_days': 30, 'icon': '🥈', 'name_cn': '表达达人'},
            {'level': 'expert', 'name': '60天达人', 'required_days': 60, 'icon': '🥇', 'name_cn': '演讲大师'},
            {'level': 'master', 'name': '100天大师', 'required_days': 100, 'icon': '👑', 'name_cn': '口才王者'},
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
                'reward_extra_ai': 0,
                'reward_level': '',
            })

    return ok({
        'current_level': current_level,
        'current_level_label': LEVEL_LABELS.get(current_level, current_level),
        'goals': goals,
    })
