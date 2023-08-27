from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from config import DSN
Base = declarative_base()


class TaskState(Base):
    __tablename__ = 'task_states'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(200), nullable=True)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    completed = Column(Boolean, default=False)

    state_id = Column(Integer, ForeignKey('task_states.id'))
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


engine = create_engine(DSN)
Base.metadata.create_all(engine)
