import sqlalchemy.orm
from midauth.web.application import get_session


def test_open_session(app):
    with app.app_context():
        s = get_session()
        assert isinstance(s, sqlalchemy.orm.Session)
        s2 = get_session()
        assert isinstance(s2, sqlalchemy.orm.Session)
        assert s is not s2


def test_close_session_after_appcontext(app):
    closed = [False]
    with app.app_context():
        s = get_session()
        old_close = s.close
        def close():
            closed[0] = True
            old_close()
        s.close = close
        assert not closed[0]
    assert closed[0]
