from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Task, TaskState, Base, engine


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

