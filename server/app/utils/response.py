"""
统一响应格式
"""
from flask import jsonify


def ok(data=None, message='ok'):
    """200 成功"""
    return jsonify({'code': 200, 'message': message, 'data': data})


def fail(code=400, message='Bad Request', data=None):
    """通用失败"""
    return jsonify({'code': code, 'message': message, 'data': data}), code


def paginated(items, pagination):
    """分页响应"""
    return ok({
        'items': items,
        'pagination': {
            'page': pagination['page'],
            'page_size': pagination['page_size'],
            'total': pagination['total'],
            'total_pages': (pagination['total'] + pagination['page_size'] - 1) // pagination['page_size']
        }
    })
