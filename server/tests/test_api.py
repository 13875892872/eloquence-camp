"""核心 API 冒烟测试 — 内存 SQLite，不依赖外部服务"""
import json
import os
import unittest
from datetime import date, datetime

import bcrypt
from flask_jwt_extended import create_access_token

# 必须在 create_app 之前设置，避免连到本地开发库
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app
from app.extensions import db
from app.models.admin import AdminUser
from app.models.checkin import CheckinRecord, DailyTaskConfig
from app.models.common import PracticeRecord
from app.models.training import TrainingItem
from app.models.user import User, UserQuota


def _json(resp):
    return json.loads(resp.data)


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('development')
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()
            cls._seed()

    @classmethod
    def _seed(cls):
        user = User(openid='test_openid', nickname='测试用户', continuous_days=5)
        db.session.add(user)
        db.session.flush()
        db.session.add(UserQuota(user_id=user.id))
        cls.user_id = user.id
        cls.user_token = create_access_token(identity=str(user.id))

        pwd = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
        admin = AdminUser(username='test_admin', password_hash=pwd, role='super_admin')
        db.session.add(admin)

        db.session.add(DailyTaskConfig(
            task_index=1, title='跟读练习', min_duration=30, is_active=True
        ))
        db.session.add(TrainingItem(
            category='speech', sub_category='测试', title='测试素材',
            difficulty=1, sample_text='大家好', status='online',
        ))
        db.session.flush()
        training_id = TrainingItem.query.first().id

        rec = PracticeRecord(
            user_id=user.id,
            training_item_id=training_id,
            audio_url='https://example.com/a.mp3',
            duration=90,
            ai_score=85,
            created_at=datetime.utcnow(),
        )
        db.session.add(rec)
        db.session.commit()
        cls.practice_id = rec.id

    def setUp(self):
        self.auth = {'Authorization': f'Bearer {self.user_token}'}

    def test_leaderboard_types(self):
        for lb_type in ('week_duration', 'month_duration', 'continuous_days'):
            resp = self.client.get(f'/api/user/leaderboard?type={lb_type}', headers=self.auth)
            body = _json(resp)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(body['code'], 200)
            self.assertEqual(body['data']['type'], lb_type)
            self.assertLessEqual(len(body['data']['items']), 10)

    def test_leaderboard_invalid_type(self):
        resp = self.client.get('/api/user/leaderboard?type=invalid', headers=self.auth)
        body = _json(resp)
        self.assertEqual(body['code'], 400)

    def test_complete_task_with_practice(self):
        resp = self.client.post(
            '/api/checkin/complete-task',
            json={'task_index': 1, 'practice_record_id': self.practice_id},
            headers=self.auth,
        )
        body = _json(resp)
        self.assertEqual(body['code'], 200)
        self.assertTrue(body['data']['task_completed'])
        self.assertIn(1, body['data']['completed_tasks'])

    def test_complete_task_duration_too_short(self):
        resp = self.client.post(
            '/api/checkin/complete-task',
            json={'task_index': 1, 'duration': 10},
            headers=self.auth,
        )
        body = _json(resp)
        self.assertEqual(body['code'], 400)

    def test_import_practice(self):
        resp = self.client.post(
            '/api/ai-text/import-practice',
            json={
                'title': '我的面试稿',
                'content': '您好，我是……',
                'scene_type': 'interview',
            },
            headers=self.auth,
        )
        body = _json(resp)
        self.assertEqual(body['code'], 200)
        self.assertIn('training_item_id', body['data'])

        with self.app.app_context():
            item = TrainingItem.query.get(body['data']['training_item_id'])
            self.assertEqual(item.category, 'interview')
            self.assertEqual(item.owner_user_id, self.user_id)

    def test_calendar(self):
        with self.app.app_context():
            db.session.add(CheckinRecord(
                user_id=self.user_id,
                task_date=date.today(),
                status='completed',
                completed_tasks=[1],
            ))
            db.session.commit()

        resp = self.client.get('/api/checkin/calendar', headers=self.auth)
        body = _json(resp)
        self.assertEqual(body['code'], 200)
        self.assertGreaterEqual(body['data']['summary']['completed'], 1)

    def test_admin_dashboard(self):
        with self.app.app_context():
            admin = AdminUser.query.filter_by(username='test_admin').first()
            token = create_access_token(identity={'admin_id': admin.id, 'role': admin.role})

        resp = self.client.get(
            '/api/admin/dashboard?period=7',
            headers={'Authorization': f'Bearer {token}'},
        )
        body = _json(resp)
        self.assertEqual(body['code'], 200)
        self.assertIn('stats', body['data'])
        self.assertIn('retention', body['data'])
        self.assertIn('checkin_heatmap', body['data'])
        self.assertIn('weekdays', body['data']['checkin_heatmap'])


if __name__ == '__main__':
    unittest.main()
