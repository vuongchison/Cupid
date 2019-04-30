from flask import Blueprint

api = Blueprint('api', __name__)

from . import message, notification, post, errors, authentication, user