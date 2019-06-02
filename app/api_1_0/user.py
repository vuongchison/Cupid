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
    # print('coordinates')
    if distance.distance((latitude, longitude), current_user.coordinates).km > 0.1: 
        current_user.coordinates = (latitude, longitude)
        db.session.commit()
        # print('calculate')
        current_user.calculate_distances()
    return jsonify({'status': 'OK'})
