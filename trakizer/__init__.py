from flask import Flask
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from flask_jwt_extended import JWTManager
from .config import DSN, Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine(DSN)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager()

docs = FlaskApiSpec()

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='usertasks',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def close_session(exception=None):
    session.remove()


from .main.views import tasks
from .users.views import users

app.register_blueprint(tasks)
app.register_blueprint(users)

docs.init_app(app)
jwt.init_app(app)