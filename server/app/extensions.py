"""
Flask 扩展初始化
"""
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def init_extensions(app):
    """初始化所有 Flask 扩展"""
    # CORS 跨域 — 显式配置资源+方法，确保预检请求通过
    CORS(app,
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})
    # 额外：为所有请求添加 CORS 头，兜底 OPTIONS 预检
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,PATCH,OPTIONS'
        return response

    # 数据库
    db.init_app(app)

    # 数据库迁移
    migrate.init_app(app, db)

    # JWT
    jwt.init_app(app)

    # 导入所有模型，确保 migrate 能检测到
    with app.app_context():
        from .models import (User, UserQuota, TrainingItem,  # noqa
                            PracticeRecord, UserFavorite, RecommendConfig,
                            CheckinRecord, DailyTaskConfig, GrowthGoalConfig,
                            AiTextRecord, AiConfig,
                            AdminUser, OperationLog, PushRecord)
