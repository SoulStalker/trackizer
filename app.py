from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import datetime, time
from config import DSN, Config
from models import *

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine(DSN)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/api/current', methods=['GET'])
@jwt_required()
def get_tasks_list():
    """
    Tasks from Current tab
    """
    user_id = get_jwt_identity()
    tasks = Task.query.filter(
        Task.completed == False,
        Task.start_time == None,
        Task.user_id == user_id
    )
    serialized = []
    for task in tasks:
        serialized.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        })
    return jsonify(serialized)


@app.route('/api', methods=['POST'])
@jwt_required()
def add_new_task():
    user_id = get_jwt_identity()
    data = request.json

    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    new_task = Task(
        user_id=user_id,
        title=data['title'],
        description=data['description'],
        start_time=datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None,
        end_time=datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None
    )
    session.add(new_task)
    session.commit()
    serialized = {
        'id': new_task.id,
        'title': new_task.title,
        'description': new_task.description,
        'completed': False,
    }
    return jsonify(serialized)


@app.route('/api/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter(Task.id == task_id, Task.user_id == user_id).first()
    params = request.json
    if not task:
        return {'message': f'No task with id {task_id}'}, 400
    for key, value in params.items():
        setattr(task, key, value)
    session.commit()
    serialized = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.completed,
    }
    return serialized


@app.route('/api/<int:task_id>', methods=['DELETE'])
@jwt_required()
def del_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        return {'message': f'No task with id {task_id}'}, 400
    session.delete(task)
    session.commit()
    return '', 204


@app.route('/api/completed', methods=['GET'])
@jwt_required()
def get_completed_tasks():
    """
    Completed tasks
    """
    user_id = get_jwt_identity()
    tasks = Task.query.filter(Task.completed == True, Task.user_id == user_id)
    serialized = []
    for task in tasks:
        serialized.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        })
    return jsonify(serialized)


@app.route('/api/daily', methods=['GET'])
@jwt_required()
def get_daily_tasks():
    """
    Daily tasks
    """
    user_id = get_jwt_identity()
    tasks = Task.query.filter(Task.start_time != None, Task.user_id == user_id)
    serialized = []
    for task in tasks:
        serialized.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'start_time': task.start_time.strftime('%H:%M') if task.start_time else None,
            'end_time': task.end_time.strftime('%H:%M') if task.end_time else None,
            'completed': task.completed,
        })
    return jsonify(serialized)


@app.route('/api/signup', methods=['POST'])
def signup():
    params = request.json
    user = Users(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/api/signin', methods=['POST'])
def signin():
    params = request.json
    user = Users.auth(**params)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def close_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
