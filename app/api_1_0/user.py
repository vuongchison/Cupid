from flask import jsonify, request, url_for, abort
from flask_login import current_user
from .. import db
from ..models import User
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
from geopy import distance


@api.route('/user/coordinates', methods=['POST'])
@validate_params(
    Param('latitude', JSON, float, required=True),
    Param('longitude', JSON, float, required=True),
    Param('timestamp', JSON, str, required=False)
)
def coordinates(latitude, longitude, timestamp):
    """"Lấy tọa độ người dùng
    latitude: vĩ độ
    longtitude: kinh độ
    timestamp: thời gian lấy tọa độ""""

    #Nếu tọa độ mới cách tọa độ cũ hơn 100m
    if distance.distance((latitude, longitude), current_user.coordinates).km > 0.1: 
        #Cập nhật tọa độ mới
        current_user.coordinates = (latitude, longitude)
        db.session.commit()
        #Tính khoảng cách của người dùng đến các người dùn khác
        current_user.calculate_distances()
    return jsonify({'status': 'OK'})
