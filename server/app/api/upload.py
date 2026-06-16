"""文件上传模块"""
from flask import Blueprint
from ..utils import ok

bp = Blueprint('upload', __name__)


@bp.route('/audio', methods=['POST'])
def upload_audio():
    return ok({'audio_url': '/tmp/audio.mp3'})
