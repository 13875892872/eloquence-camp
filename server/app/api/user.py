"""用户模块 — 个人信息 / 收藏 / 练习历史"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..extensions import db
from ..models.user import User
from ..models.common import PracticeRecord, UserFavorite
from ..models.training import TrainingItem
from ..models.ai import AiTextRecord
from ..utils import ok, fail, paginated

bp = Blueprint('user', __name__)


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
