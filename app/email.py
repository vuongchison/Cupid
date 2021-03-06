from flask_mail import Message
from app import mail
from flask import current_app, render_template
from threading import Thread

def send_email(subject:str, to:list, template:str, **kwargs:dict):
    """Gửi email đến 1 danh sách email.
    subject: chủ đề email
    to: danh sách người nhận
    template: mẫu email
    **kwargs: danh sách các tham số"""
    app = current_app._get_current_object()
    msg = Message(subject, sender='Admin <%s>'%app.config.get('MAIL_USERNAME'), recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)