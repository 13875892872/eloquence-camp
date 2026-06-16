"""
全局错误处理
"""
from flask import Flask
from werkzeug.exceptions import HTTPException
from .response import fail


def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return fail(400, str(e.description) if hasattr(e, 'description') else '请求参数错误')

    @app.errorhandler(401)
    def unauthorized(e):
        return fail(401, '请先登录')

    @app.errorhandler(403)
    def forbidden(e):
        return fail(403, '无权限访问')

    @app.errorhandler(404)
    def not_found(e):
        return fail(404, '资源不存在')

    @app.errorhandler(405)
    def method_not_allowed(e):
        return fail(405, '请求方法不允许')

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return fail(413, '文件大小超过限制')

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'Internal Server Error: {e}')
        return fail(500, '服务器内部错误，请稍后重试')

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return fail(e.code, e.description)
