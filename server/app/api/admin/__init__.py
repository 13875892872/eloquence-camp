"""
后台管理 API 蓝图
"""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from . import dashboard, training, checkin, ai_config, user, push  # noqa
