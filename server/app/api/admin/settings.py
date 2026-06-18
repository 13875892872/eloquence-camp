"""后台 — 操作日志"""
from flask import request
from ...models.admin import OperationLog
from ...utils import ok, paginated
from . import admin_bp


@admin_bp.route('/operation-logs', methods=['GET'])
def list_operation_logs():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = OperationLog.query.order_by(OperationLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for log in logs:
        items.append({
            'id': log.id,
            'action': log.action,
            'target_type': log.target_type,
            'target_id': log.target_id,
            'detail': log.detail,
            'time': log.created_at.strftime('%Y-%m-%d %H:%M') if log.created_at else '',
            'created_at': log.created_at.isoformat() if log.created_at else None,
        })

    return paginated(items, {'page': page, 'page_size': page_size, 'total': total})
