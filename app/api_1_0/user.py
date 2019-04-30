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


@api.route('/user/coordinates', methods=['POST'])
@validate_params(
    Param('latitude', JSON, float, required=True),
    Param('longitude', JSON, float, required=True),
    Param('timestamp', JSON, str, required=False)
)
def coordinates(latitude, longitude, timestamp):
    current_user.coordinates = (latitude, longitude)
    db.session.commit()
    return jsonify({'status': 'OK'})
