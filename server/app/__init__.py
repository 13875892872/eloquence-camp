"""
Flask 工厂函数
"""
from flask import Flask
from .config import config_map
from .extensions import init_extensions


def create_app(env: str = 'development') -> Flask:
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config_map.get(env, config_map['development']))

    # 初始化扩展 (db, migrate, cors, jwt)
    init_extensions(app)

    # 注册蓝图
    from .api import register_blueprints
    register_blueprints(app)

    # 注册错误处理
    from .utils.error_handler import register_error_handlers
    register_error_handlers(app)

    return app
