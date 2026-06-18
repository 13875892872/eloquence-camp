"""后台管理 — 登录 & 数据看板"""
import bcrypt
from datetime import date, timedelta, datetime
from flask import request
from flask_jwt_extended import create_access_token
from sqlalchemy import func
from . import admin_bp
from ...extensions import db
from ...models.admin import AdminUser
from ...models.user import User
from ...models.training import TrainingItem
from ...models.common import PracticeRecord
from ...models.checkin import CheckinRecord
from ...models.ai import AiTextRecord
from ...utils import ok, fail


@admin_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return ok()
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return fail(400, '账号和密码不能为空')

    admin = AdminUser.query.filter_by(username=username).first()
    if not admin or not bcrypt.checkpw(password.encode(), admin.password_hash.encode()):
        return fail(401, '账号或密码错误')

    token = create_access_token(identity={'admin_id': admin.id, 'role': admin.role})
    return ok({
        'token': token,
        'admin': {'id': admin.id, 'username': admin.username, 'role': admin.role},
        'expires_in': 86400
    })


@admin_bp.route('/change-password', methods=['PUT'])
def change_password():
    data = request.get_json()
    old = data.get('old_password', '')
    new = data.get('new_password', '')
    if not old or not new or len(new) < 6:
        return fail(400, '新密码至少6位')
    return ok({'message': '密码修改成功'})


def _user_active_on(user_id, day):
    """用户在指定日期是否有练习或打卡"""
    if PracticeRecord.query.filter(
        PracticeRecord.user_id == user_id,
        func.date(PracticeRecord.created_at) == day
    ).first():
        return True
    if CheckinRecord.query.filter_by(user_id=user_id, task_date=day).filter(
        CheckinRecord.status.in_(['completed', 'makeup'])
    ).first():
        return True
    return False


def _calc_retention(days=30):
    today = date.today()
    cohort_start = today - timedelta(days=days)
    users = User.query.filter(func.date(User.created_at) >= cohort_start).all()
    total = len(users)
    if not total:
        return {'new_users': 0, 'd1_retention': 0, 'd7_retention': 0, 'd30_retention': 0}

    d1 = d7 = d30 = 0
    for u in users:
        reg = u.created_at.date() if u.created_at else today
        if _user_active_on(u.id, reg + timedelta(days=1)):
            d1 += 1
        if _user_active_on(u.id, reg + timedelta(days=7)):
            d7 += 1
        if _user_active_on(u.id, reg + timedelta(days=30)):
            d30 += 1

    return {
        'new_users': total,
        'd1_retention': round(d1 / total * 100, 1),
        'd7_retention': round(d7 / total * 100, 1),
        'd30_retention': round(d30 / total * 100, 1),
        'd1_count': d1,
        'd7_count': d7,
        'd30_count': d30,
    }


def _calc_checkin_heatmap():
    """近7天按星期×小时统计练习活跃度"""
    today = date.today()
    start = today - timedelta(days=6)
    records = PracticeRecord.query.filter(
        func.date(PracticeRecord.created_at) >= start
    ).all()

    grid = [[0] * 24 for _ in range(7)]
    for r in records:
        if not r.created_at:
            continue
        wd = r.created_at.weekday()  # 0=周一
        hr = r.created_at.hour
        grid[wd][hr] += 1

    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    data = []
    for wd in range(7):
        for hr in range(24):
            if grid[wd][hr] > 0:
                data.append([hr, wd, grid[wd][hr]])
    return {'weekdays': weekdays, 'data': data, 'max': max((c for row in grid for c in row), default=1)}


@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    period = request.args.get('period', 30, type=int)
    today = date.today()

    total_users = User.query.count()
    yesterday_new = User.query.filter(
        func.date(User.created_at) == today - timedelta(days=1)
    ).count()

    yesterday_active = db.session.query(func.count(func.distinct(PracticeRecord.user_id))).filter(
        func.date(PracticeRecord.created_at) == today - timedelta(days=1)
    ).scalar() or 0

    active_users = User.query.filter(User.total_days > 0).count() or 1
    yesterday_checkin = CheckinRecord.query.filter(
        CheckinRecord.task_date == today - timedelta(days=1),
        CheckinRecord.status.in_(['completed', 'makeup'])
    ).count()
    checkin_rate = round(yesterday_checkin / active_users * 100, 1)

    trends = []
    for i in range(period, -1, -1):
        d = today - timedelta(days=i)
        trends.append({
            'date': str(d),
            'new_users': User.query.filter(func.date(User.created_at) == d).count(),
            'dau': db.session.query(func.count(func.distinct(PracticeRecord.user_id))).filter(
                func.date(PracticeRecord.created_at) == d
            ).scalar() or 0,
            'checkin_rate': round(
                CheckinRecord.query.filter(
                    CheckinRecord.task_date == d,
                    CheckinRecord.status.in_(['completed', 'makeup'])
                ).count() / active_users * 100, 1
            )
        })

    top = db.session.query(
        TrainingItem.title, TrainingItem.practice_count
    ).filter(TrainingItem.status == 'online').order_by(
        TrainingItem.practice_count.desc()
    ).limit(10).all()

    today_text = AiTextRecord.query.filter(func.date(AiTextRecord.created_at) == today).count()
    today_speech = PracticeRecord.query.filter(func.date(PracticeRecord.created_at) == today).count()
    today_users = db.session.query(func.count(func.distinct(PracticeRecord.user_id))).filter(
        func.date(PracticeRecord.created_at) == today
    ).scalar() or 0

    return ok({
        'stats': {
            'total_users': total_users,
            'yesterday_new_users': yesterday_new,
            'yesterday_dau': yesterday_active,
            'yesterday_checkin_rate': checkin_rate
        },
        'trends': trends,
        'top_trainings': [{'title': t[0], 'practice_count': t[1]} for t in top],
        'retention': _calc_retention(30),
        'ai_usage': {
            'today_text_generations': today_text,
            'today_speech_evaluations': today_speech,
            'today_active_users': today_users,
        },
        'checkin_heatmap': _calc_checkin_heatmap(),
    })
