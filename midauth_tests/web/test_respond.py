# -*- coding: utf-8 -*-
import pytest
from . import app as _app
import datetime
import flask
import jinja2
from flask import json
from dateutil.tz import tzutc
from midauth.web.application import respond


TEMPLATES = {
    'test.html': 'response: {{ obj }}',
}


@pytest.fixture(scope='module')
def app(_app):
    _app.jinja_env.loader = jinja2.ChoiceLoader([
        jinja2.DictLoader(TEMPLATES),
        _app.jinja_env.loader,
    ])
    return _app


DATA = [
    (None,),
    (123,),
    ({'hello': 'world!'},),
]


@pytest.mark.parametrize(('data',), DATA)
def test_respond_default_to_html(app, data):
    with app.test_request_context():
        assert not flask.request.accept_mimetypes
        response = respond(data, 'test.html')
        assert response.mimetype == 'text/html'
        assert 'response: {0}'.format(flask.escape(data)) == response.data


@pytest.mark.parametrize(('data', ), DATA)
def test_respond_json(app, data):
    with app.test_request_context(
            headers={'Accept': 'application/json, */*;q=0.5'}):
        assert flask.request.accept_mimetypes
        response = respond(data, 'test.html')
        assert response.mimetype == 'application/json'
        assert data == json.loads(response.data)


def test_respond_json_array_should_fail(app):
    with app.test_request_context(headers={'Accept': 'application/json'}):
        assert flask.request.accept_mimetypes
        with pytest.raises(ValueError):
            respond([1, 2, 3], 'test.html')
