import pytest
import os
import base64

import midauth.web.application


@pytest.fixture(scope='module')
def app():
    config = {
        'DATABASE_URL': 'postgresql://postgres@localhost/midauth_test',
        'SECRET_KEY': base64.b64encode(os.urandom(36)),
        'TESTING': True,
    }
    return midauth.web.application.create_app(config)
