"""
60s API — 每日精选新闻 + 微语
API: https://60s.viki.moe/v2/60s
"""
from typing import List, Dict, Any
from ..base import BaseSource


class News60sSource(BaseSource):
    name = 'news_60s'
    label = '60s每日新闻'

    API_URL = 'https://60s.viki.moe/v2/60s'

    def fetch(self) -> List[Dict[str, Any]]:
        resp = self._safe_get(self.API_URL, timeout=15)
        if resp is None:
            return []

        try:
            data = resp.json()
        except (ValueError, KeyError):
            return []

        items = []

        # 新闻列表 — 可能是字符串列表或 dict 列表
        news_list = data.get('data', {}).get('news', [])
        for news in news_list[:self.config.get('max_items', 5)]:
            # 兼容两种格式：纯字符串 或 {'title':..., 'content':...}
            if isinstance(news, str):
                text = news.strip()
                if not text:
                    continue
                # 尝试拆分标题和内容（格式多为 "来源 标题：内容"）
                if '：' in text:
                    title, content = text.split('：', 1)
                elif ':' in text:
                    title, content = text.split(':', 1)
                else:
                    title = text[:30]
                    content = text
                items.append(self._to_raw(
                    title=title.strip(),
                    content=content.strip(),
                    source_type='news',
                    metadata={'section': '60s_news'}
                ))
            elif isinstance(news, dict):
                title = news.get('title', '')
                content = news.get('content', '')
                if content:
                    items.append(self._to_raw(
                        title=title,
                        content=content,
                        source_type='news',
                        metadata={'section': '60s_news'}
                    ))

        # 每日微语
        tip = data.get('data', {}).get('tip', '')
        if tip:
            items.append(self._to_raw(
                title='每日微语',
                content=tip,
                source_type='quote',
                metadata={'section': '60s_tip'}
            ))

        return items[:self.config.get('max_items', 5)]
