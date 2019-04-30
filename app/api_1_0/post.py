from flask import jsonify, request, url_for, abort
from flask_login import current_user
from .. import db
from ..models import User, Post
from . import api
from .errors import forbidden, page_not_found
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

@api.route('/post/like', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True)
)
def like_post(uuid):
    p = Post.query.filter_by(uuid=uuid).first_or_404()
    current_user.like(p)
    return jsonify({'count_likes': p.count_likes})
    


