"""后台管理 — 素材管理（训练题库 + 推荐位）"""
from flask import request
from flask_jwt_extended import get_jwt_identity
from . import admin_bp
from ...extensions import db
from ...models.training import TrainingItem
from ...models.common import RecommendConfig
from ...services.admin_log import log_operation
from ...utils import ok, fail, paginated


def _admin_id():
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('admin_id')
    return None


# ==================== 训练题库 CRUD ====================

@admin_bp.route('/training-items', methods=['GET'])
def list_training_items():
    """训练题列表（分页+筛选+搜索）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    category = request.args.get('category')
    difficulty = request.args.get('difficulty', type=int)
    status = request.args.get('status')
    source = request.args.get('source')
    keyword = request.args.get('keyword', '').strip()

    query = TrainingItem.query
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if source:
        query = query.filter_by(source=source)
    if status:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            db.or_(
                TrainingItem.title.contains(keyword),
                TrainingItem.tags.contains(keyword)
            )
        )

    total = query.count()
    items = query.order_by(TrainingItem.sort_order.asc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return paginated(
        [it.to_dict() for it in items],
        {'page': page, 'page_size': page_size, 'total': total}
    )


@admin_bp.route('/training-items', methods=['POST'])
def create_training_item():
    """新增训练题"""
    data = request.get_json()
    if not data.get('title') or not data.get('sample_text'):
        return fail(400, '标题和范文文本不能为空')
    if not data.get('category'):
        return fail(400, '请选择分类')

    item = TrainingItem(
        category=data['category'],
        sub_category=data.get('sub_category', ''),
        title=data['title'].strip(),
        difficulty=data.get('difficulty', 1),
        sample_text=data['sample_text'].strip(),
        tags=data.get('tags', []),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 'online'),
            source=data.get('source', 'manual')
    )
    db.session.add(item)
    db.session.commit()
    log_operation(_admin_id(), '新增素材', '训练题库', item.id, {'title': item.title})
    db.session.commit()
    return ok(item.to_dict())


@admin_bp.route('/training-items/<int:item_id>', methods=['PUT'])
def update_training_item(item_id):
    """编辑训练题"""
    item = TrainingItem.query.get_or_404(item_id)
    data = request.get_json()

    if 'title' in data: item.title = data['title'].strip()
    if 'category' in data: item.category = data['category']
    if 'sub_category' in data: item.sub_category = data.get('sub_category', '')
    if 'difficulty' in data: item.difficulty = data['difficulty']
    if 'sample_text' in data: item.sample_text = data['sample_text'].strip()
    if 'tags' in data: item.tags = data['tags']
    if 'sort_order' in data: item.sort_order = data['sort_order']
    if 'source' in data: item.source = data['source']
    if 'status' in data: item.status = data['status']

    db.session.commit()
    log_operation(_admin_id(), '编辑素材', '训练题库', item.id, {'title': item.title})
    db.session.commit()
    return ok(item.to_dict())


@admin_bp.route('/training-items/<int:item_id>', methods=['DELETE'])
def delete_training_item(item_id):
    """删除训练题"""
    item = TrainingItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return ok({'message': '已删除'})


@admin_bp.route('/training-items/<int:item_id>/status', methods=['PATCH'])
def toggle_status(item_id):
    """上架/下架"""
    item = TrainingItem.query.get_or_404(item_id)
    data = request.get_json()
    item.status = data.get('status', 'offline')
    db.session.commit()
    return ok(item.to_dict())


@admin_bp.route('/training-items/batch-status', methods=['POST'])
def batch_toggle():
    """批量上下架"""
    data = request.get_json()
    ids = data.get('ids', [])
    status = data.get('status', 'offline')
    TrainingItem.query.filter(TrainingItem.id.in_(ids)).update(
        {'status': status}, synchronize_session=False
    )
    db.session.commit()
    return ok({'message': f'已批量{status}'})


@admin_bp.route('/training-items/<int:item_id>/upload-audio', methods=['POST'])
def upload_sample_audio(item_id):
    """上传范本音频"""
    item = TrainingItem.query.get_or_404(item_id)
    # TODO: 实际文件上传到OSS
    data = request.get_json()
    url = data.get('audio_url', '')
    if url:
        item.sample_audio_url = url
        db.session.commit()
    return ok({'sample_audio_url': item.sample_audio_url})


# ==================== 推荐位配置 ====================

@admin_bp.route('/recommend-config', methods=['GET'])
def get_recommend():
    """获取推荐位配置"""
    configs = RecommendConfig.query.order_by(RecommendConfig.slot.asc()).all()
    return ok({
        'slots': [
            {
                'slot': c.slot,
                'training_item_id': c.training_item_id,
                'custom_title': c.custom_title,
                'refresh_mode': c.refresh_mode
            } for c in configs
        ]
    })


@admin_bp.route('/recommend-config', methods=['PUT'])
def update_recommend():
    """更新推荐位配置"""
    data = request.get_json()
    slots = data.get('slots', [])
    for s in slots:
        config = RecommendConfig.query.filter_by(slot=s['slot']).first()
        if config:
            config.training_item_id = s.get('training_item_id')
            config.custom_title = s.get('custom_title')
            config.refresh_mode = s.get('refresh_mode', 'manual')
    db.session.commit()
    return ok({'message': '保存成功'})
