import pytest
import sys

sys.path.append('..')

from trakizer import app, Base, engine, session as db_session
from trakizer.models import Users


@pytest.yield_fixture(scope='function')
def testapp():
    _app = app

    Base.metadata.create_all(bind=engine)
    _app.connection = engine.connect()

    yield app

    Base.metadata.drop_all(bind=engine)
    _app.connection.close()


@pytest.fixture(scope='function')
def session(testapp):
    ctx = app.app_context()
    ctx.push()

    yield db_session

    db_session.close_all()
    ctx.pop()


@pytest.fixture(scope='function')
def user(session):
    user = Users(
        name='Testuser',
        email='test@test.ru',
        password='password'
    )
    session.add(user)
    session.commit()

    return user


@pytest.fixture
def client(testapp):
    return testapp.test_clent()


@pytest.fixture
def user_token(user, client):
    res = client.post('/signin', json={
        'email': user.email,
        'password': 'password'
    })
    return res.get_json()['access_token']


@pytest.fixture
def user_headers(user_token):
    headers = {
        'Authorization': f'Bearer {user_token}'
    }
    return headers
