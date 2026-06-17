"""后台管理 — 消息推送（真实 DB + 微信 API）"""
from flask import request
from . import admin_bp
from ...extensions import db
from ...models.admin import PushRecord, PushTemplate
from ...models.user import User
from ...services.push import push_service
from ...utils import ok, fail, paginated


@admin_bp.route('/push-templates', methods=['GET'])
def get_templates():
    """获取推送模板配置（从数据库读取）"""
    templates = PushTemplate.query.order_by(PushTemplate.id).all()
    return ok({
        'templates': [
            {
                'id': t.id,
                'type': t.type,
                'name': t.name,
                'wx_template_id': t.wx_template_id or '',
                'push_time': t.push_time or '',
                'is_active': t.is_active
            } for t in templates
        ]
    })


@admin_bp.route('/push-templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """更新推送模板配置"""
    tpl = PushTemplate.query.get_or_404(template_id)
    data = request.get_json()

    if 'is_active' in data:
        tpl.is_active = data['is_active']
    if 'push_time' in data:
        tpl.push_time = data['push_time']
    if 'wx_template_id' in data:
        tpl.wx_template_id = data['wx_template_id']
    if 'name' in data:
        tpl.name = data['name']

    db.session.commit()
    return ok({'message': '模板配置已保存', 'template': {
        'id': tpl.id, 'name': tpl.name, 'is_active': tpl.is_active,
        'push_time': tpl.push_time, 'wx_template_id': tpl.wx_template_id
    }})


@admin_bp.route('/push/manual', methods=['POST'])
def manual_push():
    """手动推送消息"""
    data = request.get_json()
    template_type = data.get('template_type', 'new_material')
    title = data.get('title', '')
    content = data.get('content', '')
    target = data.get('target', 'all')

    # 查找模板配置
    tpl = PushTemplate.query.filter_by(type=template_type).first()
    wx_template_id = tpl.wx_template_id if tpl else ''

    # 获取目标用户
    if target == 'all':
        users = User.query.filter(
            User.subscribe_status == True,
            User.openid != '',
            User.openid.isnot(None)
        ).all()
    else:
        users = []

    target_count = len(users)

    # 创建推送记录
    record = PushRecord(
        template_type=template_type,
        title=title or (tpl.name if tpl else ''),
        content=content,
        target_count=target_count,
        reach_count=0,
        status='sending'
    )
    db.session.add(record)
    db.session.commit()

    # 调用微信推送
    if users and wx_template_id:
        result = push_service.send_batch(
            users=users,
            template_id=wx_template_id,
            data_builder=lambda u: {
                'thing1': {'value': title or '口才训练营'},
                'thing2': {'value': '新内容已上线'},
                'thing3': {'value': content or '点击查看最新训练素材！'},
            }
        )
        record.reach_count = result['success']
        record.status = 'success' if result['failed'] == 0 else 'partial'
    else:
        record.reach_count = 0
        record.status = 'success'  # 无用户或未配置模板ID，视为完成
        if not wx_template_id:
            record.error_msg = '模板 wx_template_id 未配置，消息未实际发送'

    db.session.commit()

    return ok({
        'push_id': record.id,
        'target_count': target_count,
        'reach_count': record.reach_count,
        'status': record.status
    })


@admin_bp.route('/push-records', methods=['GET'])
def list_push_records():
    """推送记录列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = PushRecord.query.order_by(PushRecord.created_at.desc())
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    return paginated(
        [
            {
                'id': r.id,
                'template_type': r.template_type,
                'title': r.title,
                'target_count': r.target_count,
                'reach_count': r.reach_count,
                'status': r.status,
                'error_msg': r.error_msg,
                'created_at': r.created_at.isoformat() if r.created_at else None
            } for r in records
        ],
        {'page': page, 'page_size': page_size, 'total': total}
    )
