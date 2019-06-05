from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flask_login import current_user, login_user
from ..models import User
from . import api
from .errors import  forbidden, unauthorized

#Xác thực bằng email, mật khẩu
basic_auth = HTTPBasicAuth()

#Xác thực bằng token
token_auth = HTTPTokenAuth('Bearer')

multi_auth = MultiAuth(basic_auth, token_auth)

@basic_auth.verify_password
def verify_password(email, password):
    """Xác thực bằng email và mật khẩu"""
    if not email:
        return current_user.is_authenticated
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    if user.verify_password(password):
        login_user(user, True)
        return True
    return False

@token_auth.verify_token
def verify_token(token:str) -> bool:
    """Xác thực bằng token
    - Trả về False nếu token không hợp lệ
    - Ghi nhận người dùng đã đăng nhập và trả về True nếu token hợp lệ"""
    if not token:
        return current_user.is_authenticated
    user = User.verify_auth_token(token)
    if user:
        login_user(user, True)
        return True
    return False

@basic_auth.error_handler
def auth_error():
    return unauthorized('Thông tin không hợp lệ')

@api.before_request
@multi_auth.login_required
def before_request():
    #Kiểm tra người dùng đã xác nhận email chưa trước mỗi request
    if not current_user.is_anonymous and not current_user.confirmed_email:
        return forbidden('Chưa xác nhận email')

@api.route('/tokens/', methods=['POST', 'GET'])
def get_token() -> 'token':
    """Lấy token"""
    if current_user.is_anonymous:
        return unauthorized('Thông tin không hợp lệ')
    return jsonify({'token': current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
