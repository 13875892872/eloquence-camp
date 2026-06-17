"""
文件存储服务 — 开发环境存本地，生产环境可切换阿里云 OSS
"""
import os
import uuid
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

# 确保本地上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'audio'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'tts'), exist_ok=True)

# ---- OSS 客户端（懒加载） ----

_oss_bucket = None
_oss_checked = False


def _get_oss_bucket():
    """懒加载 OSS Bucket 实例，未配置则返回 None"""
    global _oss_bucket, _oss_checked
    if _oss_checked:
        return _oss_bucket

    _oss_checked = True
    endpoint = os.environ.get('OSS_ENDPOINT', '')
    key_id = os.environ.get('OSS_ACCESS_KEY_ID', '')
    key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
    bucket_name = os.environ.get('OSS_BUCKET_NAME', '')

    # 检测是否配置了有效凭证
    placeholders = ('your-', 'your_', 'changeme', 'xxx')
    if (not key_id or not key_secret or not endpoint or not bucket_name
            or any(p in key_id.lower() for p in placeholders)):
        return None

    try:
        import oss2
        auth = oss2.Auth(key_id, key_secret)
        _oss_bucket = oss2.Bucket(auth, endpoint, bucket_name)
        logger.info('OSS 客户端已初始化: %s/%s', endpoint, bucket_name)
    except Exception as e:
        logger.warning('OSS 初始化失败，降级到本地存储: %s', e)
        _oss_bucket = None

    return _oss_bucket


def _oss_enabled():
    """OSS 是否可用"""
    return _get_oss_bucket() is not None


def _oss_upload(key: str, data: bytes, content_type: str = 'audio/mpeg') -> str:
    """上传到 OSS，返回 CDN URL"""
    bucket = _get_oss_bucket()
    bucket.put_object(key, data, headers={'Content-Type': content_type})
    # 构造访问 URL（使用 Bucket 域名）
    endpoint = os.environ.get('OSS_ENDPOINT', '')
    bucket_name = os.environ.get('OSS_BUCKET_NAME', '')
    cdn_domain = os.environ.get('OSS_CDN_DOMAIN', '')
    if cdn_domain:
        return f'https://{cdn_domain}/{key}'
    return f'https://{bucket_name}.{endpoint}/{key}'


def _oss_delete(key: str) -> bool:
    """从 OSS 删除文件"""
    try:
        bucket = _get_oss_bucket()
        bucket.delete_object(key)
        return True
    except Exception:
        return False


# ---- 公开接口 ----

def save_audio(file_data, filename: str = None) -> str:
    """
    保存音频文件
    返回可访问的路径（本地相对路径或 OSS URL）
    """
    if not filename:
        ext = '.mp3'
        filename = f"{uuid.uuid4().hex}{ext}"

    date_dir = datetime.now().strftime('%Y%m')
    key = f'audio/{date_dir}/{filename}'

    # OSS 模式
    if _oss_enabled():
        try:
            if hasattr(file_data, 'read'):
                content = file_data.read()
            elif isinstance(file_data, bytes):
                content = file_data
            else:
                with open(file_data, 'rb') as f:
                    content = f.read()
            url = _oss_upload(key, content)
            return url
        except Exception as e:
            logger.warning('OSS 上传失败，降级到本地: %s', e)
            # 降级到本地存储

    # 本地存储
    dir_path = os.path.join(UPLOAD_DIR, 'audio', date_dir)
    os.makedirs(dir_path, exist_ok=True)
    filepath = os.path.join(dir_path, filename)

    if hasattr(file_data, 'save'):
        # Flask FileStorage 对象
        file_data.save(filepath)
    elif isinstance(file_data, bytes):
        with open(filepath, 'wb') as f:
            f.write(file_data)
    elif hasattr(file_data, 'read'):
        # 普通文件对象 / BufferedReader
        with open(filepath, 'wb') as f:
            f.write(file_data.read())
    else:
        with open(filepath, 'wb') as f:
            f.write(file_data)

    return f'audio/{date_dir}/{filename}'


def save_tts_audio(audio_bytes: bytes, prefix: str = 'tts') -> str:
    """保存 TTS 生成的音频"""
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.mp3"
    date_dir = datetime.now().strftime('%Y%m')
    key = f'tts/{date_dir}/{filename}'

    # OSS 模式
    if _oss_enabled():
        try:
            return _oss_upload(key, audio_bytes)
        except Exception as e:
            logger.warning('OSS TTS 上传失败，降级到本地: %s', e)

    # 本地存储
    dir_path = os.path.join(UPLOAD_DIR, 'tts', date_dir)
    os.makedirs(dir_path, exist_ok=True)
    filepath = os.path.join(dir_path, filename)
    with open(filepath, 'wb') as f:
        f.write(audio_bytes)

    return f'tts/{date_dir}/{filename}'


def get_absolute_path(relative_path: str) -> str:
    """将相对路径转为绝对路径（OSS 模式返回原 URL）"""
    if _oss_enabled() and relative_path.startswith('https://'):
        return relative_path
    clean = relative_path.lstrip('/')
    return os.path.join(UPLOAD_DIR, clean)


def is_oss_url(path: str) -> bool:
    """判断是否为 OSS URL"""
    return path.startswith('https://') and 'aliyuncs.com' in path


def delete_file(relative_url: str) -> bool:
    """删除文件（本地或 OSS）"""
    try:
        if relative_url.startswith('https://'):
            # OSS URL — 提取 key
            if 'aliyuncs.com/' in relative_url:
                key = relative_url.split('aliyuncs.com/', 1)[1]
                return _oss_delete(key)
            return False
        # 本地文件
        clean = relative_url.lstrip('/')
        path = os.path.join(UPLOAD_DIR, clean)
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception as e:
        logger.warning('删除文件失败: %s', e)
    return False
