from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from config import DSN
from models import *

app = Flask(__name__)

client = app.test_client()

engine = create_engine(DSN)

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/api/tasks', methods=['GET'])
def get_tasks_list():
    tasks = Task.query.all()
    serialized = []
    for task in tasks:
        serialized.append({
            'id': task.id,
            'title': task.title,
            'description': task.description
        })
    return jsonify(serialized)


@app.route('/api/tasks', methods=['POST'])
def add_new_task():
    new_task = Task(**request.json)
    session.add(new_task)
    session.commit()
    serialized = {
        'id': new_task.id,
        'title': new_task.title,
        'description': new_task.description
    }
    return jsonify(serialized)


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.filter(Task.id == task_id).first()
    params = request.json
    if not task:
        return {'message': f'No task with id {task_id}'}, 400
    for k, v in params.items():
        setattr(task, k, v)
    session.commit()
    serialized = {
        'id': task.id,
        'title': task.title,
        'description': task.description
    }
    return serialized


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def del_task(task_id):
    task = Task.query.filter(Task.id == task_id).first()
    if not task:
        return {'message': f'No task with id {task_id}'}, 400
    session.delete(task)
    session.commit()
    return '', 204


@app.teardown_appcontext
def close_session(exeption=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
