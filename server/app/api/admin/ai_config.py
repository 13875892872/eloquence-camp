"""后台管理 — AI配置"""
from flask import request
from . import admin_bp
from ...extensions import db
from ...models.ai import AiConfig
from ...utils import ok


@admin_bp.route('/ai-config', methods=['GET'])
def get_ai_config():
    """获取AI配置"""
    config = AiConfig.query.first()
    if not config:
        config = AiConfig()
        db.session.add(config)
        db.session.commit()

    return ok({
        'text_model': config.text_model,
        'text_temperature': float(config.text_temperature),
        'text_max_tokens': config.text_max_tokens,
        'text_timeout': config.text_timeout,
        'new_user_daily': config.new_user_daily,
        'checkin_bonus': config.checkin_bonus,
        'reset_hour': config.reset_hour,
        'weight_pronunciation': config.weight_pronunciation,
        'weight_fluency': config.weight_fluency,
        'weight_completeness': config.weight_completeness,
        'weight_content': config.weight_content,
        'weight_expressiveness': config.weight_expressiveness,
        'min_pass_score': config.min_pass_score,
        'prompt_templates': config.prompt_templates or {}
    })


@admin_bp.route('/ai-config', methods=['PUT'])
def update_ai_config():
    """更新AI配置"""
    config = AiConfig.query.first()
    if not config:
        config = AiConfig()
        db.session.add(config)

    data = request.get_json()
    # Qwen参数
    if 'text_model' in data: config.text_model = data['text_model']
    if 'text_temperature' in data: config.text_temperature = data['text_temperature']
    if 'text_max_tokens' in data: config.text_max_tokens = data['text_max_tokens']
    if 'text_timeout' in data: config.text_timeout = data['text_timeout']
    # 次数策略
    if 'new_user_daily' in data: config.new_user_daily = data['new_user_daily']
    if 'checkin_bonus' in data: config.checkin_bonus = data['checkin_bonus']
    if 'reset_hour' in data: config.reset_hour = data['reset_hour']
    # 评测权重
    if 'weight_pronunciation' in data: config.weight_pronunciation = data['weight_pronunciation']
    if 'weight_fluency' in data: config.weight_fluency = data['weight_fluency']
    if 'weight_completeness' in data: config.weight_completeness = data['weight_completeness']
    if 'weight_content' in data: config.weight_content = data['weight_content']
    if 'weight_expressiveness' in data: config.weight_expressiveness = data['weight_expressiveness']
    if 'min_pass_score' in data: config.min_pass_score = data['min_pass_score']
    # Prompt模板
    if 'prompt_templates' in data: config.prompt_templates = data['prompt_templates']

    db.session.commit()
    return ok({'message': 'AI配置已保存'})
