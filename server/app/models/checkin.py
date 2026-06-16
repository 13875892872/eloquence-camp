"""打卡相关模型"""
from ..extensions import db
from datetime import datetime


class CheckinRecord(db.Model):
    __tablename__ = 'checkin_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='completed')
    completed_tasks = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'task_date', name='uk_user_date'),)

    def to_dict(self):
        return {
            'id': self.id,
            'task_date': str(self.task_date),
            'status': self.status,
            'completed_tasks': self.completed_tasks,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DailyTaskConfig(db.Model):
    __tablename__ = 'daily_task_config'
    id = db.Column(db.Integer, primary_key=True)
    task_index = db.Column(db.SmallInteger, unique=True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    subtitle = db.Column(db.String(128), default='')
    min_duration = db.Column(db.Integer, default=60)
    source_type = db.Column(db.String(20), default='random')
    source_category = db.Column(db.String(30))
    source_difficulty_min = db.Column(db.SmallInteger, default=1)
    source_difficulty_max = db.Column(db.SmallInteger, default=3)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GrowthGoalConfig(db.Model):
    __tablename__ = 'growth_goal_config'
    id = db.Column(db.Integer, primary_key=True)
    goal_level = db.Column(db.String(20), unique=True, nullable=False)
    goal_name = db.Column(db.String(64), nullable=False)
    required_days = db.Column(db.Integer, nullable=False)
    reward_level = db.Column(db.String(30))
    reward_extra_ai = db.Column(db.Integer, default=0)
    badge_icon = db.Column(db.String(10), default='')
    badge_name = db.Column(db.String(30), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
