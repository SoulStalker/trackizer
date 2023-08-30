from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from config import DSN

app = Flask(__name__)

engine = create_engine(DSN)
session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine
))

Base = declarative_base()
Base.query = session.query_property()

from models import *

Base.metadata.create_all(bind=engine)

tasks = {
    "1": {'title': 'step1', 'description': 'do crud in simple list'},
    "2": {'title': 'step2', 'description': 'do it in sqlalchemy'}
}


@app.route('/api/tasks', methods=['GET'])
def get_list():
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def update_list():
    new_task = request.json
    tasks.update(new_task)
    return jsonify(tasks)


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not str(task_id) in tasks.keys():
        return {'message': 'No task with this ID'}, 400
    task = tasks[str(task_id)]
    params = request.json
    task.update(params)
    return task


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def del_task(task_id):
    if not str(task_id) in tasks.keys():
        return {'message': 'No task with this ID'}, 400
    tasks.pop(str(task_id))
    return jsonify(tasks)


@app.teardown_appcontext
def close_session(exeption=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
