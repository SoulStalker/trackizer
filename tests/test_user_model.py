def test_model(user):
    assert user.name == 'Testuser'


def test_user_login(user, client):
    res = client.post('/signin', json={
        'email': user.email,
        'password': user.get_token()
    })
    assert res.get_json().get('access_token')


def test_user_signup(client):
    res = client.post('/signup', json={
        'name': 'Testuser',
        'email': 'test@tesrt.ru',
        'password': 'password'
    })
    assert res.status_code == 200
    assert res.get_json().get('access_token')