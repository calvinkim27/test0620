# -*- coding: utf-8 -*-
import pytest


def test_redirect_to_oauth_provider(app):
    with app.test_client() as client:
        r = client.get('/users/auth/google')
        assert 300 <= r.status_code < 400
        google_auth_url = 'https://accounts.google.com/o/oauth2/auth'
        assert r.location.startswith(google_auth_url)
