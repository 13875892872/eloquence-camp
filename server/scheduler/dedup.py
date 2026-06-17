"""
两级去重：源缓存 SHA256 + 数据库标题/内容相似度
"""
import os
import json
import hashlib
import time
from typing import Optional
from app.extensions import db
from app.models.training import TrainingItem


class DedupManager:
    """管理源素材和数据库两条去重管线"""

    def __init__(self, config: dict):
        # 解析缓存路径（相对于 server/）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = config.get('cache_dir', 'scheduler/cache')
        self.cache_path = os.path.join(project_root, cache_dir, 'source_cache.json')
        self.cache_ttl_secs = config.get('cache_ttl_days', 30) * 86400
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        """加载缓存 JSON，过期条目自动清理"""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

        # 清理过期条目
        now = time.time()
        for source_name in list(cache.keys()):
            src = cache[source_name]
            if isinstance(src, dict) and 'entries' in src:
                src['entries'] = [
                    e for e in src['entries']
                    if now - e.get('ts', 0) < self.cache_ttl_secs
                ]
                # 保留最近 500 条
                if len(src['entries']) > 500:
                    src['entries'] = src['entries'][-500:]

        return cache

    def _save_cache(self):
        """写回缓存"""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _compute_hash(title: str, content: str) -> str:
        """计算 SHA256 摘要"""
        seed = (title[:50] + content[:100]).encode('utf-8')
        return hashlib.sha256(seed).hexdigest()[:16]

    def is_duplicate_source(self, source_name: str, title: str, content: str) -> bool:
        """Level 1: 检查源素材是否曾经获取过"""
        h = self._compute_hash(title, content)
        src = self._cache.get(source_name, {})
        if isinstance(src, dict) and 'entries' in src:
            for entry in src['entries']:
                if entry.get('h') == h:
                    return True
        return False

    def mark_processed_source(self, source_name: str, title: str, content: str):
        """Level 1: 记录已处理的源素材"""
        h = self._compute_hash(title, content)
        if source_name not in self._cache:
            self._cache[source_name] = {'entries': []}
        self._cache[source_name]['entries'].append({
            'h': h,
            'ts': time.time()
        })

    @staticmethod
    def is_duplicate_db(title: str, sample_text: str) -> bool:
        """Level 2: 检查数据库是否已有相似训练题"""
        # 完全匹配标题
        if TrainingItem.query.filter_by(title=title).first():
            return True
        # 前 50 字前缀匹配
        prefix = sample_text[:50].replace('%', '\\%')
        if prefix:
            pattern = prefix + '%'
            if TrainingItem.query.filter(
                TrainingItem.sample_text.like(pattern)
            ).first():
                return True
        return False
