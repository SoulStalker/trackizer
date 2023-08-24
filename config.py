from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

DSN = 'postgresql://mpro:mpro@localhost:5432/trakizer'


def create_session(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine


db, db_engine = create_session(DSN)
Base = declarative_base()

