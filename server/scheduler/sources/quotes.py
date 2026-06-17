"""
名言诗词 — 一言(Hitokoto) + 今日诗词(Jinrishici)
"""
import random
from typing import List, Dict, Any
from ..base import BaseSource


class QuotesSource(BaseSource):
    name = 'quotes'
    label = '名言诗词'

    HITOKOTO_URL = 'https://v1.hitokoto.cn/'
    JINRISHICI_URL = 'https://v2.jinrishici.com/one.json'

    # 一言类型映射
    HITOKOTO_TYPES = 'abcdefghijkl'  # 所有类型随机

    def _fetch_hitokoto(self) -> dict:
        """获取一条一言"""
        try:
            resp = self._safe_get(
                f'{self.HITOKOTO_URL}?c={random.choice(self.HITOKOTO_TYPES)}',
                timeout=10
            )
            if resp:
                data = resp.json()
                text = data.get('hitokoto', '')
                source = data.get('from', '')
                content = text
                if source:
                    content = f'"{text}" —— {source}'
                return self._to_raw(
                    title='',
                    content=content,
                    source_type='quote',
                    metadata={'tag': 'hitokoto'}
                )
        except Exception:
            pass
        return None

    def _fetch_jinrishici(self) -> dict:
        """获取一首今日诗词"""
        try:
            resp = self._safe_get(self.JINRISHICI_URL, timeout=10)
            if resp:
                data = resp.json()
                poem = data.get('data', {}) if 'data' in data else data
                content = poem.get('content', '')
                origin = poem.get('origin', '')
                author = poem.get('author', '')
                parts = [content]
                if author:
                    parts.append(f'—— {author}')
                if origin:
                    parts.append(f'《{origin}》')
                return self._to_raw(
                    title='',
                    content='\n'.join(parts),
                    source_type='poem',
                    metadata={'tag': 'jinrishici'}
                )
        except Exception:
            pass
        return None

    def fetch(self) -> List[Dict[str, Any]]:
        max_items = self.config.get('max_items', 3)
        items = []

        # 获取 2 条一言
        for _ in range(min(max_items - 1, 2)):
            hit = self._fetch_hitokoto()
            if hit:
                items.append(hit)

        # 获取 1 首诗词
        poem = self._fetch_jinrishici()
        if poem:
            items.append(poem)

        return items[:max_items]
