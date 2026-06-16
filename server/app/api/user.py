"""用户模块 — 个人信息 / 收藏 / 练习历史"""
from flask import Blueprint
from ..utils import ok

bp = Blueprint('user', __name__)


@bp.route('/profile', methods=['GET'])
def get_profile():
    return ok({'message': 'TODO'})


@bp.route('/favorites', methods=['GET'])
def list_favorites():
    return ok({'items': [], 'pagination': {}})


@bp.route('/favorites/toggle', methods=['POST'])
def toggle_favorite():
    return ok({'is_favorited': True})


@bp.route('/practice-records', methods=['GET'])
def list_practices():
    return ok({'items': [], 'pagination': {}})
