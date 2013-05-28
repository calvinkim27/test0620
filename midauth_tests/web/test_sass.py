# -*- coding: utf-8 -*-
from . import app


def test_access_compiled_css(app):
    with app.test_client() as client:
        response = client.get('/static/sass/main.scss.css')
        assert response.status_code < 400
