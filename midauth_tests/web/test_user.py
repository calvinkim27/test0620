# -*- coding: utf-8 -*-


def test_get_wrong_user(app):
    with app.test_client() as client:
        r = client.get('/users/nothing')
        assert r.status_code == 404
        assert r.content_type.startswith('text/html')
        r = client.get('/users/nothing',
                       headers={'Accept': 'application/json'})
        assert r.status_code == 404
        assert r.content_type.startswith('application/json')
        assert r.data is 'null'
