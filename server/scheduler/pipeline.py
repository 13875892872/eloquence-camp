"""
主编排器 — 串联「获取 → 去重 → 加工 → 入库」全流程
"""
import time
from app.extensions import db
from app.models.training import TrainingItem
from .sources import get_enabled_sources
from .processor import Processor
from .dedup import DedupManager


class Pipeline:
    """每日素材获取与加工主编排器"""

    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        self.processor = Processor(config)
        self.dedup = DedupManager(config)

    def run(self) -> dict:
        """执行完整流水线，返回统计摘要"""
        self.logger.info('Pipeline started')

        # ── 1. 实例化所有已启用源 ──
        sources = get_enabled_sources(self.config)
        if not sources:
            self.logger.info('No sources enabled, exiting')
            return {'total_fetched': 0, 'after_dedup': 0, 'created': 0, 'failed': 0}

        self.logger.info(f'Enabled sources: {[s.name for s in sources]}')

        # ── 2. 从各源获取原始素材 ──
        all_materials = []
        for source in sources:
            self.logger.info(f'Fetching {source.label}...', extra={'source': source.name})
            try:
                raw = source.fetch()
                self.logger.info(
                    f'Got {len(raw)} raw items', extra={'source': source.name}
                )
                all_materials.extend(raw)
            except Exception as e:
                self.logger.error(
                    f'Source failed: {e}', extra={'source': source.name}
                )

        self.logger.info(f'Total raw items: {len(all_materials)}')

        # ── 3. Level-1 去重（源缓存） ──
        fresh = []
        dups = 0
        for m in all_materials:
            if not self.dedup.is_duplicate_source(
                m['source_name'], m['title'], m['content']
            ):
                fresh.append(m)
                self.dedup.mark_processed_source(
                    m['source_name'], m['title'], m['content']
                )
            else:
                dups += 1
        self.logger.info(f'After source dedup: {len(fresh)} new ({dups} duplicates)')

        # ── 4. 限制每轮最大入库数 ──
        max_items = self.config.get('max_items_per_run', 12)
        fresh = fresh[:max_items]
        self.logger.info(f'Capped to {len(fresh)} items (max={max_items})')

        # ── 5. AI 加工 + Level-2 去重 + 入库 ──
        created = 0
        skipped_db = 0
        failed = 0

        for i, m in enumerate(fresh):
            if i > 0:
                delay = self.processor.delay
                self.logger.info(f'Waiting {delay}s before next Qwen call...')
                time.sleep(delay)

            self.logger.info(
                f'Processing [{i+1}/{len(fresh)}]: {m["title"][:40]}',
                extra={'source': m['source_name']}
            )

            # AI 加工
            processed = self.processor.process(m)
            if processed is None:
                self.logger.warning(
                    f'Qwen processing failed: {m["title"][:40]}',
                    extra={'source': m['source_name']}
                )
                failed += 1
                continue

            # Level-2 去重（数据库）
            if self.dedup.is_duplicate_db(processed['title'], processed['sample_text']):
                self.logger.info(
                    f'Skipped DB duplicate: {processed["title"]}',
                    extra={'source': m['source_name']}
                )
                skipped_db += 1
                continue

            # 入库
            try:
                item = TrainingItem(
                    category=processed['category'],
                    sub_category=processed['sub_category'],
                    title=processed['title'],
                    difficulty=processed['difficulty'],
                    sample_text=processed['sample_text'],
                    tags=processed['tags'],
                    status=self.config.get('default_status', 'online'),
                    sort_order=0,
                )
                db.session.add(item)
                db.session.commit()
                created += 1
                self.logger.info(
                    f'Created #{item.id}: {item.title} '
                    f'[{item.category}/{item.sub_category}] d={item.difficulty} '
                    f'tags={item.tags}',
                    extra={'source': m['source_name']}
                )
            except Exception as e:
                db.session.rollback()
                self.logger.error(
                    f'DB write failed: {e}',
                    extra={'source': m['source_name']}
                )
                failed += 1

        # ── 6. 保存缓存 ──
        self.dedup._save_cache()

        summary = {
            'total_fetched': len(all_materials),
            'after_dedup': len(fresh),
            'created': created,
            'skipped_db': skipped_db,
            'failed': failed,
        }
        self.logger.info(
            f'Pipeline complete: fetched={summary["total_fetched"]} '
            f'fresh={summary["after_dedup"]} created={created} '
            f'skipped={skipped_db} failed={failed}'
        )
        return summary
