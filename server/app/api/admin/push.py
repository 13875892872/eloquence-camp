"""后台管理 — 消息推送"""
from flask import request
from . import admin_bp
from ...extensions import db
from ...models.admin import PushRecord
from ...models.user import User
from ...utils import ok, fail, paginated


@admin_bp.route('/push-templates', methods=['GET'])
def get_templates():
    """获取推送模板配置"""
    return ok({
        'templates': [
            {
                'id': 1, 'type': 'daily_remind',
                'name': '每日练习提醒', 'push_time': '20:00',
                'wx_template_id': '', 'is_active': True
            },
            {
                'id': 2, 'type': 'checkin_success',
                'name': '打卡成功通知', 'push_time': '',
                'wx_template_id': '', 'is_active': True
            },
            {
                'id': 3, 'type': 'new_material',
                'name': '新素材上线通知', 'push_time': '',
                'wx_template_id': '', 'is_active': False
            }
        ]
    })


@admin_bp.route('/push-templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """更新推送模板"""
    data = request.get_json()
    # 一期简化为返回成功，实际应写入数据库
    return ok({'message': '模板配置已保存'})


@admin_bp.route('/push/manual', methods=['POST'])
def manual_push():
    """手动推送消息"""
    data = request.get_json()
    template_type = data.get('template_type', 'new_material')
    title = data.get('title', '')
    content = data.get('content', '')
    target = data.get('target', 'all')

    # 计算目标用户数
    target_count = User.query.count() if target == 'all' else 0

    push = PushRecord(
        template_type=template_type,
        title=title, content=content,
        target_count=target_count,
        reach_count=0,
        status='sending'
    )
    db.session.add(push)
    db.session.commit()

    # TODO: 实际调用微信订阅消息推送接口
    push.reach_count = target_count
    push.status = 'success'
    db.session.commit()

    return ok({
        'push_id': push.id,
        'target_count': target_count,
        'status': push.status
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
                'created_at': r.created_at.isoformat() if r.created_at else None
            } for r in records
        ],
        {'page': page, 'page_size': page_size, 'total': total}
    )
