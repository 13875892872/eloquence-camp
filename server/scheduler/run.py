#!/usr/bin/env python
"""
每日素材自动获取与加工 — 入口脚本

用法:
    cd server
    set PYTHONIOENCODING=utf-8
    set PYTHONPATH=.
    python scheduler/run.py

可配合 Windows 任务计划程序每日定时执行。
"""
import sys
import os

# 确保 server/ 在 sys.path 中以支持 from app import create_app
SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SERVER_DIR)

from app import create_app
from scheduler.config import load_config
from scheduler.logger import setup_logger
from scheduler.pipeline import Pipeline


def main():
    config = load_config()
    logger = setup_logger(config)

    logger.info('=' * 50, extra={'source': 'run'})
    logger.info('Daily Material Scheduler — Starting', extra={'source': 'run'})
    logger.info(
        f'Sources: {[k for k,v in config["sources"].items() if v.get("enabled")]}',
        extra={'source': 'run'}
    )
    logger.info(f'Max items: {config["max_items_per_run"]}', extra={'source': 'run'})
    logger.info(f'Qwen model: {config["qwen_model"]}', extra={'source': 'run'})

    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)

    with app.app_context():
        from app.extensions import db
        db.create_all()  # 确保表存在（幂等）

        pipeline = Pipeline(config, logger)
        summary = pipeline.run()

    logger.info(
        f'Done. Created {summary["created"]} new training items '
        f'(fetched {summary["total_fetched"]}, skipped {summary["skipped_db"]}, '
        f'failed {summary["failed"]})',
        extra={'source': 'run'}
    )
    logger.info('=' * 50, extra={'source': 'run'})

    # 返回状态码给外部调用者
    if summary['created'] == 0 and summary['failed'] > 0:
        sys.exit(1)  # 所有素材加工失败
    sys.exit(0)


if __name__ == '__main__':
    main()
