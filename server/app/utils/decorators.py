"""
装饰器：登录校验 / 管理员校验
"""
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .response import fail


def login_required(fn):
    """小程序用户登录校验"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            kwargs['current_user_id'] = int(user_id) if isinstance(user_id, str) else user_id
            return fn(*args, **kwargs)
        except Exception:
            return fail(401, '请先登录')
    return wrapper


def admin_required(fn):
    """后台管理员登录校验"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if not identity or not identity.get('admin_id'):
                return fail(403, '无权限访问')
            kwargs['admin_id'] = identity['admin_id']
            return fn(*args, **kwargs)
        except Exception:
            return fail(401, '请先登录后台')
    return wrapper


def optional_login(fn):
    """可选登录（未登录也不报错）"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            kwargs['current_user_id'] = int(identity) if identity else None
        except Exception:
            kwargs['current_user_id'] = None
        return fn(*args, **kwargs)
    return wrapper
