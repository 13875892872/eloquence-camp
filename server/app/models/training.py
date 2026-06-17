"""训练题模型"""
from ..extensions import db
from datetime import datetime


class TrainingItem(db.Model):
    __tablename__ = 'training_items'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False)
    sub_category = db.Column(db.String(30))
    title = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.SmallInteger, default=1)
    sample_text = db.Column(db.Text, nullable=False)
    sample_audio_url = db.Column(db.String(512))
    tags = db.Column(db.JSON)
    status = db.Column(db.String(20), default='online')
    source = db.Column(db.String(20), default='manual')  # 'manual' | 'ai_generated'
    practice_count = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'sub_category': self.sub_category,
            'title': self.title,
            'difficulty': self.difficulty,
            'sample_text': self.sample_text,
            'sample_audio_url': self.sample_audio_url,
            'tags': self.tags,
            'practice_count': self.practice_count,
            'sort_order': self.sort_order,
            'status': self.status,
            'source': self.source or 'manual',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
