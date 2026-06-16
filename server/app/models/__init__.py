"""
SQLAlchemy 数据模型 — 按依赖顺序导入，避免关系解析失败
"""
from ..extensions import db

# 基础表（无外键依赖）
from .user import User, UserQuota
from .training import TrainingItem

# 关系表（依赖上面的基础表）
from .common import PracticeRecord, UserFavorite, RecommendConfig
from .checkin import CheckinRecord, DailyTaskConfig, GrowthGoalConfig
from .ai import AiTextRecord, AiConfig
from .admin import AdminUser, OperationLog, PushRecord
