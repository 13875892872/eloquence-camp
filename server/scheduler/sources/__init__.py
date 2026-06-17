"""
源注册表 — 汇集所有素材源
"""
from .news_60s import News60sSource
from .hot_topics import HotTopicsSource
from .quotes import QuotesSource
from .rss_feeds import RssFeedsSource

SOURCE_REGISTRY = {
    'news_60s':   News60sSource,
    'hot_topics': HotTopicsSource,
    'quotes':     QuotesSource,
    'rss_feeds':  RssFeedsSource,
}


def get_enabled_sources(config: dict):
    """
    根据配置实例化所有已启用的源
    返回 BaseSource 实例列表
    """
    sources_config = config.get('sources', {})
    instances = []
    for name, cls in SOURCE_REGISTRY.items():
        src_cfg = sources_config.get(name, {})
        if src_cfg.get('enabled', False):
            instances.append(cls(src_cfg))
    return instances
