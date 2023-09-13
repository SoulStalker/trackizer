from flask import Blueprint
from trakizer import session, docs
from trakizer.schemas import TaskSchema
from flask_apispec import use_kwargs, marshal_with
from trakizer.models import Task
from flask_jwt_extended import jwt_required, get_jwt_identity

tasks = Blueprint('tasks', __name__)


@tasks.route('/api/current', methods=['GET'])
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


@tasks.route('/api/completed', methods=['GET'])
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


@tasks.route('/api/daily', methods=['GET'])
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


@tasks.route('/api', methods=['POST'])
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


@tasks.route('/api/<int:task_id>', methods=['PUT'])
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


@tasks.route('/api/<int:task_id>', methods=['DELETE'])
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


docs.register(get_tasks_list, blueprint='tasks')
docs.register(get_daily_tasks, blueprint='tasks')
docs.register(get_completed_tasks, blueprint='tasks')
docs.register(add_new_task, blueprint='tasks')
docs.register(update_task, blueprint='tasks')
docs.register(del_task, blueprint='tasks')