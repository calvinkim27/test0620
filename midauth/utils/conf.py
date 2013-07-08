import os
from base64 import b64encode

from jinja2 import Environment


TEMPLATE = '''# -*- coding: utf-8 -*-

# Make this unique, and don't share it with anybody.
SECRET_KEY = {{ secret_key }}

DEBUG = True

# http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#database-urls
DATABASE_URL = 'postgresql://postgres@localhost/midauth'

GOOGLE_OAUTH2 = {
    'consumer_key': '',
    'consumer_secret': '',
}
'''


def generate_settings():
    env = Environment()
    template = env.from_string(TEMPLATE)
    context = {
        'secret_key': repr(generate_secret_key()),
    }
    return template.render(context)


def generate_secret_key(length=64):
    return b64encode(os.urandom(length))[:length]


def create_settings(filename):
    """Create new setting file interactively"""
    content = generate_settings()
    with file(filename, 'w') as f:
        f.write(content)
