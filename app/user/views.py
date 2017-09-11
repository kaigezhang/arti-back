from flask import Blueprint, request
from flask_apispec import use_kwargs, marshal_with
from flask_jwt import current_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from .models import User
from .serializers import user_schema
from app.database import db
from app.exceptions import InvalidUsage
# from app.extensions import cors
from app.profile.models import UserProfile
from app.utils import jwt_optional

blueprint = Blueprint('users', __name__)


@blueprint.route('/api/users', methods=('POST',))
@use_kwargs(user_schema)
@marshal_with(user_schema)
def register_user(username, email, password, **kwargs):
    # user, profile的关系还是没有搞清楚
    try:
        userprofile = UserProfile(User(username, email, password=password).save()).save()
    except IntegrityError:
        db.session.rollback()
        raise InvalidUsage.user_already_registered()
    return userprofile.user


@blueprint.route('/api/users/login', methods=('POST',))
@jwt_optional()
@use_kwargs(user_schema)
@marshal_with(user_schema)
def login_user(email, password, **kwargs):
    user = User.query.filter_by(email=email).first()
    if user is not None and user.check_password(password):
        return user
    else:
        raise InvalidUsage.user_not_found()


@blueprint.route('/api/user', methods=['GET'])
@jwt_required()
@marshal_with(user_schema)
def get_user():
    return current_identity


@blueprint.route('/api/user', methods=['PUT'])
@jwt_required()
@use_kwargs(user_schema)
@marshal_with(user_schema)
def update_user(**kwargs):
    user = current_identity
    password = kwargs.pop('password', None)
    if password:
        user.set_password(password)
    if 'updated_at' in kwargs:
        kwargs['updated_at'] = user.created_at.replace(tzinfo=None)
    user.update(**kwargs)
    return user
