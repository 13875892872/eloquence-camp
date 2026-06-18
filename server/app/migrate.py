"""
轻量数据库迁移 — 补齐缺失列/表（SQLite / MySQL 通用）
运行: PYTHONIOENCODING=utf-8 PYTHONPATH=. python app/migrate.py
"""
from sqlalchemy import inspect, text
from app import create_app
from app.extensions import db

MIGRATIONS = [
    {
        'table': 'training_items',
        'column': 'owner_user_id',
        'sqlite': 'ALTER TABLE training_items ADD COLUMN owner_user_id INTEGER',
        'mysql': 'ALTER TABLE training_items ADD COLUMN owner_user_id INT NULL',
    },
    {
        'table': 'checkin_records',
        'column': 'status',
        'sqlite': "ALTER TABLE checkin_records ADD COLUMN status VARCHAR(20) DEFAULT 'pending'",
        'mysql': "ALTER TABLE checkin_records ADD COLUMN status VARCHAR(20) DEFAULT 'pending'",
    },
]


def column_exists(insp, table, column):
    try:
        cols = [c['name'] for c in insp.get_columns(table)]
        return column in cols
    except Exception:
        return False


def run_migrations():
    app = create_app()
    with app.app_context():
        db.create_all()
        insp = inspect(db.engine)
        dialect = db.engine.dialect.name
        applied = 0
        for m in MIGRATIONS:
            if column_exists(insp, m['table'], m['column']):
                continue
            sql = m['mysql'] if dialect == 'mysql' else m['sqlite']
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f'✅ {m["table"]}.{m["column"]}')
                applied += 1
            except Exception as e:
                db.session.rollback()
                print(f'⚠️  {m["table"]}.{m["column"]}: {e}')
        print(f'迁移完成，新增 {applied} 列')


if __name__ == '__main__':
    run_migrations()
