"""
AI 处理器 — 将原始素材通过 Qwen 加工为训练题字段
"""
import json
import re
import time
from typing import Optional, Dict, Any
from app.services.qwen_client import qwen_client


# ── Prompt 模板 ──
PROCESS_PROMPT = """你是一位专业口才训练内容编辑。你的任务是将外部素材转化为适合口才练习的训练题。
请严格以JSON格式返回结果。

【素材类型】{source_type}
【原始标题】{title}
【原始内容】{content}

请完成以下转化：

1. category（5选1）：basic（朗读/发音）、speech（演讲/致辞）、livestream（直播/带货）、improv（即兴/辩论/故事）、interview（求职/面试）
2. sub_category：细分类型，如：新闻朗读、观点评述、带货话术、诗词诵读、故事讲述
3. title：吸引人的练习标题（10-20字）
4. sample_text：改写为适合大声朗读的口才练习文本：
   - 保留核心信息，口语化改写
   - 短句有节奏，150-400字
   - 名言/诗词需简要介绍背景并附练习提示
5. difficulty：1=短朗读(<200字) 2=简单表达 3=中等语气 4=长文本观点 5=复杂逻辑
6. tags：3-5个中文标签

返回严格JSON（不要markdown代码块）：
{{"category":"...","sub_category":"...","title":"...","sample_text":"...","difficulty":N,"tags":["...","..."]}}"""


class Processor:
    """Qwen AI 素材处理器"""

    VALID_CATEGORIES = {'basic', 'speech', 'livestream', 'live', 'improv', 'interview', 'short_video', 'student'}

    def __init__(self, config: dict):
        self.model = config.get('qwen_model', 'qwen-plus')
        self.temperature = config.get('qwen_temperature', 0.6)
        self.timeout = config.get('qwen_timeout', 30)
        self.delay = config.get('inter_item_delay', 2.0)

    def process(self, raw: dict) -> Optional[Dict[str, Any]]:
        """
        加工一条原始素材，返回 TrainingItem 构造字段或 None

        raw 格式: {title, content, source_name, source_type, metadata}
        返回格式: {category, sub_category, title, difficulty, sample_text, tags}
        """
        prompt = PROCESS_PROMPT.format(
            source_type=raw.get('source_type', 'news'),
            title=raw.get('title', '') or '无标题',
            content=(raw.get('content', '') or '')[:1500]
        )

        # 第一次尝试
        result = qwen_client.chat(
            prompt,
            model=self.model,
            temperature=self.temperature,
            max_tokens=1200
        )

        if not result.get('success'):
            # 等待后重试（可能是限流）
            time.sleep(3)
            result = qwen_client.chat(
                prompt,
                model=self.model,
                temperature=0.3,  # 低温重试增强格式遵循
                max_tokens=1200
            )

        if not result.get('success'):
            return None

        return self._parse_response(result['content'], raw)

    def _parse_response(self, raw_text: str, raw: dict) -> Optional[Dict[str, Any]]:
        """解析 Qwen 返回的 JSON"""
        text = raw_text.strip()

        # 去除 markdown 代码块标记
        if text.startswith('```'):
            lines = text.split('\n')
            if len(lines) > 1:
                lines = lines[1:]  # 去掉 ```json 或 ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines).strip()

        # 尝试解析 JSON
        data = None
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # 正则兜底：提取第一个完整 JSON 对象
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    return None
            if data is None:
                return None

        # 验证必填字段
        required = ['category', 'sub_category', 'title', 'sample_text', 'difficulty', 'tags']
        for key in required:
            if key not in data:
                return None

        # 清理和验证
        category = data['category'].strip().lower()
        if category == 'live':
            category = 'livestream'
        if category not in self.VALID_CATEGORIES:
            category = 'basic'

        try:
            difficulty = int(data['difficulty'])
            difficulty = max(1, min(5, difficulty))
        except (ValueError, TypeError):
            difficulty = 3

        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        tags = [t for t in tags if t][:5]

        sample_text = data.get('sample_text', '') or raw.get('content', '')
        if len(sample_text) < 20:
            sample_text = raw.get('content', '')  # 太短则回退到原文

        return {
            'category': category,
            'sub_category': data.get('sub_category', '')[:30],
            'title': data.get('title', raw.get('title', ''))[:100],
            'difficulty': difficulty,
            'sample_text': sample_text[:3000],
            'tags': tags
        }
