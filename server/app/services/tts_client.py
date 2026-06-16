"""
TTS 语音合成 — 使用 DashScope TTS v2 API (CosyVoice)
"""
import os
import dashscope
from .oss_client import save_tts_audio


# 可用音色: longanyang(男), longxiaochun(女), longxiaoxia(活泼女), longyue(御姐), longcheng, longhua
DEFAULT_VOICE = 'longanyang'
DEFAULT_MODEL = 'cosyvoice-v3-flash'


class TTSClient:
    """DashScope TTS 客户端 (tts_v2 / CosyVoice)"""

    def __init__(self):
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        key = os.environ.get('DASHSCOPE_API_KEY', '')
        if key and key != 'your-dashscope-api-key':
            dashscope.api_key = key
        # 设置 WebSocket 地址（华北2北京地域）
        dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
        self._initialized = True

    def synthesize(self, text: str, voice: str = None) -> dict:
        """
        将文字合成为语音
        返回 {'success': bool, 'audio_url': str, 'error': str}
        """
        self._ensure_init()

        if not dashscope.api_key:
            return {
                'success': False,
                'error': 'TTS API Key 未配置，请在 .env 中设置 DASHSCOPE_API_KEY'
            }

        # 限制文本长度
        text = text[:500]
        if not voice:
            voice = DEFAULT_VOICE

        synthesizer = None
        try:
            from dashscope.audio.tts_v2 import SpeechSynthesizer
            import asyncio

            # Flask 请求线程可能没有事件循环，需要创建
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            synthesizer = SpeechSynthesizer(model=DEFAULT_MODEL, voice=voice)
            audio_bytes = synthesizer.call(text)

            if audio_bytes and len(audio_bytes) > 0:
                url = save_tts_audio(audio_bytes)
                return {
                    'success': True,
                    'audio_url': url
                }

            return {'success': False, 'error': 'TTS 返回空音频，请稍后重试'}

        except ImportError:
            return {
                'success': False,
                'error': 'dashscope 版本过旧，请升级: pip install dashscope --upgrade'
            }
        except Exception as e:
            msg = str(e)
            if '418' in msg or 'InvalidParameter' in msg:
                return {
                    'success': False,
                    'error': f'音色 {voice} 不可用，请尝试其他音色'
                }
            return {'success': False, 'error': f'TTS 服务异常: {msg[:100]}'}
        finally:
            if synthesizer:
                try:
                    del synthesizer
                except Exception:
                    pass


# 单例
tts_client = TTSClient()
