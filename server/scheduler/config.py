"""
配置加载 — 三层覆盖：默认值 < config.json < 环境变量
"""
import os
import json


DEFAULT_CONFIG = {
    'sources': {
        'news_60s':   {'enabled': True,  'max_items': 5},
        'hot_topics': {'enabled': True,  'max_items': 3},
        'quotes':     {'enabled': True,  'max_items': 3},
        'rss_feeds':  {'enabled': False, 'max_items': 5,
                       'urls': [
                           'http://www.people.com.cn/rss/opml.xml',
                           'https://36kr.com/feed',
                           'https://www.huxiu.com/rss/0.xml',
                       ]},
    },
    'max_items_per_run': 12,          # 每轮最多入库条数
    'qwen_model': os.environ.get('QWEN_TEXT_MODEL', 'qwen-plus'),
    'qwen_temperature': 0.6,
    'qwen_timeout': 30,
    'inter_item_delay': 2.0,          # Qwen 调用间隔（秒），避免限流
    'default_status': 'online',       # 入库状态
    'cache_dir': 'scheduler/cache',
    'cache_ttl_days': 30,
    'log_dir': 'scheduler/logs',
    'log_level': 'INFO',
}


def _deep_merge(base, override):
    """深度合并两个 dict，override 中的值覆盖 base"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def load_config():
    """加载配置，返回合并后的 dict"""
    config = {}
    _deep_merge(config, DEFAULT_CONFIG)

    # 从 config.json 加载（可选）
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                _deep_merge(config, file_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f'[WARN] config.json 读取失败，使用默认配置: {e}')

    # 环境变量覆盖
    env_overrides = {
        'max_items_per_run': 'SCHEDULER_MAX_ITEMS',
        'qwen_model': 'SCHEDULER_QWEN_MODEL',
        'qwen_temperature': 'SCHEDULER_QWEN_TEMPERATURE',
        'inter_item_delay': 'SCHEDULER_INTER_DELAY',
        'log_level': 'SCHEDULER_LOG_LEVEL',
    }
    for config_key, env_key in env_overrides.items():
        val = os.environ.get(env_key)
        if val is not None:
            target_type = type(config[config_key])
            if target_type is float:
                config[config_key] = float(val)
            elif target_type is int:
                config[config_key] = int(val)
            else:
                config[config_key] = val

    return config
