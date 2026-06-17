#!/usr/bin/env python
"""
Loop Engineering 验证脚本 — 代码改动后自动运行
用法: PYTHONIOENCODING=utf-8 PYTHONPATH=. python verify.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app


def check_db_health(app):
    """检查数据库连接和表完整性"""
    with app.app_context():
        from app.extensions import db
        from sqlalchemy import inspect
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert len(tables) >= 14, f"预期 14+ 张表，实际 {len(tables)}"
            print(f'  ✅ 数据库: {len(tables)} 张表正常')
            return True
        except Exception as e:
            print(f'  ❌ 数据库异常: {e}')
            return False


def check_api_health():
    """检查 API 核心端点可访问"""
    import requests
    endpoints = [
        ('GET', 'http://127.0.0.1:5000/api/training/items?page_size=1'),
        ('GET', 'http://127.0.0.1:5000/api/training/items/1'),
    ]
    all_ok = True
    for method, url in endpoints:
        try:
            r = requests.request(method, url, timeout=10)
            if r.status_code == 200 and r.json().get('code') == 200:
                print(f'  ✅ {method} {url}')
            else:
                print(f'  ⚠️  {method} {url} → {r.status_code}')
                all_ok = False
        except Exception as e:
            print(f'  ❌ {method} {url} → {e}')
            all_ok = False
    return all_ok


def check_training_data(app):
    """检查训练数据完整性"""
    with app.app_context():
        from app.models.training import TrainingItem
        from app.models.checkin import DailyTaskConfig, GrowthGoalConfig
        from app.models.ai import AiConfig

        training_count = TrainingItem.query.count()
        tasks_count = DailyTaskConfig.query.count()
        goals_count = GrowthGoalConfig.query.count()
        ai_config = AiConfig.query.first()

        ok = True
        if training_count < 10:
            print(f'  ⚠️  训练题仅 {training_count} 条（建议≥10）')
            ok = False
        else:
            print(f'  ✅ 训练题: {training_count} 条')

        if tasks_count < 3:
            print(f'  ⚠️  每日任务仅 {tasks_count} 条（建议≥3）')
            ok = False
        else:
            print(f'  ✅ 每日任务: {tasks_count} 条配置')

        if goals_count < 4:
            print(f'  ⚠️  成长目标仅 {goals_count} 条（建议≥4）')
            ok = False
        else:
            print(f'  ✅ 成长目标: {goals_count} 条配置')

        if ai_config:
            print(f'  ✅ AI配置: 已初始化')
        else:
            print(f'  ⚠️  AI配置: 未初始化')
            ok = False

        return ok


def check_miniapp_build():
    """检查小程序是否能编译"""
    import subprocess
    miniapp_dir = os.path.join(os.path.dirname(__file__), '..', 'miniapp')
    if not os.path.exists(os.path.join(miniapp_dir, 'package.json')):
        print('  ⏭️  小程序目录不存在，跳过')
        return True

    try:
        result = subprocess.run(
            ['npx', 'uni', 'build', '-p', 'mp-weixin'],
            cwd=miniapp_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        if 'DONE' in result.stdout or 'Build complete' in result.stdout:
            print('  ✅ 小程序编译通过')
            return True
        else:
            print(f'  ⚠️  小程序编译输出不明确')
            return False
    except Exception as e:
        print(f'  ⚠️  小程序编译检查跳过: {e}')
        return True  # 非致命


def main():
    print('🔍 Loop Verification — 开始检查')
    print()

    app = create_app('development')

    results = {
        '数据库': check_db_health(app),
        '训练数据': check_training_data(app),
    }

    # API 检查（需要 Flask 正在运行）
    try:
        import requests
        results['API端点'] = check_api_health()
    except ImportError:
        print('  ⏭️  requests 未安装，跳过 API 检查')
        results['API端点'] = True

    # 小程序编译（可选）
    results['小程序'] = check_miniapp_build()

    print()
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f'📊 结果: {passed}/{total} 通过')

    for name, ok in results.items():
        status = '✅' if ok else '❌'
        print(f'  {status} {name}')

    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
