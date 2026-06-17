"""后台管理相关模型"""
from ..extensions import db
from datetime import datetime


class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='super_admin')
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id', ondelete='SET NULL'))
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer)
    detail = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PushRecord(db.Model):
    __tablename__ = 'push_records'
    id = db.Column(db.Integer, primary_key=True)
    template_type = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(100), default='')
    content = db.Column(db.Text)
    target_count = db.Column(db.Integer, default=0)
    reach_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='sending')
    error_msg = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PushTemplate(db.Model):
    __tablename__ = 'push_templates'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    wx_template_id = db.Column(db.String(64), default='')
    push_time = db.Column(db.String(5), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
