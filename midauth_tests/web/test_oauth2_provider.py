# -*- coding: utf-8 -*-
import pytest

from oauthlib.oauth2 import WebApplicationClient

from midauth.models import auth
from midauth.models.user import User, UserStatus
from midauth.web.application import get_session


redirect_uri = 'https://sample.midauth.org/auth'


@pytest.fixture
def oauth2_client(app):
    with app.app_context():
        session = get_session()
        client = auth.Client(u'Test sample', [redirect_uri],
                             description=u'This is test.')
        session.add(client)
        session.commit()
        assert isinstance(client.client_id, bytes)
        assert isinstance(client.client_secret, basestring)
        return client.client_id, client.client_secret


@pytest.fixture
def user(app):
    with app.app_context():
        session = get_session()
        user = User(u'eunchongyu', u'유은총', (u'kroisse@smartstudy.co.kr',),
                    status=UserStatus.active)
        session.add(user)
        session.commit()
        return user.get_id()


def test_oauth2(app, user, oauth2_client):
    client_id, client_secret = oauth2_client
    client = WebApplicationClient(client_id)
    host = 'https://localhost'
    state = 'randomly_text'

    with app.test_client() as provider:
        # login forcefully.
        with provider.session_transaction() as sess:
            sess['user_id'] = user
            sess['_fresh'] = True
        uri = client.prepare_request_uri(host + '/oauth2/authorize',
                                         redirect_uri=redirect_uri,
                                         state=state)
        uri = uri[len(host):]
        # step 1: redirect to provider
        response = provider.get(uri, follow_redirects=True)
        assert response.status_code == 200
        # step 2: redirect to client
        response = provider.post(uri, data={
            'scope': 'user', 'confirm': 'yes',
        })
        assert response.location.startswith(redirect_uri)
        data = client.parse_request_uri_response(response.location,
                                                 state=state)
        assert 'code' in data
        # step 3: get the token
        body = client.prepare_request_body(
            code=data['code'],
            redirect_uri=redirect_uri,
        )
        response = provider.post(
            '/oauth2/token',
            content_type='application/x-www-form-urlencoded',
            data=body)
        assert response.status_code == 200
        data = client.parse_request_body_response(response.data)
        assert 'access_token' in data
        assert data['token_type'] == 'Bearer'
        assert data['scope'] == ['user']
        # step 4: using token
        pass
