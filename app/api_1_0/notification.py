from flask import jsonify, request, url_for, abort
from flask_login import current_user
from .. import db
from ..models import Notification, User
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
    Param('timestamp', JSON, str, required=False),
)
def get_news_noti(timestamp):
    # print(current_user.notifications.all())
    if (current_user.new_noti == 0):
        res = []
    else:
        timestamp = dateutil.parser.parse(timestamp)
        res = current_user.notifications.filter_by(read=False).filter(Notification.timestamp >= timestamp).limit(current_user.new_noti).all()
        res = [{'id': n.id, 'image': n.image, 'body': n.body, 'link': n.link, 'timestamp': n.timestamp.isoformat()} for n in res]
    return jsonify({'notifications': res})