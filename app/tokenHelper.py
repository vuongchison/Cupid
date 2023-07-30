from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from app import mail


def gen(data:dict, expiration:int=43200) -> str:
    """Sinh token từ dữ liệu data với thời hạn expiration.
    - Trả về xâu token với mã hóa utf-8"""

    s = Serializer(current_app.config.get('SECRET_KEY'), expiration)
    return s.dumps(data).decode('utf-8')

def check(token:str, *args:list, **kwargs:dict) -> str:
    """Kiểm tra token xem có hợp lệ không. 
    Token sau khi giải mã phải có các tham số *args, và các cặp tham số - giá trị tương ứng như trong **kwargs.
    - Trả về dữ liệu sau khi giải mã nếu hợp lệ.
    - Trả về False nếu không hợp lệ."""
    
    decoder = Serializer(current_app.config.get('SECRET_KEY'))

    try:
        data = decoder.loads(token.encode('utf-8'))
    except:
        return False
    
    for arg in args:
        if data.get(arg) is None:
            return False

    for k, v in kwargs.items():
        if data.get(k) != v:
            return False
    
    return data