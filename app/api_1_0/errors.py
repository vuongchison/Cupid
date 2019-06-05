from flask import jsonify
from app.exceptions import ValidationError
from . import api

def page_not_found(message:str) -> response:
    """Không tìm thấy trang"""
    response = jsonify({'error': 'page not found', 'message': message})
    response.status_code = 404
    return response

def forbidden(message:str) -> response:
    """Không có quyền truy cập"""
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def unauthorized(message:str) -> response:
    """Chưa xác thực"""
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def bad_request(message:str) -> response:
    """Request thiếu tham số"""
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])