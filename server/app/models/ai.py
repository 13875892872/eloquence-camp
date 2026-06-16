"""AI相关模型"""
from ..extensions import db
from datetime import datetime


class AiTextRecord(db.Model):
    __tablename__ = 'ai_text_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    scene_type = db.Column(db.String(30), nullable=False)
    input_params = db.Column(db.JSON, nullable=False)
    generated_content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(200), default='')
    is_favorited = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'scene_type': self.scene_type,
            'title': self.title or '未命名',
            'content': self.generated_content,
            'input_params': self.input_params,
            'is_favorited': self.is_favorited,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AiConfig(db.Model):
    __tablename__ = 'ai_config'
    id = db.Column(db.Integer, primary_key=True)
    text_model = db.Column(db.String(50), default='qwen3-max')
    text_temperature = db.Column(db.Numeric(3, 2), default=0.70)
    text_max_tokens = db.Column(db.Integer, default=2000)
    text_timeout = db.Column(db.Integer, default=15)
    new_user_daily = db.Column(db.Integer, default=3)
    checkin_bonus = db.Column(db.Integer, default=1)
    reset_hour = db.Column(db.SmallInteger, default=0)
    weight_pronunciation = db.Column(db.SmallInteger, default=30)
    weight_fluency = db.Column(db.SmallInteger, default=25)
    weight_completeness = db.Column(db.SmallInteger, default=20)
    weight_content = db.Column(db.SmallInteger, default=15)
    weight_expressiveness = db.Column(db.SmallInteger, default=10)
    min_pass_score = db.Column(db.SmallInteger, default=60)
    prompt_templates = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
