from app import session, Base, db
# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time, create_engine
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from config import DSN
# Base = declarative_base()
from flask_jwt_extended import create_access_token
from datetime import timedelta


class TaskState(Base):
    __tablename__ = 'task_states'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(500), nullable=True)


class Task(Base):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    #
    state_id = db.Column(db.Integer, db.ForeignKey('task_states.id'))
    state = relationship('TaskState', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'completed': self.completed,
            'state': self.state.name if self.state else None
        }


class Users(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    tasks = relationship('Task', backref='Users', lazy=True)

    def get_token(self, expire_hours=24):
        expire_delta = timedelta(expire_hours)
        token = create_access_token(identity=self.id, expires_delta=expire_delta)
        return token





# engine = create_engine(DSN)
# Base.metadata.create_all(engine)
