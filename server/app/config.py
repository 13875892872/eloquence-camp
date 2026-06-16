"""
多环境配置
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)))

    # 阿里云 OSS
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', '')
    OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', '')
    OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
    OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME', '')

    # 阿里云百炼 (Qwen)
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')
    QWEN_TEXT_MODEL = os.environ.get('QWEN_TEXT_MODEL', 'qwen3-max')
    QWEN_FEEDBACK_MODEL = os.environ.get('QWEN_FEEDBACK_MODEL', 'qwen3-flash')

    # 阿里云语音评测
    ALIYUN_SPEECH_APP_KEY = os.environ.get('ALIYUN_SPEECH_APP_KEY', '')
    ALIYUN_SPEECH_ACCESS_KEY_ID = os.environ.get('ALIYUN_SPEECH_ACCESS_KEY_ID', '')
    ALIYUN_SPEECH_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_SPEECH_ACCESS_KEY_SECRET', '')

    # 微信小程序
    WECHAT_APPID = os.environ.get('WECHAT_APPID', '')
    WECHAT_SECRET = os.environ.get('WECHAT_SECRET', '')

    # 录音配置
    MAX_RECORDING_DURATION = 300  # 单次最长录音秒数(5分钟)
    MAX_RECORDING_SIZE_MB = 5
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a'}


class DevelopmentConfig(Config):
    DEBUG = True
    # 默认使用 SQLite 本地开发；有 MySQL 时通过 .env 的 DATABASE_URL 覆盖
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'eloquence_dev.db')
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
