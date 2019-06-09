from flask import jsonify, request, url_for, abort
from flask_login import current_user
from .. import db
from ..models import Notification, User, Post, PostNoti, ReadPostNoti, Follow
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

@api.route('/notification/get_news', methods=['POST'])
@validate_params(
    Param('timestamp', JSON, str, required=True),
)
def get_news_noti(timestamp):
    """Lấy các thông báo mới kể từ thời điểm timestamp"""

    allpostnoti = []
    newpostnoti = PostNoti.query.join(Follow, Follow.follower_id==current_user.id).all()
    for npn in newpostnoti:
        #Chưa đọc
        if ReadPostNoti.query.filter_by(user_id=current_user.id, postnoti_id=npn.id).first() is None:
            author = User.query.get(npn.user_id)
            post = Post.query.get(npn.post_id)
            allpostnoti.append({'body': '%s đã đăng 1 bài đăng mới' % (author.name), 'link': url_for('main.post', uuid=post.uuid)})
            rpn = ReadPostNoti(user_id=current_user.id, postnoti_id=npn.id)
            db.session.add(rpn)
    
    db.session.commit()

    res = []
    if (current_user.new_noti == 0):
        res = []
        pass
    else:
        timestamp = dateutil.parser.parse(timestamp)
        res = current_user.notifications.filter_by(read=False).filter(Notification.timestamp >= timestamp).limit(current_user.new_noti).all()
        res = [{'id': n.id, 'image': n.image, 'body': n.body, 'link': n.link, 'timestamp': n.timestamp.isoformat()} for n in res]
    res+=allpostnoti
    return jsonify({'notifications': res, 'new_noti': current_user.new_noti})