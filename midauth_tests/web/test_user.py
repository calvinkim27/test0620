# -*- coding: utf-8 -*-
import pytest
from midauth.web import user as web_user


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


def test_wrong_args_to_register_form():
    with pytest.raises(TypeError):
        web_user.register_form(42)


def test_register(app):
    with app.test_client() as client:
        r = client.post('/users/register')
        assert r.status_code == 400
