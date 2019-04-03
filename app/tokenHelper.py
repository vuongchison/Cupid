from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app import mail


def gen(data, expiration=43200):
    s = Serializer(current_app.config.get('SECRET_KEY'), expiration)
    return s.dumps(data).decode('utf-8')

def check(token, *args, **kwargs):
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