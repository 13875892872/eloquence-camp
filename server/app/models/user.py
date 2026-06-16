"""用户模型"""
from ..extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True, nullable=False)
    unionid = db.Column(db.String(64))
    nickname = db.Column(db.String(64), default='')
    avatar_url = db.Column(db.String(512), default='')
    total_days = db.Column(db.Integer, default=0)
    continuous_days = db.Column(db.Integer, default=0)
    total_practice_minutes = db.Column(db.Integer, default=0)
    ability_score = db.Column(db.JSON)
    growth_level = db.Column(db.String(20), default='newbie')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    quota = db.relationship('UserQuota', backref='user', uselist=False, lazy='joined')
    checkins = db.relationship('CheckinRecord', backref='user', lazy='dynamic')
    practice_records = db.relationship('PracticeRecord', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'growth_level': self.growth_level,
            'total_days': self.total_days,
            'continuous_days': self.continuous_days,
            'total_practice_minutes': self.total_practice_minutes,
            'ability_score': self.ability_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserQuota(db.Model):
    __tablename__ = 'user_quota'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    daily_ai_quota = db.Column(db.Integer, default=3)
    daily_ai_used = db.Column(db.Integer, default=0)
    extra_quota = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def remaining_today(self):
        return max(0, self.daily_ai_quota + self.extra_quota - self.daily_ai_used)
