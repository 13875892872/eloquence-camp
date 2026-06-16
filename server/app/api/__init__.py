"""
蓝图注册
"""
from flask import Flask
from . import auth, training, checkin, ai_text, ai_speech, upload, user
from .admin import admin_bp


def register_blueprints(app: Flask):
    """注册所有蓝图"""
    # 小程序端 API
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(training.bp, url_prefix='/api/training')
    app.register_blueprint(checkin.bp, url_prefix='/api/checkin')
    app.register_blueprint(ai_text.bp, url_prefix='/api/ai-text')
    app.register_blueprint(ai_speech.bp, url_prefix='/api/ai-speech')
    app.register_blueprint(user.bp, url_prefix='/api/user')
    app.register_blueprint(upload.bp, url_prefix='/api/upload')

    # 后台管理端 API
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
