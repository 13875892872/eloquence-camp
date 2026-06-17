"""
热搜话题 — 多平台热搜聚合 API
API: https://orz.ai/api/v1/dailynews/?platform=weibo
"""
from typing import List, Dict, Any
from ..base import BaseSource


class HotTopicsSource(BaseSource):
    name = 'hot_topics'
    label = '热搜话题'

    API_URL = 'https://orz.ai/api/v1/dailynews/?platform=weibo'

    def fetch(self) -> List[Dict[str, Any]]:
        resp = self._safe_get(self.API_URL, timeout=15)
        if resp is None:
            return []

        try:
            data = resp.json()
        except (ValueError, KeyError):
            return []

        # API 可能返回不同形状：可能是 list 或 {platforms: [...]}
        topics = []
        if isinstance(data, list):
            topics = data
        elif isinstance(data, dict):
            # 尝试从嵌套结构中提取
            for key in ('data', 'news', 'items', 'topics'):
                val = data.get(key)
                if isinstance(val, list):
                    topics = val
                    break
            if not topics:
                # 可能是 {platform_name: [...]} 结构
                for val in data.values():
                    if isinstance(val, list) and val:
                        topics = val
                        break

        max_items = self.config.get('max_items', 3)
        items = []
        for topic in topics[:max_items]:
            title = topic.get('title') or topic.get('name') or topic.get('keyword', '')
            digest = topic.get('digest') or topic.get('desc') or topic.get('summary', '')
            content = digest if digest else title

            if title and content:
                items.append(self._to_raw(
                    title=title,
                    content=content,
                    source_type='topic',
                    metadata={
                        'rank': topic.get('rank', 0),
                        'hot': topic.get('hot') or topic.get('hot_score', 0),
                        'url': topic.get('url', '')
                    }
                ))

        return items[:max_items]
