from flask import Blueprint
from trakizer import session, docs
from trakizer.schemas import UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with
from trakizer.models import Users

users = Blueprint('users', __name__)


@users.route('/api/signup', methods=['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def signup(**kwargs):
    user = Users(**kwargs)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@users.route('/api/signin', methods=['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthSchema)
def signin(**kwargs):
    user = Users.auth(**kwargs)
    token = user.get_token()
    return {'access_token': token}


docs.register(signup, blueprint='users')
docs.register(signin, blueprint='users')
