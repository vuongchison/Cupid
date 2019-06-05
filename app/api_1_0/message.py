from flask import jsonify, request, url_for, abort
from flask_login import current_user
from .. import db
from ..models import Message, LastMessage, User
from . import api
from .errors import forbidden
from flask_request_validator import (
    PATH,
    JSON,
    Param,
    Pattern,
    validate_params
)
from html import escape
from datetime import datetime
import dateutil.parser
from flask_images import resized_img_src




@api.route('/message/get_news', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True),
    Param('count', JSON, int, required=False),
    Param('last_id', JSON, int, required=False),
)
def get_news(uuid:str, count:int, last_id:int):
    """Lấy các tin nhắn mới
    uuid: uuid của người dùng
    count: số tin nhắn cần lấy
    last_id: lấy các tin nhắn mới hơn tin nhắn có id là last_id
    Có count và không có last_id: lấy count tin nhắn mới nhất (kể cả tin nhắn đã đọc lẫn chưa đọc)
    Ngược lại có last_id: lấy tất cả tin nhắn mới hơn last_id
    Đánh dấu tất cả tin nhắn lấy được là đã đọc"""

    u = User.query.filter_by(uuid=uuid).first_or_404()

    if last_id is None and count:
        res = current_user.get_latest_messages(u).limit(count).all()
        
    else:
        m = Message.query.get(last_id)
        if m is None:
            abort(404)
        else:
            res = current_user.get_latest_messages(u).filter( Message.id > m.id ).all()
   
   #Đánh dấu các tin nhắn lấy được thành đã được đọc
    for m in res:
        if m.read == False and m.receiver_id == current_user.id:
            current_user.new_message -= 1
        m.read = True

    if current_user.new_message < 0:
        current_user.new_message = 0

    db.session.commit()

    res = [m.todict() for m in res]
    return jsonify({'messages': res})


@api.route('/message/get_olds', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True),
    Param('count', JSON, int, required=True),
    Param('last_id', JSON, int, required=True),
)
def get_olds(uuid:str, count:int, last_id:int):
    """Lấy các tin nhắn cũ
    uuid: uuid của người dùng
    count: số lượng các tin nhắn cần lấy
    last_id: lấy các tin nhắn cũ hơn tin nhắn có id này"""

    #Tìm người dùng bằng uuid
    u = User.query.filter_by(uuid=uuid).first_or_404()

    m = Message.query.get(last_id)
    if m is None:
        abort(404)
    else:
        res = current_user.get_latest_messages(u).filter( Message.id < m.id ).limit(count).all()
    #Đánh dấu các tin nhắn thành đã đọc
    for m in res:
        if not m.read and m.receiver_id == current_user.id:
            current_user.new_message -= 1
        m.read = True

    if current_user.new_message < 0:
        current_user.new_message = 0

    db.session.commit()

    res = [m.todict() for m in res]    
    
    return jsonify({'messages': res})



@api.route('/message/send', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True),
    Param('body', JSON, str, required=True),
)
def send(uuid:str, body:str):
    """Gửi tin nhắn đến người dùng có uuid với nội dung body"""
    #Tìm người dùng bằng uuid
    u = User.query.filter_by(uuid=uuid).first_or_404()
    #Nếu không match
    if not current_user.is_match_with(u):
        #Không có quyền nhắn tin
        abort(403)

    body = escape(body.strip())
    m = current_user.message(u, body)

    return jsonify({'id': m.id, 'timestamp': m.timestamp.isoformat()})


@api.route('/message/check-news', methods=['POST'])
@validate_params(
    Param('timestamp', JSON, str, required=True),
)
def message_check_news(timestamp):
    """Kiểm tra xem có tin nhắn mới kể từ thời điểm timestamp hay không"""
    if (current_user.new_message == 0):
        res = []
    else:
        timestamp = dateutil.parser.parse(timestamp)
        res = current_user.message_r.filter_by(read=False).filter(Message.timestamp >= timestamp).limit(current_user.new_message).all()
        res = [{'id': m.id, 'user': {'uuid': m.sender.uuid, 'name': m.sender.name, 'avatar': resized_img_src(m.sender.avatar, width=48, height=48, mode='crop') }, 'link': url_for('main.inbox', uuid=m.sender.uuid), 'timestamp': m.timestamp.isoformat()} for m in res]
    return jsonify({'messages': res, 'new_message': current_user.new_message})    
