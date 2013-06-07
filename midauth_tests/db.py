# -*- coding: utf-8 -*-
import pytest
import sqlalchemy
from midauth.models.base import Base


@pytest.fixture(scope='session')
def engine(request):
    engine = sqlalchemy.create_engine('postgresql://ecdysis@localhost/midauth_test')
    engine.execute('CREATE EXTENSION IF NOT EXISTS hstore')
    Base.metadata.create_all(engine)
    def fin():
        Base.metadata.drop_all(engine)
        engine.execute('DROP EXTENSION IF EXISTS hstore')
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
