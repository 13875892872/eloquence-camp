"""
认证模块 — 微信登录 / JWT签发
"""
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from ..models.user import User
from ..extensions import db
from ..utils import ok, fail

bp = Blueprint('auth', __name__)


@bp.route('/wechat-login', methods=['POST'])
def wechat_login():
    """微信登录"""
    data = request.get_json()
    code = data.get('code')
    if not code:
        return fail(400, 'code不能为空')

    # TODO: 调用微信 code2Session 获取 openid
    # from ..services.wechat import code_to_session
    # session = code_to_session(code)
    # openid = session.get('openid')

    # 开发阶段使用 mock
    openid = f'mock_openid_{code}'

    if not openid:
        return fail(500, '微信登录失败')

    # 查找或创建用户
    user = User.query.filter_by(openid=openid).first()
    is_new = False
    if not user:
        user = User(openid=openid)
        db.session.add(user)
        db.session.flush()
        is_new = True

    # 签发JWT
    token = create_access_token(identity=str(user.id))

    db.session.commit()
    return ok({
        'token': token,
        'user': user.to_dict(),
        'is_new_user': is_new,
        'expires_in': 86400
    })


@bp.route('/sync-profile', methods=['PUT'])
def sync_profile():
    """同步微信用户信息"""
    data = request.get_json()
    return ok({'message': '同步成功'})
