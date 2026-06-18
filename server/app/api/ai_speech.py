"""
AI语音评测 + TTS 语音合成
"""
from flask import Blueprint, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..extensions import db
from ..models.common import PracticeRecord
from ..services.speech_eval import speech_evaluator
from ..services.tts_client import tts_client
from ..utils import ok, fail

bp = Blueprint('ai_speech', __name__)


def _get_user_id():
    """获取当前用户ID（可选登录）"""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return int(identity) if identity else None
    except Exception:
        return None


@bp.route('/evaluate', methods=['POST'])
def evaluate():
    """
    语音评测
    请求: { audio_url, reference_text?, duration?, training_item_id? }
    返回: { score, dimensions, feedback, record_id }
    """
    user_id = _get_user_id()
    data = request.get_json()

    audio_url = data.get('audio_url', '')
    if not audio_url:
        return fail(400, 'audio_url 不能为空')

    reference_text = data.get('reference_text', '')
    duration = data.get('duration', 0)
    training_item_id = data.get('training_item_id')

    # 调用评测服务
    result = speech_evaluator.evaluate(
        audio_url=audio_url,
        reference_text=reference_text,
        duration=duration
    )

    if not result.get('success'):
        return fail(500, result.get('error', '评测失败'))

    # 保存练习记录
    record_id = None
    if user_id:
        record = PracticeRecord(
            user_id=user_id,
            training_item_id=training_item_id,
            audio_url=audio_url,
            duration=duration,
            ai_score=result['score'],
            dimension_scores=result['dimensions'],
            ai_feedback=result['feedback'],
            source='training'
        )
        db.session.add(record)
        db.session.commit()
        record_id = record.id

    return ok({
        'ai_score': result['score'],
        'dimension_scores': result['dimensions'],
        'ai_feedback': result['feedback'],
        'record_id': record_id
    })


@bp.route('/tts', methods=['POST'])
def synthesize_speech():
    """
    文字转语音（范本播放）
    请求: { text, voice?, training_item_id? }
    返回: { audio_url, cached? }
    """
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return fail(400, 'text 不能为空')

    training_item_id = data.get('training_item_id')

    # 如果传了 training_item_id，先检查是否已有范本音频（复用）
    if training_item_id:
        from ..models.training import TrainingItem
        ti = TrainingItem.query.get(training_item_id)
        if ti and ti.sample_audio_url:
            return ok({'audio_url': ti.sample_audio_url, 'cached': True})

    voice = data.get('voice')  # 不传则使用 TTS 客户端默认音色 longanyang

    result = tts_client.synthesize(text, voice=voice)

    if not result.get('success'):
        return fail(500, result.get('error', 'TTS 合成失败'))

    # 拼接完整 API 路径
    audio_url = f"/api/upload/{result['audio_url']}"

    # 将生成的音频 URL 保存到训练题，下次直接复用
    if training_item_id:
        from ..models.training import TrainingItem
        ti = TrainingItem.query.get(training_item_id)
        if ti and not ti.sample_audio_url:
            ti.sample_audio_url = audio_url
            db.session.commit()

    return ok({'audio_url': audio_url, 'cached': False})
