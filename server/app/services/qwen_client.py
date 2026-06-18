"""
Qwen API 客户端 — 阿里云百炼 DashScope
"""
import os
import json
import dashscope
from http import HTTPStatus
from dashscope import Generation


class QwenClient:
    """Qwen 大模型调用封装"""

    def __init__(self, app=None):
        self._initialized = False

    def _ensure_init(self):
        """延迟初始化：确保在 Flask app context 之后读取配置"""
        if self._initialized:
            return
        self.api_key = os.environ.get('DASHSCOPE_API_KEY', '')
        if self.api_key:
            dashscope.api_key = self.api_key
        self.text_model = os.environ.get('QWEN_TEXT_MODEL', 'qwen-plus')
        self.feedback_model = os.environ.get('QWEN_FEEDBACK_MODEL', 'qwen-plus')
        self._initialized = True

    def chat(self, prompt: str, model: str = None, temperature: float = 0.7,
             max_tokens: int = 2000) -> dict:
        """调用 Qwen 生成文本"""
        self._ensure_init()
        try:
            response = Generation.call(
                model=model or self.text_model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                return {'success': True, 'content': content}
            else:
                return {
                    'success': False,
                    'error': f'Qwen API 返回错误: code={response.status_code}, message={response.message}'
                }
        except Exception as e:
            return {'success': False, 'error': f'Qwen 调用异常: {str(e)}'}

    def generate_text(self, scene_type: str, topic: str, scene_desc: str = '',
                      duration: str = '3min', style: str = '专业正式',
                      extra_notes: str = '') -> dict:
        """根据场景生成口才文案"""
        prompt = self._build_prompt(scene_type, topic, scene_desc, duration, style, extra_notes)
        return self.chat(prompt)

    def generate_feedback(self, transcription: str, scores: dict) -> dict:
        """根据录音转写和评分生成改进建议"""
        prompt = f"""你是一位专业的口才教练。请根据以下语音练习的评分结果，给出具体改进建议。

【各项评分（满分100）】
发音准确度：{scores.get('pronunciation', 0)}分
流利度：{scores.get('fluency', 0)}分
完整度：{scores.get('completeness', 0)}分
内容质量：{scores.get('content', 0)}分
表现力：{scores.get('expressiveness', 0)}分

【录音转写内容】
{transcription or '(未获取到语音内容)'}

请用友好的口吻，给出一条总体评价和 2-3 条具体可操作的改进建议。控制在200字以内。"""
        return self.chat(prompt, model=self.feedback_model, temperature=0.6, max_tokens=500)

    def _build_prompt(self, scene_type, topic, scene_desc, duration, style, extra_notes):
        """根据场景类型构建 Prompt"""
        base = {
            'speech': f"""你是一位专业的演讲稿撰写专家。请根据以下信息生成一篇演讲稿：

【主题】{topic}
【场景】{scene_desc or '正式演讲'}
【时长要求】{duration}
【风格偏好】{style}
【补充说明】{extra_notes or '无'}

要求：
1. 结构清晰：开场白（吸引注意）+ 正文（2-3个要点展开）+ 结尾（总结升华）
2. 语言口语化，适合朗读表达
3. 适当使用排比、设问等修辞手法增强感染力
4. 用 **粗体** 标注重音词，用 /// 标注停顿点
5. 文末附带3个关键要点总结和1条表达技巧提示""",

            'short_video': f"""你是一位短视频口播文案专家。请根据以下信息生成一篇短视频口播稿：

【主题】{topic}
【场景】{scene_desc or '短视频平台'}
【时长要求】{duration}
【风格偏好】{style or '轻松口语化'}
【补充说明】{extra_notes or '无'}

要求：
1. 前3秒必须有钩子抓住注意力（痛点提问/惊人数据/反转开头）
2. 语言口语化、有节奏感，适合口播
3. 使用短句，每句不超过20字
4. 加入互动引导语（"你觉得呢？""评论区告诉我"等）
5. 文末给出拍摄建议（如配合什么画面/表情）""",

            'livestream': f"""你是一位直播带货话术专家。请根据以下信息生成直播话术：

【产品/主题】{topic}
【直播场景】{scene_desc or '带货直播'}
【时长要求】{duration}
【风格偏好】{style or '热情有感染力'}
【补充说明】{extra_notes or '无'}

要求：
1. 包含完整的带货节奏：开场暖场 → 痛点引入 → 产品讲解 → 逼单促单
2. 使用FAB法则（特点-优势-利益）讲解产品
3. 穿插限时限量、价格锚定等促单话术
4. 语言热情有感染力，多用感叹和设问
5. 文末附带直播节奏控制建议""",

            'opening': f"""你是一位万能开场白专家。请根据以下信息生成多种开场白：

【主题】{topic}
【使用场景】{scene_desc or '多场景通用'}
【补充说明】{extra_notes or '无'}

要求：
1. 生成3种不同风格的开场白：专业正式版、轻松幽默版、情感共鸣版
2. 每种开场白30-60秒朗读时长
3. 开场白要能立刻抓住听众注意力
4. 适合直接拿来就用，即插即用""",

            'interview': f"""你是一位求职面试表达教练。请根据以下信息生成面试话术：

【面试主题/岗位】{topic}
【面试场景】{scene_desc or '结构化面试'}
【时长要求】{duration}
【风格偏好】{style or '真诚专业'}
【补充说明】{extra_notes or '无'}

要求：
1. 包含：开场自我介绍要点 + 核心回答正文 + 收尾致谢
2. 使用 STAR 法则组织经历类回答（情境-任务-行动-结果）
3. 语言真诚、逻辑清晰，适合口头表达
4. 用 **粗体** 标注重音词，用 /// 标注停顿点
5. 文末附带3条面试表达技巧和常见追问应对提示""",
        }

        prompt = base.get(scene_type, base['speech'])
        prompt += "\n\n请以JSON格式返回，包含title（标题）、content（完整文案，含标注）和tips（表达技巧提示）。"

        return prompt


# 全局单例
qwen_client = QwenClient()
