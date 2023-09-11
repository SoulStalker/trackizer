from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import DSN, Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import TaskSchema, UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with
from models import *

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine(DSN)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()
docs.init_app(app)

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='usertasks',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

Base.metadata.create_all(bind=engine)


@app.route('/api/current', methods=['GET'])
@jwt_required()
@marshal_with(TaskSchema(many=True))
def get_tasks_list():
    """
    Tasks from Current tab
    """
    try:
        user_id = get_jwt_identity()
        tasks = Task.query.filter(
            Task.completed == False,
            Task.start_time == None,
            Task.user_id == user_id
        )
    except Exception:
        return {'message': str(Exception)}, 400
    return tasks


@app.route('/api/completed', methods=['GET'])
@jwt_required()
@marshal_with(TaskSchema(many=True))
def get_completed_tasks():
    """
    Completed tasks
    """
    try:
        user_id = get_jwt_identity()
        tasks = Task.query.filter(Task.completed == True, Task.user_id == user_id)
    except Exception:
        return {'message': str(Exception)}, 400
    return tasks


@app.route('/api/daily', methods=['GET'])
@jwt_required()
@marshal_with(TaskSchema(many=True))
def get_daily_tasks():
    """
    Daily tasks
    """
    try:
        user_id = get_jwt_identity()
        tasks = Task.query.filter(Task.start_time != None, Task.user_id == user_id)
    except Exception:
        return {'message': str(Exception)}, 400
    return tasks


@app.route('/api', methods=['POST'])
@jwt_required()
@use_kwargs(TaskSchema)
@marshal_with(TaskSchema)
def add_new_task(**kwargs):
    try:
        user_id = get_jwt_identity()
        new_task = Task(user_id=user_id, **kwargs)
        session.add(new_task)
        session.commit()
    except Exception:
        return {'message': str(Exception)}, 400
    return new_task


@app.route('/api/<int:task_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(TaskSchema)
@marshal_with(TaskSchema)
def update_task(task_id, **kwargs):
    user_id = get_jwt_identity()
    task = Task.query.filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        return {'message': f'No task with id {task_id}'}, 400
    for key, value in kwargs.items():
        setattr(task, key, value)
    session.commit()
    return task


@app.route('/api/<int:task_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(TaskSchema)
def del_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            return {'message': f'No task with id {task_id}'}, 400
        session.delete(task)
        session.commit()
    except Exception:
        return {'message': str(Exception)}, 400
    return '', 204


@app.route('/api/signup', methods=['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def signup(**kwargs):
    user = Users(**kwargs)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/api/signin', methods=['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthSchema)
def signin(**kwargs):
    user = Users.auth(**kwargs)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def close_session(exception=None):
    session.remove()


@app.errorhandler(422)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Invalid input params: {messages}')
    if headers:
        return jsonify({'message': messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400


docs.register(get_tasks_list)
docs.register(get_daily_tasks)
docs.register(get_completed_tasks)
docs.register(add_new_task)
docs.register(update_task)
docs.register(del_task)
docs.register(signup)
docs.register(signin)

if __name__ == '__main__':
    app.run(debug=True, threaded=False)
