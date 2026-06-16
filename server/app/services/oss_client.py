"""
文件存储服务 — 开发环境存本地，生产环境可切换 OSS
"""
import os
import uuid
from datetime import datetime
from flask import current_app


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'audio'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'tts'), exist_ok=True)


def save_audio(file_data, filename: str = None) -> str:
    """
    保存音频文件到本地存储
    返回可访问的 URL 路径
    """
    if not filename:
        ext = '.mp3'
        filename = f"{uuid.uuid4().hex}{ext}"

    # 按日期分目录
    date_dir = datetime.now().strftime('%Y%m')
    dir_path = os.path.join(UPLOAD_DIR, 'audio', date_dir)
    os.makedirs(dir_path, exist_ok=True)

    filepath = os.path.join(dir_path, filename)

    if hasattr(file_data, 'save'):
        file_data.save(filepath)
    else:
        with open(filepath, 'wb') as f:
            f.write(file_data)

    # 返回相对路径，前端通过 /api/upload/audio/{date_dir}/{filename} 访问
    return f'audio/{date_dir}/{filename}'


def save_tts_audio(audio_bytes: bytes, prefix: str = 'tts') -> str:
    """保存 TTS 生成的音频"""
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.mp3"
    date_dir = datetime.now().strftime('%Y%m')
    dir_path = os.path.join(UPLOAD_DIR, 'tts', date_dir)
    os.makedirs(dir_path, exist_ok=True)

    filepath = os.path.join(dir_path, filename)
    with open(filepath, 'wb') as f:
        f.write(audio_bytes)

    return f'tts/{date_dir}/{filename}'


def get_absolute_path(relative_path: str) -> str:
    """将相对路径转为绝对路径"""
    # audio/202606/xxx.mp3 → <UPLOAD_DIR>/audio/202606/xxx.mp3
    clean = relative_path.lstrip('/')
    return os.path.join(UPLOAD_DIR, clean)


def delete_file(relative_url: str) -> bool:
    """删除文件"""
    try:
        path = get_absolute_path(relative_url)
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception:
        pass
    return False
