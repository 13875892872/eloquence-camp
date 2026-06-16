"""后台管理 — 用户管理"""
from datetime import date, timedelta
from flask import request
from . import admin_bp
from ...extensions import db
from ...models.user import User, UserQuota
from ...models.checkin import CheckinRecord
from ...models.common import PracticeRecord
from ...models.ai import AiTextRecord
from ...utils import ok, fail, paginated


@admin_bp.route('/users', methods=['GET'])
def list_users():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '').strip()
    growth_level = request.args.get('growth_level', '').strip()

    query = User.query
    if keyword:
        query = query.filter(
            db.or_(User.nickname.contains(keyword), User.id == keyword if keyword.isdigit() else False)
        )
    if growth_level:
        query = query.filter_by(growth_level=growth_level)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for u in users:
        quota = UserQuota.query.filter_by(user_id=u.id).first()
        result.append({
            'id': u.id,
            'nickname': u.nickname or f'用户{u.id}',
            'avatar_url': u.avatar_url,
            'growth_level': u.growth_level,
            'total_days': u.total_days,
            'continuous_days': u.continuous_days,
            'remaining_ai': quota.remaining_today if quota else 3,
            'created_at': u.created_at.isoformat() if u.created_at else None
        })

    return paginated(result, {'page': page, 'page_size': page_size, 'total': total})


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def user_detail(user_id):
    """用户详情"""
    user = User.query.get_or_404(user_id)

    # 最近30天打卡
    today = date.today()
    recent_checkins = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        record = CheckinRecord.query.filter_by(user_id=user_id, task_date=d).first()
        recent_checkins.append({
            'date': str(d),
            'status': record.status if record else 'empty'
        })

    # 最近练习
    practices = PracticeRecord.query.filter_by(user_id=user_id).order_by(
        PracticeRecord.created_at.desc()
    ).limit(10).all()

    # 最近AI生成
    ai_texts = AiTextRecord.query.filter_by(user_id=user_id).order_by(
        AiTextRecord.created_at.desc()
    ).limit(10).all()

    # 权益
    quota = UserQuota.query.filter_by(user_id=user_id).first()

    return ok({
        'id': user.id,
        'nickname': user.nickname or f'用户{user.id}',
        'avatar_url': user.avatar_url,
        'growth_level': user.growth_level,
        'total_days': user.total_days,
        'continuous_days': user.continuous_days,
        'total_practice_minutes': user.total_practice_minutes,
        'ability_score': user.ability_score,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_active_at': practices[0].created_at.isoformat() if practices else None,
        'recent_checkins': recent_checkins,
        'recent_practices': [
            {
                'id': p.id,
                'title': p.training_item.title if p.training_item else '自由练习',
                'score': p.ai_score,
                'duration': p.duration,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in practices
        ],
        'recent_ai_texts': [
            {
                'id': a.id,
                'title': a.title or '未命名',
                'scene_type': a.scene_type,
                'created_at': a.created_at.isoformat() if a.created_at else None
            } for a in ai_texts
        ],
        'quota': {
            'daily_ai_quota': quota.daily_ai_quota if quota else 3,
            'daily_ai_used': quota.daily_ai_used if quota else 0,
            'extra_quota': quota.extra_quota if quota else 0,
            'remaining_today': quota.remaining_today if quota else 3
        }
    })


@admin_bp.route('/users/<int:user_id>/quota', methods=['PUT'])
def update_user_quota(user_id):
    """手动调整用户权益"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    reason = data.get('reason', '')

    quota = UserQuota.query.filter_by(user_id=user_id).first()
    if not quota:
        quota = UserQuota(user_id=user_id)
        db.session.add(quota)

    if 'growth_level' in data:
        user.growth_level = data['growth_level']
    if 'extra_ai_quota' in data:
        quota.extra_quota = data['extra_ai_quota']
    if 'daily_ai_quota' in data:
        quota.daily_ai_quota = data['daily_ai_quota']

    # TODO: 记录操作日志
    db.session.commit()
    return ok({'message': '权益调整成功', 'remaining_today': quota.remaining_today})
