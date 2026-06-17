"""
RSS 订阅源 — 解析 XML RSS 2.0
默认关闭，需在配置中启用并设置 urls
"""
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import List, Dict, Any
from ..base import BaseSource


class MLStripper(HTMLParser):
    """去除 HTML 标签"""
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)


def strip_html(text: str) -> str:
    """去除 HTML 标签，保留纯文本"""
    if not text:
        return ''
    s = MLStripper()
    try:
        s.feed(text)
        return s.get_data().strip()
    except Exception:
        # fallback: 正则去标签
        return re.sub(r'<[^>]+>', '', text).strip()


class RssFeedsSource(BaseSource):
    name = 'rss_feeds'
    label = 'RSS订阅'

    def _parse_feed(self, url: str) -> List[dict]:
        """解析单个 RSS feed"""
        resp = self._safe_get(url, timeout=20)
        if resp is None:
            return []

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError:
            return []

        items = []
        for elem in root.iter('item'):
            title_elem = elem.find('title')
            desc_elem = elem.find('description')

            title = title_elem.text if title_elem is not None and title_elem.text else ''
            desc = desc_elem.text if desc_elem is not None and desc_elem.text else ''

            # 清理 HTML
            desc = strip_html(desc)

            # 截断过长的描述
            if len(desc) > 800:
                desc = desc[:800] + '...'

            if title and desc:
                items.append({
                    'title': title.strip(),
                    'content': desc.strip(),
                    'url': url
                })

        return items

    def fetch(self) -> List[Dict[str, Any]]:
        urls = self.config.get('urls', [])
        if not urls:
            return []

        max_items = self.config.get('max_items', 5)
        all_items = []

        for url in urls:
            if len(all_items) >= max_items:
                break
            feed_items = self._parse_feed(url)
            all_items.extend(feed_items)

        # 截断到 max_items
        raw = []
        for item in all_items[:max_items]:
            raw.append(self._to_raw(
                title=item['title'],
                content=item['content'],
                source_type='news',
                metadata={'url': item['url']}
            ))

        return raw
