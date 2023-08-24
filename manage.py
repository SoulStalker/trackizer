from flask.cli import FlaskGroup
from app import apple
from config import db
from flask_migrate import Migrate


migrate = Migrate(apple, db)
cli = FlaskGroup(apple)


if __name__ == '__main__':
    cli()




