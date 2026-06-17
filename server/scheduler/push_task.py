"""
定时推送任务 — 每日提醒 / 新素材通知

用法:
    cd server
    PYTHONIOENCODING=utf-8 PYTHONPATH=. python scheduler/push_task.py
    PYTHONIOENCODING=utf-8 PYTHONPATH=. python scheduler/push_task.py --type daily_remind
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.admin import PushTemplate, PushRecord
from app.services.push import push_service


def run_daily_remind():
    """每日练习提醒 — 推送给所有已订阅用户"""
    tpl = PushTemplate.query.filter_by(type='daily_remind', is_active=True).first()
    if not tpl or not tpl.wx_template_id:
        print('[SKIP] 每日提醒模板未配置或未启用')
        return {'total': 0, 'success': 0, 'failed': 0}

    users = User.query.filter(
        User.subscribe_status == True,
        User.openid != '',
        User.openid.isnot(None)
    ).all()

    if not users:
        print('[SKIP] 没有已订阅的用户')
        return {'total': 0, 'success': 0, 'failed': 0}

    print(f'[PUSH] 每日提醒 → {len(users)} 个用户')
    result = push_service.send_batch(
        users=users,
        template_id=tpl.wx_template_id,
        data_builder=lambda u: {
            'thing1': {'value': '每日口才练习'},
            'time2': {'value': '20:00'},
            'thing3': {'value': '坚持每日打卡，口才步步提升！'},
        },
        page='pages/checkin/index'
    )

    # 记录推送
    record = PushRecord(
        template_type='daily_remind',
        title='每日练习提醒',
        content='系统自动推送',
        target_count=result['total'],
        reach_count=result['success'],
        status='success' if result['failed'] == 0 else 'partial'
    )
    db.session.add(record)
    db.session.commit()

    print(f'[DONE] 成功:{result["success"]} 失败:{result["failed"]}')
    return result


def run_new_material():
    """新素材通知 — 仅推送给已订阅用户（低频）"""
    tpl = PushTemplate.query.filter_by(type='new_material', is_active=True).first()
    if not tpl or not tpl.wx_template_id:
        print('[SKIP] 新素材通知模板未配置或未启用')
        return {'total': 0, 'success': 0, 'failed': 0}

    users = User.query.filter(
        User.subscribe_status == True,
        User.openid != '',
        User.openid.isnot(None)
    ).all()

    if not users:
        print('[SKIP] 没有已订阅的用户')
        return {'total': 0, 'success': 0, 'failed': 0}

    # 获取最近新增的素材标题
    from app.models.training import TrainingItem
    recent = TrainingItem.query.order_by(TrainingItem.created_at.desc()).first()
    title = f'「{recent.title}」等新素材已上线' if recent else '新训练素材已上线'

    print(f'[PUSH] 新素材通知 → {len(users)} 个用户')
    result = push_service.send_batch(
        users=users,
        template_id=tpl.wx_template_id,
        data_builder=lambda u: {
            'thing1': {'value': title[:20]},
            'thing2': {'value': '口才训练营'},
            'thing3': {'value': '快来挑战新题目，提升口才！'},
        },
        page='pages/training/index'
    )

    record = PushRecord(
        template_type='new_material',
        title='新素材上线通知',
        content=title,
        target_count=result['total'],
        reach_count=result['success'],
        status='success' if result['failed'] == 0 else 'partial'
    )
    db.session.add(record)
    db.session.commit()

    print(f'[DONE] 成功:{result["success"]} 失败:{result["failed"]}')
    return result


def main():
    parser = argparse.ArgumentParser(description='定时推送任务')
    parser.add_argument('--type', default='daily_remind',
                       choices=['daily_remind', 'new_material', 'all'],
                       help='推送类型')
    args = parser.parse_args()

    app = create_app(os.environ.get('FLASK_ENV', 'development'))

    with app.app_context():
        if args.type in ('daily_remind', 'all'):
            run_daily_remind()
        if args.type in ('new_material', 'all'):
            run_new_material()

    print('推送任务完成')


if __name__ == '__main__':
    main()
