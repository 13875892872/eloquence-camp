"""
日志模块 — 按天滚动，保留30天，同时输出到控制台
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler


class SourceAdapter(logging.LoggerAdapter):
    """为日志添加 source 上下文的适配器"""
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        source = extra.get('source', '-')
        return f'[{source}] {msg}', kwargs


def setup_logger(config: dict) -> SourceAdapter:
    """创建并配置 logger"""
    log_dir = config.get('log_dir', 'scheduler/logs')

    # 确保日志目录存在
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(project_root, log_dir)
    os.makedirs(log_path, exist_ok=True)

    logger = logging.getLogger('scheduler')
    logger.setLevel(getattr(logging, config.get('log_level', 'INFO'), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return SourceAdapter(logger, {})

    # 文件 handler — 每天滚动，保留 30 天
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_path, 'scheduler.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return SourceAdapter(logger, {})
