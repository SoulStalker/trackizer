from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from flask_jwt_extended import JWTManager

from datetime import datetime, time

from config import DSN
from models import *

app = Flask(__name__)

client = app.test_client()

engine = create_engine(DSN)

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager()

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/api/current', methods=['GET'])
def get_tasks_list():
    """
    Tasks from Current tab
    """
    tasks = Task.query.filter(Task.completed == False, Task.start_time == None)
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
def add_new_task():
    data = request.json

    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    new_task = Task(
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
def update_task(task_id):
    task = Task.query.filter(Task.id == task_id).first()
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
def del_task(task_id):
    task = Task.query.filter(Task.id == task_id).first()
    if not task:
        return {'message': f'No task with id {task_id}'}, 400
    session.delete(task)
    session.commit()
    return '', 204


@app.route('/api/completed', methods=['GET'])
def get_completed_tasks():
    """
    Completed tasks
    """
    tasks = Task.query.filter(Task.completed == True)
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
def get_daily_tasks():
    """
    Daily tasks
    """
    tasks = Task.query.filter(Task.start_time != None)
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


@app.teardown_appcontext
def close_session(exeption=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
