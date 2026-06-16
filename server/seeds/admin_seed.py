"""初始化管理员账号"""
import bcrypt
from app import create_app
from app.extensions import db
from app.models.admin import AdminUser

app = create_app()

with app.app_context():
    db.create_all()
    if not AdminUser.query.filter_by(username='admin').first():
        password_hash = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        db.session.add(AdminUser(username='admin', password_hash=password_hash))
        db.session.commit()
        print('✅ 管理员账号已创建: admin / admin123')
    else:
        print('⚠️  管理员账号已存在，跳过')
