"""用户模块 — 个人信息 / 收藏 / 练习历史"""
from datetime import datetime, timedelta, date
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func
from ..extensions import db
from ..models.user import User
from ..models.common import PracticeRecord, UserFavorite
from ..models.training import TrainingItem
from ..models.ai import AiTextRecord
from ..utils import ok, fail, paginated

bp = Blueprint('user', __name__)

LEADERBOARD_LIMIT = 10
LEADERBOARD_TYPES = {
    'week_duration': {'label': '本周训练时长', 'unit': '分钟'},
    'month_duration': {'label': '本月训练时长', 'unit': '分钟'},
    'continuous_days': {'label': '连续训练天数', 'unit': '天'},
}


def _period_start(lb_type):
    today = date.today()
    if lb_type == 'week_duration':
        monday = today - timedelta(days=today.weekday())
        return datetime.combine(monday, datetime.min.time())
    if lb_type == 'month_duration':
        return datetime.combine(today.replace(day=1), datetime.min.time())
    return None


def _user_item(rank, user, value):
    return {
        'rank': rank,
        'user_id': user.id,
        'nickname': user.nickname or '微信用户',
        'avatar_url': user.avatar_url,
        'growth_level': user.growth_level,
        'value': value,
    }


def _leaderboard_continuous():
    users = User.query.filter(User.continuous_days > 0)\
        .order_by(User.continuous_days.desc(), User.total_practice_minutes.desc())\
        .limit(LEADERBOARD_LIMIT).all()
    items = [_user_item(i + 1, u, u.continuous_days) for i, u in enumerate(users)]
    return items, lambda u: u.continuous_days


def _leaderboard_duration(lb_type):
    start = _period_start(lb_type)
    rows = db.session.query(
        User,
        func.coalesce(func.sum(PracticeRecord.duration), 0).label('total_seconds')
    ).join(PracticeRecord, PracticeRecord.user_id == User.id)\
     .filter(PracticeRecord.created_at >= start)\
     .group_by(User.id)\
     .having(func.sum(PracticeRecord.duration) > 0)\
     .order_by(func.sum(PracticeRecord.duration).desc())\
     .limit(LEADERBOARD_LIMIT).all()

    items = [_user_item(i + 1, user, int(total_seconds or 0) // 60) for i, (user, total_seconds) in enumerate(rows)]

    def value_fn(u):
        total = db.session.query(func.coalesce(func.sum(PracticeRecord.duration), 0))\
            .filter(PracticeRecord.user_id == u.id, PracticeRecord.created_at >= start).scalar()
        return int(total or 0) // 60

    return items, value_fn


def _my_data(user, value):
    return {
        'user_id': user.id,
        'nickname': user.nickname or '微信用户',
        'avatar_url': user.avatar_url,
        'growth_level': user.growth_level,
        'value': value,
    }


def _calc_my_rank(user, items, lb_type, value_fn):
    if not user:
        return None, None
    my_value = value_fn(user)
    if my_value <= 0:
        return None, None

    for item in items:
        if item['user_id'] == user.id:
            return item['rank'], _my_data(user, my_value)

    if lb_type == 'continuous_days':
        higher = User.query.filter(
            db.or_(
                User.continuous_days > user.continuous_days,
                db.and_(
                    User.continuous_days == user.continuous_days,
                    User.total_practice_minutes > user.total_practice_minutes
                )
            )
        ).count()
    else:
        start = _period_start(lb_type)
        my_total = db.session.query(func.coalesce(func.sum(PracticeRecord.duration), 0))\
            .filter(PracticeRecord.user_id == user.id, PracticeRecord.created_at >= start).scalar() or 0
        subq = db.session.query(
            PracticeRecord.user_id,
            func.sum(PracticeRecord.duration).label('total')
        ).filter(PracticeRecord.created_at >= start)\
         .group_by(PracticeRecord.user_id).subquery()
        higher = db.session.query(func.count()).select_from(subq)\
            .filter(subq.c.total > my_total).scalar() or 0

    return higher + 1, _my_data(user, my_value)


def _get_user():
    """从JWT获取当前用户"""
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user_id = int(identity) if identity else None
    return User.query.get(user_id) if user_id else None


@bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户个人信息"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')
    return ok(user.to_dict())


@bp.route('/profile/subscribe', methods=['PUT'])
def update_subscribe():
    """更新用户订阅状态"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')
    data = request.get_json()
    if 'subscribe_status' in data:
        user.subscribe_status = bool(data['subscribe_status'])
        db.session.commit()
    return ok({'subscribe_status': user.subscribe_status})


@bp.route('/favorites', methods=['GET'])
def list_favorites():
    """获取用户收藏列表"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    item_type = request.args.get('item_type', 'training_item')

    query = UserFavorite.query.filter_by(user_id=user.id, item_type=item_type)\
        .order_by(UserFavorite.created_at.desc())
    total = query.count()
    favs = query.offset((page - 1) * page_size).limit(page_size).all()

    # 关联查询实际条目
    items = []
    for f in favs:
        item_data = None
        if f.item_type == 'training_item':
            ti = TrainingItem.query.get(f.item_id)
            if ti:
                item_data = ti.to_dict()
        elif f.item_type == 'ai_text':
            ai = AiTextRecord.query.get(f.item_id)
            if ai:
                item_data = ai.to_dict()
        items.append({
            'id': f.id,
            'item_type': f.item_type,
            'item_id': f.item_id,
            'item': item_data,
            'created_at': f.created_at.isoformat() if f.created_at else None
        })

    return paginated(items, {'page': page, 'page_size': page_size, 'total': total})


@bp.route('/favorites/toggle', methods=['POST'])
def toggle_favorite():
    """切换收藏状态"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    data = request.get_json()
    item_type = data.get('item_type', 'training_item')
    item_id = data.get('item_id')
    if not item_id:
        return fail(400, 'item_id不能为空')

    existing = UserFavorite.query.filter_by(
        user_id=user.id, item_type=item_type, item_id=item_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return ok({'is_favorited': False, 'message': '已取消收藏'})
    else:
        fav = UserFavorite(user_id=user.id, item_type=item_type, item_id=item_id)
        db.session.add(fav)
        db.session.commit()
        return ok({'is_favorited': True, 'message': '已收藏'})


@bp.route('/practice-records', methods=['GET'])
def list_practices():
    """获取用户练习记录"""
    user = _get_user()
    if not user:
        return fail(401, '请先登录')

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = PracticeRecord.query.filter_by(user_id=user.id)\
        .order_by(PracticeRecord.created_at.desc())
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    # 关联训练题信息
    items = []
    for r in records:
        d = r.to_dict()
        if r.training_item_id:
            ti = TrainingItem.query.get(r.training_item_id)
            d['training_item'] = ti.to_dict() if ti else None
        else:
            d['training_item'] = None
        items.append(d)

    return paginated(items, {'page': page, 'page_size': page_size, 'total': total})

@bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    """训练排行榜 — 支持多维度，最多前10名"""
    lb_type = request.args.get('type', 'week_duration')
    if lb_type not in LEADERBOARD_TYPES:
        return fail(400, '无效的排行榜类型')

    user = None
    try:
        user = _get_user()
    except Exception:
        pass

    if lb_type == 'continuous_days':
        items, value_fn = _leaderboard_continuous()
    else:
        items, value_fn = _leaderboard_duration(lb_type)

    my_rank, my_data = _calc_my_rank(user, items, lb_type, value_fn)
    meta = LEADERBOARD_TYPES[lb_type]
    return ok({
        'type': lb_type,
        'type_label': meta['label'],
        'unit': meta['unit'],
        'items': items,
        'my_rank': my_rank,
        'my_data': my_data,
    })
