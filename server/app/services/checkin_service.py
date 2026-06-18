"""打卡业务逻辑"""
from datetime import date, timedelta
from ..extensions import db
from ..models.checkin import DailyTaskConfig, CheckinRecord
from ..models.common import PracticeRecord
from ..services.growth import apply_growth_rewards


DEFAULT_MIN_DURATION = {1: 30, 2: 60, 3: 60}


def get_task_config(task_index):
    cfg = DailyTaskConfig.query.filter_by(task_index=task_index, is_active=True).first()
    if cfg:
        return cfg
    return None


def min_duration_for(task_index):
    cfg = get_task_config(task_index)
    if cfg:
        return cfg.min_duration or 60
    return DEFAULT_MIN_DURATION.get(task_index, 60)


def validate_practice_for_task(user, task_index, practice_record_id=None, duration=None):
    """
    校验练习是否满足任务最低时长。
    返回 (ok, error_message, record)
    """
    min_dur = min_duration_for(task_index)
    today = date.today()

    if practice_record_id:
        rec = PracticeRecord.query.filter_by(id=practice_record_id, user_id=user.id).first()
        if not rec:
            return False, '练习记录不存在', None
        if (rec.created_at.date() if rec.created_at else today) != today:
            return False, '请完成今日练习后再打卡', None
        if (rec.duration or 0) < min_dur:
            return False, f'录音时长不足，请至少练习{min_dur}秒', None
        return True, '', rec

    if duration is not None and duration >= min_dur:
        return True, '', None

    return False, f'请至少练习{min_dur}秒', None


def can_unlock_task(task_index, completed_indices, task_configs):
    """任务是否已解锁（顺序完成）"""
    if not task_configs:
        return task_index == 1 or (task_index - 1) in completed_indices
    ordered = sorted(task_configs, key=lambda c: c.task_index)
    for i, cfg in enumerate(ordered):
        if cfg.task_index == task_index:
            if i == 0:
                return True
            prev = ordered[i - 1].task_index
            return prev in completed_indices
    return False


def finalize_daily_checkin(user, record, total_tasks):
    """
    当日全部任务首次完成时更新用户统计，返回 (goal_achieved_list, stats_dict)
    """
    if record.status in ('completed', 'makeup'):
        return [], None

    today = date.today()
    yesterday = today - timedelta(days=1)

    record.status = 'completed'
    user.total_days = (user.total_days or 0) + 1

    yesterday_record = CheckinRecord.query.filter_by(
        user_id=user.id, task_date=yesterday
    ).filter(CheckinRecord.status.in_(['completed', 'makeup'])).first()

    if yesterday_record or (user.continuous_days or 0) == 0:
        user.continuous_days = (user.continuous_days or 0) + 1
    else:
        user.continuous_days = 1

    today_records = PracticeRecord.query.filter(
        PracticeRecord.user_id == user.id,
        db.func.date(PracticeRecord.created_at) == str(today)
    ).all()
    today_seconds = sum(r.duration or 0 for r in today_records)
    user.total_practice_minutes = (user.total_practice_minutes or 0) + max(1, round(today_seconds / 60))

    newly_achieved = apply_growth_rewards(user)

    stats = {
        'continuous_days': user.continuous_days,
        'total_days': user.total_days,
        'total_minutes': user.total_practice_minutes,
    }
    return newly_achieved, stats
