"""
AI文案模块 — 生成 / 配额 / 历史
"""
import json
from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..extensions import db
from ..models.ai import AiTextRecord, AiConfig
from ..models.user import UserQuota
from ..services.qwen_client import qwen_client
from ..utils import ok, fail, paginated

bp = Blueprint('ai_text', __name__)


def _get_user_id():
    """从JWT获取用户ID（可选登录）"""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return int(identity) if identity else None
    except Exception:
        return None


def _check_and_deduct_quota(user_id):
    """检查并扣减用户AI次数，返回(是否可生成, 剩余次数, 错误信息)"""
    quota = UserQuota.query.filter_by(user_id=user_id).first()
    if not quota:
        quota = UserQuota(user_id=user_id)
        db.session.add(quota)
        db.session.flush()

    # 重置每日计数
    today = date.today()
    if quota.last_reset_date != today:
        quota.daily_ai_used = 0
        quota.last_reset_date = today

    remaining = quota.daily_ai_quota + quota.extra_quota - quota.daily_ai_used
    if remaining <= 0:
        return False, 0, '今日免费次数已用完，完成打卡可获取额外次数'

    quota.daily_ai_used += 1
    db.session.commit()
    return True, remaining - 1, ''


@bp.route('/quota', methods=['GET'])
def get_quota():
    """获取AI配额"""
    user_id = _get_user_id()
    if not user_id:
        return ok({'daily_quota': 3, 'daily_used': 0, 'remaining': 3})

    quota = UserQuota.query.filter_by(user_id=user_id).first()
    if not quota:
        return ok({'daily_quota': 3, 'daily_used': 0, 'remaining': 3})

    today = date.today()
    if quota.last_reset_date != today:
        quota.daily_ai_used = 0

    remaining = max(0, quota.daily_ai_quota + quota.extra_quota - quota.daily_ai_used)
    return ok({
        'daily_quota': quota.daily_ai_quota,
        'daily_used': quota.daily_ai_used,
        'remaining': remaining,
        'extra_from_checkin': quota.extra_quota
    })


@bp.route('/generate', methods=['POST'])
def generate():
    """AI生成文案"""
    user_id = _get_user_id()
    data = request.get_json()

    scene_type = data.get('scene_type', 'speech')
    topic = data.get('topic', '').strip()
    if not topic:
        return fail(400, '请输入主题')

    # 检查配额
    if user_id:
        ok_gen, remaining, err = _check_and_deduct_quota(user_id)
        if not ok_gen:
            return fail(400, err)
    else:
        remaining = 0

    # 调用 Qwen
    scene_desc = data.get('scene_desc', '')
    duration = data.get('duration', '3min')
    style = data.get('style', '专业正式')
    extra = data.get('extra_notes', '')

    result = qwen_client.generate_text(
        scene_type=scene_type, topic=topic,
        scene_desc=scene_desc, duration=duration,
        style=style, extra_notes=extra
    )

    if not result['success']:
        # 退还次数
        if user_id:
            quota = UserQuota.query.filter_by(user_id=user_id).first()
            if quota and quota.daily_ai_used > 0:
                quota.daily_ai_used -= 1
                db.session.commit()
        return fail(500, result.get('error', 'AI生成失败，请稍后重试'))

    content = result['content']

    # 尝试解析JSON
    title = topic
    tips = ''
    try:
        parsed = json.loads(content)
        title = parsed.get('title', topic)
        content = parsed.get('content', content)
        tips = parsed.get('tips', '')
    except (json.JSONDecodeError, TypeError):
        pass

    # 保存记录
    if user_id:
        record = AiTextRecord(
            user_id=user_id,
            scene_type=scene_type,
            input_params=data,
            generated_content=content,
            title=title
        )
        db.session.add(record)
        db.session.commit()

    return ok({
        'id': record.id if user_id else 0,
        'title': title,
        'content': content,
        'estimated_duration': duration,
        'key_points': [],
        'tips': tips,
        'remaining_quota': remaining
    })


@bp.route('/history', methods=['GET'])
def history():
    """获取AI文案历史"""
    user_id = _get_user_id()
    if not user_id:
        return ok({'items': [], 'pagination': {'page': 1, 'page_size': 20, 'total': 0}})

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = AiTextRecord.query.filter_by(user_id=user_id).order_by(AiTextRecord.created_at.desc())
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    return paginated(
        [r.to_dict() for r in records],
        {'page': page, 'page_size': page_size, 'total': total}
    )


@bp.route('/history/<int:record_id>', methods=['GET'])
def get_history_detail(record_id):
    """获取AI文案详情"""
    record = AiTextRecord.query.get_or_404(record_id)
    return ok(record.to_dict())


SCENE_CATEGORY = {
    'speech': 'speech',
    'short_video': 'short_video',
    'livestream': 'livestream',
    'opening': 'speech',
    'interview': 'interview',
}


@bp.route('/import-practice', methods=['POST'])
def import_practice():
    """将 AI 文案导入为个人练习素材"""
    user_id = _get_user_id()
    if not user_id:
        return fail(401, '请先登录')

    data = request.get_json() or {}
    title = (data.get('title') or data.get('topic') or 'AI练习稿').strip()[:100]
    content = (data.get('content') or '').strip()
    if not content:
        return fail(400, '文案内容不能为空')

    scene_type = data.get('scene_type', 'speech')
    category = SCENE_CATEGORY.get(scene_type, 'speech')

    from ..models.training import TrainingItem
    item = TrainingItem(
        category=category,
        sub_category='AI导入',
        title=title,
        difficulty=1,
        sample_text=content[:3000],
        tags=['AI导入', '自定义'],
        status='online',
        source='user_custom',
        owner_user_id=user_id,
        sort_order=9999,
    )
    db.session.add(item)
    db.session.commit()

    return ok({
        'training_item_id': item.id,
        'title': item.title,
        'message': '已导入练习库',
    })
