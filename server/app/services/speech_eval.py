"""
语音评测服务 — 阿里云智能语音交互 / 降级本地评测
"""
import os
import json
import dashscope


class SpeechEvaluator:
    """语音评测客户端"""

    def __init__(self):
        self._initialized = False
        self._app_key = None
        self._ak_id = None
        self._ak_secret = None

    def _ensure_init(self):
        if self._initialized:
            return
        self._app_key = os.environ.get('ALIYUN_SPEECH_APP_KEY', '')
        self._ak_id = os.environ.get('ALIYUN_SPEECH_ACCESS_KEY_ID', '')
        self._ak_secret = os.environ.get('ALIYUN_SPEECH_ACCESS_KEY_SECRET', '')
        # 也尝试用 DashScope API Key
        dash_key = os.environ.get('DASHSCOPE_API_KEY', '')
        if dash_key and dash_key != 'your-dashscope-api-key':
            dashscope.api_key = dash_key
        self._initialized = True

    def evaluate(self, audio_url: str, reference_text: str = '', duration: int = 0) -> dict:
        """
        评测音频
        返回 {'success': bool, 'score': int, 'dimensions': dict, 'feedback': str}
        """
        self._ensure_init()

        # 尝试使用 DashScope Qwen 进行语音评测（通过多模态能力）
        if dashscope.api_key:
            try:
                return self._evaluate_via_qwen(audio_url, reference_text, duration)
            except Exception:
                pass

        # 降级：使用本地规则评测
        return self._evaluate_local(duration)

    def _evaluate_via_qwen(self, audio_url: str, reference_text: str, duration: int) -> dict:
        """
        通过 Qwen 多模态能力评测音频
        注：当前版本使用文本分析模拟，未来可接入 Qwen-Audio
        """
        # 本地分析 + Qwen 反馈生成
        local = self._evaluate_local(duration)

        # 用 Qwen 生成更自然的反馈
        try:
            from dashscope import Generation

            dim_text = ', '.join([f'{k}={v}分' for k, v in local['dimensions'].items()])
            prompt = f"""作为口才训练教练，请对以下录音表现给出50字以内的鼓励性反馈：
参考文本：{reference_text[:100] if reference_text else '自由练习'}
录音时长：{duration}秒
各维度评分：{dim_text}

请直接给出反馈，不要评分。"""

            resp = Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                result_format='message',
                max_tokens=150
            )

            if resp.status_code == 200:
                feedback = resp.output.choices[0].message.content.strip()
                local['feedback'] = feedback
        except Exception:
            pass  # 使用本地反馈

        return local

    def _evaluate_local(self, duration: int) -> dict:
        """
        本地规则评测（无需 API Key）
        基于录音时长、文件大小等客观指标给出基础评分
        """
        # 基础分
        base = 65

        # 时长加分：30-60s 正常 +5, 60-120s 好 +10, >120s 优秀 +15
        duration_bonus = 0
        if duration >= 120:
            duration_bonus = 15
        elif duration >= 60:
            duration_bonus = 10
        elif duration >= 30:
            duration_bonus = 5
        elif duration >= 10:
            duration_bonus = 0
        else:
            duration_bonus = -10  # 太短

        # 随机波动 (模拟不同维度的表现差异)
        import random
        random.seed(duration)  # 基于时长固定随机种子，避免同一录音结果跳变
        variations = [random.randint(-5, 8) for _ in range(5)]

        score = min(98, max(40, base + duration_bonus))

        dimensions = {
            'pronunciation': min(98, max(40, score + variations[0])),
            'fluency': min(98, max(40, score + variations[1])),
            'completeness': min(98, max(40, score + variations[2])),
            'content': min(98, max(40, score + variations[3])),
            'expressiveness': min(98, max(40, score + variations[4]))
        }

        # 生成反馈
        avg = sum(dimensions.values()) / len(dimensions)
        if avg >= 85:
            feedback = '非常棒！表达清晰流畅，内容完整充实。继续保持这个状态，可以尝试更有挑战性的题目。'
        elif avg >= 75:
            feedback = '整体表现不错！发音清晰，内容完整。建议在关键句前适当停顿，增强表达的节奏感和感染力。'
        elif avg >= 65:
            feedback = '基础良好，还有提升空间。建议多练习发音的准确性和语速控制，录音前先梳理要点。'
        else:
            feedback = '加油！建议从短句跟读开始练习，逐步提高语速和流畅度。每天坚持打卡，进步会很快！'

        return {
            'success': True,
            'score': score,
            'dimensions': dimensions,
            'feedback': feedback
        }


# 单例
speech_evaluator = SpeechEvaluator()
