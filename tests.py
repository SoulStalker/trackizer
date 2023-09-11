from app import client
from models import Task


def test_simple():
    mylist = [1, 2, 3, 4, 5]

    assert 1 in mylist


def test_get():
    res = client.get('/api/tasks')

    assert res.status_code == 200

    assert len(res.get_json()) == len(Task.query.all())
    assert res.get_json()[0]['id'] == 1


def test_post():
    data = {
        'name': 'Unit Tests',
        'description': 'Pytest tutorial'
    }

    res = client.post('/api/tasks', json=data)

    assert res.status_code == 200


def test_put():
    res = client.put('/api/tasks/1', json={'name': 'UPD'})

    assert res.status_code == 200
    assert Task.query.get(1).name == 'UPD'


def test_delete():
    res = client.delete('/tutorials/1')

    assert res.status_code == 204
    assert Task.query.get(1) is None
