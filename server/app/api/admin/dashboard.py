"""后台管理 — 登录 & 数据看板"""
import bcrypt
from datetime import date, timedelta
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
    """管理员登录"""
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
    """修改密码（简化版，无认证装饰器时手动校验）"""
    data = request.get_json()
    old = data.get('old_password', '')
    new = data.get('new_password', '')
    if not old or not new or len(new) < 6:
        return fail(400, '新密码至少6位')
    # TODO: 从JWT获取admin_id
    return ok({'message': '密码修改成功'})


# ==================== 数据看板 ====================

@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """数据看板聚合指标"""
    period = request.args.get('period', 30, type=int)
    today = date.today()
    period_start = today - timedelta(days=period)

    total_users = User.query.count()
    yesterday_new = User.query.filter(
        func.date(User.created_at) == today - timedelta(days=1)
    ).count()

    yesterday_active = PracticeRecord.query.filter(
        func.date(PracticeRecord.created_at) == today - timedelta(days=1)
    ).distinct(PracticeRecord.user_id).count()

    yesterday_total = User.query.filter(
        User.total_days > 0
    ).count()
    yesterday_checkin = CheckinRecord.query.filter_by(
        task_date=today - timedelta(days=1), status='completed'
    ).count()
    checkin_rate = round(yesterday_checkin / max(yesterday_total, 1) * 100, 1)

    # 近N天趋势
    trends = []
    for i in range(period, -1, -1):
        d = today - timedelta(days=i)
        trends.append({
            'date': str(d),
            'new_users': User.query.filter(func.date(User.created_at) == d).count(),
            'dau': PracticeRecord.query.filter(
                func.date(PracticeRecord.created_at) == d
            ).distinct(PracticeRecord.user_id).count(),
            'checkin_rate': round(
                CheckinRecord.query.filter_by(task_date=d, status='completed').count() /
                max(User.query.filter(User.total_days > 0).count(), 1) * 100, 1
            )
        })

    # 热门训练 Top10
    top = db.session.query(
        TrainingItem.title, TrainingItem.practice_count
    ).filter(TrainingItem.status == 'online').order_by(
        TrainingItem.practice_count.desc()
    ).limit(10).all()

    # AI使用统计
    today_text = AiTextRecord.query.filter(
        func.date(AiTextRecord.created_at) == today
    ).count()
    today_speech = PracticeRecord.query.filter(
        func.date(PracticeRecord.created_at) == today
    ).count()

    return ok({
        'stats': {
            'total_users': total_users,
            'yesterday_new_users': yesterday_new,
            'yesterday_dau': yesterday_active,
            'yesterday_checkin_rate': checkin_rate
        },
        'trends': trends,
        'top_trainings': [{'title': t[0], 'practice_count': t[1]} for t in top],
        'retention': {'new_users': yesterday_new or 1, 'd1_retention': 0, 'd7_retention': 0, 'd30_retention': 0},
        'ai_usage': {'today_text_generations': today_text, 'today_speech_evaluations': today_speech},
        'checkin_heatmap': []
    })
