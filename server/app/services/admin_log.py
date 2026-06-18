"""后台操作日志"""
from ..extensions import db
from ..models.admin import OperationLog


def log_operation(admin_id, action, target_type, target_id=None, detail=None):
    entry = OperationLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail or {},
    )
    db.session.add(entry)
    db.session.flush()
    return entry
