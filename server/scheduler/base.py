"""
素材源抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import requests


class BaseSource(ABC):
    """所有素材源的抽象基类"""

    name: str = 'base'           # 唯一标识，与配置 key 对应
    label: str = 'Base Source'   # 人类可读的名称（日志用）

    def __init__(self, config: dict):
        self.config = config     # 此源的配置子集，如 {'enabled': True, 'max_items': 5}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EloquenceCamp/1.0 (scheduler; training-material-fetcher)'
        })

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        从远端获取原始素材。

        返回列表，每个元素为 dict：
            title       (str) — 原始标题，名言可为空
            content     (str) — 原始文本内容
            source_name (str) — 等于 self.name
            source_type (str) — 'news' | 'topic' | 'quote' | 'poem'
            metadata    (dict) — 可选附加信息（URL、时间戳等）
        """
        ...

    def _safe_get(self, url: str, timeout: int = 15) -> Optional[requests.Response]:
        """带错误处理的 HTTP GET"""
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException:
            return None

    def _to_raw(self, title: str, content: str, source_type: str,
                metadata: dict = None) -> dict:
        """工厂方法：生成统一格式的 RawMaterial dict"""
        return {
            'title': title or '',
            'content': content or '',
            'source_name': self.name,
            'source_type': source_type,
            'metadata': metadata or {}
        }

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.name})>'
