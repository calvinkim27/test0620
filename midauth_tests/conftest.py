# -*- coding: utf-8 -*-
import pytest
import os
import base64

import sqlalchemy
from sqlalchemy.exc import ProgrammingError

from midauth.models.base import Base
import midauth.web.application


@pytest.fixture(scope='session')
def config():
    return {
        'DATABASE_URL': 'postgresql://ecdysis@localhost/midauth_test',
        'SECRET_KEY': base64.b64encode(os.urandom(36)),
        'TESTING': True,
        'GOOGLE_OAUTH2': {
            'consumer_key': '638907643171.apps.googleusercontent.com',
            'consumer_secret': 'kjZrqFoI_ZPxK0_g2lJbNvPT',
        },
    }


@pytest.fixture(scope='session')
def engine(request, config):
    engine = sqlalchemy.create_engine(config['DATABASE_URL'])
    engine.execute('CREATE EXTENSION IF NOT EXISTS hstore')
    Base.metadata.create_all(engine)
    def fin():
        Base.metadata.drop_all(engine)
        try:
            engine.execute('DROP EXTENSION IF EXISTS hstore')
        except ProgrammingError:
            pass
    request.addfinalizer(fin)
    return engine


Session = sqlalchemy.orm.sessionmaker()


@pytest.fixture
def session(request, engine):
    connection = engine.connect()
    trans = connection.begin()
    session = Session(bind=connection)
    def fin():
        trans.rollback()
        session.close()
        connection.close()
    request.addfinalizer(fin)
    return session


@pytest.fixture()
def app(request, config, engine):
    app = midauth.web.application.create_app(config)
    app.config['SQLALCHEMY_ENGINE'] = engine
    connection = engine.connect()
    trans = connection.begin()
    app.config['SQLALCHEMY_SESSION'].bind = connection
    def fin():
        trans.rollback()
        connection.close()
    request.addfinalizer(fin)
    return app
