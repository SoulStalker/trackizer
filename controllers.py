from flask import request
from flask_restx import Namespace, Resource
from models import Task, TaskState, Base
from config import DSN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(DSN)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


api = Namespace('tasks', description='Task related operations')


@api.route('/daily')
class DailyTask(Resource):
    def get(self):
        daily_task = Task.query.filter(Task.state.has(TaskState.name == 'daily')).all()
        return [task.to_dict() for task in daily_task], 200

    def post(self):
        data = request.json
        new_task = Task(title=data['title'], description=data['description'])
        session.add(new_task)
        session.commit()
        return new_task.to_dict(), 201


@api.route('/current')
class CurrentTask(Resource):
    def get(self):
        current_tasks = Task.query.filter(Task.state.has(TaskState.name == 'current')).all()
        return [task.to_dict() for task in current_tasks], 200

    def post(self):
        data = request.json
        new_task = Task(title=data['title'], description=data['description'], state_id=2)
        # todo soulstalker поправить current_state_id после миграций
        session.add(new_task)
        session.commit()
        return new_task.to_dict(), 201


@api.route('/completed')
class CompletedTask(Resource):
    def get(self):
        competed_tasks = Task.query.filter(Task.state.has(TaskState.name == 'completed')).all
        return [task.to_dict() for task in competed_tasks], 200


api.add_resource(DailyTask, '/daily')
api.add_resource(CurrentTask, '/current')
api.add_resource(CompletedTask, '/completed')
