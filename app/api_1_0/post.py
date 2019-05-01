from flask import jsonify, request, url_for, abort
from flask_login import current_user
from .. import db
from ..models import User, Post, Comment
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
    

@api.route('/post/comment', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True),
    Param('body', JSON, str, required=True)
)
def comment(uuid, body):
    p = Post.query.filter_by(uuid=uuid).first_or_404()
    body = escape(body.strip())
    c = current_user.comment(p, body)
    return jsonify({'id': c.id, 'timestamp': c.timestamp.isoformat()})


@api.route('/post/comment/get_news', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True),
    Param('count', JSON, int, required=False),
    Param('last_id', JSON, int, required=False),
)
def comment_get_news(uuid, count, last_id):
    p = Post.query.filter_by(uuid=uuid).first_or_404()

    if not last_id and count:
        res = p.get_latest_comments().limit(count).all()
        
    else:
        c = Comment.query.get(last_id)
        if c is None:
            abort(404)
        else:
            res = p.get_latest_comments().filter( Comment.id > c.id ).all()
   
    res = [c.todict() for c in res]
    return jsonify({'comments': res})


@api.route('/post/comment/get_olds', methods=['POST'])
@validate_params(
    Param('uuid', JSON, str, required=True),
    Param('count', JSON, int, required=True),
    Param('last_id', JSON, int, required=True),
)
def comment_get_olds(uuid, count, last_id):
    p = Post.query.filter_by(uuid=uuid).first()
    if p is None:
        return page_not_found('Post không tồn tại')

    c = Comment.query.get(last_id)
    if c is None:
        return page_not_found('Comment last_id: %d không tồn tại' % (last_id))
    else:
        res = p.get_latest_comments().filter(Comment.id < c.id ).limit(count).all()

    res = [c.todict() for c in res]
    return jsonify({'comments': res})

