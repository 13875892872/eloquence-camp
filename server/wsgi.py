"""
启动入口
开发: python wsgi.py
生产: gunicorn wsgi:app -w 4 -b 0.0.0.0:5000
"""
import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=(env == 'development'))
