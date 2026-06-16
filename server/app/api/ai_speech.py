"""AI语音评测模块"""
from flask import Blueprint
from ..utils import ok

bp = Blueprint('ai_speech', __name__)


@bp.route('/evaluate', methods=['POST'])
def evaluate():
    return ok({'ai_score': 85, 'dimension_scores': {}, 'ai_feedback': 'TODO'})
