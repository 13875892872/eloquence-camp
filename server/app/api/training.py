"""
训练题库模块
"""
from flask import Blueprint, request
from ..models.training import TrainingItem
from ..utils import ok, fail, paginated

bp = Blueprint('training', __name__)


@bp.route('/items', methods=['GET'])
def list_items():
    """训练题列表（分页+筛选）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    category = request.args.get('category')
    difficulty = request.args.get('difficulty', type=int)
    keyword = request.args.get('keyword')

    query = TrainingItem.query.filter_by(status='online')

    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if keyword:
        query = query.filter(
            TrainingItem.title.contains(keyword) |
            TrainingItem.tags.contains(keyword)
        )

    total = query.count()
    items = query.order_by(TrainingItem.sort_order.asc())\
                  .offset((page - 1) * page_size)\
                  .limit(page_size).all()

    return paginated(
        [item.to_dict() for item in items],
        {'page': page, 'page_size': page_size, 'total': total}
    )


@bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """训练题详情"""
    item = TrainingItem.query.get_or_404(item_id)
    return ok(item.to_dict())
