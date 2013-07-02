# -*- coding: utf-8 -*-
from midauth.models import auth


def test_generate_secret():
    secret = auth.generate_client_secret()
    assert isinstance(secret, basestring)
