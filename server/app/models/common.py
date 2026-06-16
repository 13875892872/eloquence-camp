"""通用模型"""
from ..extensions import db
from datetime import datetime


class PracticeRecord(db.Model):
    __tablename__ = 'practice_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    training_item_id = db.Column(db.Integer, db.ForeignKey('training_items.id', ondelete='SET NULL'))
    audio_url = db.Column(db.String(512), nullable=False)
    duration = db.Column(db.Integer, default=0)
    ai_score = db.Column(db.SmallInteger)
    dimension_scores = db.Column(db.JSON)
    ai_feedback = db.Column(db.Text)
    source = db.Column(db.String(20), default='free_practice')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'training_item_id': self.training_item_id,
            'audio_url': self.audio_url,
            'duration': self.duration,
            'ai_score': self.ai_score,
            'dimension_scores': self.dimension_scores,
            'ai_feedback': self.ai_feedback,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    item_type = db.Column(db.String(30), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'item_type', 'item_id', name='uk_user_type_item'),)


class RecommendConfig(db.Model):
    __tablename__ = 'recommend_config'
    id = db.Column(db.Integer, primary_key=True)
    slot = db.Column(db.SmallInteger, unique=True, nullable=False)
    training_item_id = db.Column(db.Integer, db.ForeignKey('training_items.id', ondelete='SET NULL'))
    custom_title = db.Column(db.String(100))
    refresh_mode = db.Column(db.String(20), default='manual')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
