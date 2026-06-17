"""
文件上传模块 — 音频上传
"""
import os
from flask import Blueprint, request, send_file, redirect, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..services.oss_client import save_audio, UPLOAD_DIR, is_oss_url
from ..utils import ok, fail

bp = Blueprint('upload', __name__)


@bp.route('/audio', methods=['POST'])
def upload_audio():
    """上传音频文件"""
    # 可选登录（未登录也可上传但限制功能）
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = int(identity) if identity else None
    except Exception:
        pass

    # 检查是否有上传文件
    if 'file' not in request.files:
        return fail(400, '未找到音频文件')

    file = request.files['file']
    if not file.filename:
        return fail(400, '文件名为空')

    # 校验文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.silk'}
    if ext not in allowed:
        return fail(400, f'不支持的音频格式: {ext}，支持: {", ".join(allowed)}')

    # 校验文件大小（最大 10MB）
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    max_size = 10 * 1024 * 1024  # 10MB
    if size > max_size:
        return fail(400, f'文件过大，最大支持 {max_size // 1024 // 1024}MB')

    # 保存文件，返回相对路径如 audio/202606/xxx.mp3 或 OSS URL
    relative_path = save_audio(file)
    # 拼接完整路径（OSS URL 直接使用，本地路径拼接 API 前缀）
    if relative_path.startswith('https://'):
        audio_url = relative_path
    else:
        audio_url = f'/api/upload/{relative_path}'

    return ok({
        'audio_url': audio_url,
        'file_size': size,
        'format': ext.lstrip('.')
    })


@bp.route('/audio/<path:filename>', methods=['GET'])
def serve_audio(filename):
    """提供音频文件访问（开发环境本地，生产环境 OSS 重定向）"""
    # 安全检查：防止路径遍历
    safe_path = os.path.normpath(filename).lstrip(os.sep)
    full_path = os.path.join(UPLOAD_DIR, 'audio', safe_path)

    if not os.path.exists(full_path):
        return fail(404, '文件不存在')

    # 根据扩展名设置 MIME 类型
    ext = os.path.splitext(full_path)[1].lower()
    mime_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',
    }

    return send_file(full_path, mimetype=mime_map.get(ext, 'audio/mpeg'))


@bp.route('/tts/<path:filename>', methods=['GET'])
def serve_tts(filename):
    """提供 TTS 音频文件访问"""
    safe_path = os.path.normpath(filename).lstrip(os.sep)
    full_path = os.path.join(UPLOAD_DIR, 'tts', safe_path)

    if not os.path.exists(full_path):
        return fail(404, '文件不存在')

    return send_file(full_path, mimetype='audio/mpeg')
