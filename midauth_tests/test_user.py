# -*- coding: utf-8 -*-
import pytest
from .db import engine, session
import uuid

from midauth.models.user import User, AnonymousUser, UserStatus


def test_user(session):
    """Check that users can be created and can set their password"""
    u = User(u'testuser', u'Test User', status=UserStatus.active)
    # Check authentication/permissions
    assert u.is_authenticated()
    assert u.active
    assert not u.id
    session.add(u)
    session.commit()
    assert isinstance(u.id, uuid.UUID)


@pytest.mark.skipif('True')
def test_user_password_auth():
    u = User(u'testuser', u'Test User')
    # Check user creation with no password
    # assert not u.has_usable_password()

    assert u.has_usable_password()
    assert not u.check_password('bad')
    assert u.check_password('testpw')

    # Check we can manually set an unusable password
    u.set_unusable_password()
    u.save()
    assert not u.check_password('testpw')
    assert not u.has_usable_password()
    u.set_password('testpw')
    assert u.check_password('testpw')
    u.set_password(None)
    assert not u.has_usable_password()


def test_anonymous_user():
    """Check the properties of the anonymous user"""
    a = AnonymousUser()
    assert a.id is None
    assert not a.is_authenticated()
    assert not a.active
    # assert not a.is_staff
    # assert not a.is_superuser
    # assert a.groups.all().count() == 0
    # assert a.user_permissions.all().count() == 0


def test_get_picture_url():
    user = User(u'eunchong', u'은총', ['eunchong@a.com'],
                status=UserStatus.active)
    url = user.picture_url()
    assert url.startswith('http')
