# -*- coding: utf-8 -*-
import pytest
from .db import engine, session
from midauth.models.user import User, UserStatus
from midauth.models.group import Group


def test_basic_group(session):
    u1 = User(u'test1', u'Testimonial', status=UserStatus.active)
    u2 = User(u'test2', u'Testifier', status=UserStatus.active)
    session.add(u1)
    session.add(u2)
    group = Group(u'Recommended', users=[u1])
    session.add(group)
    assert u1 in {u.user for u in group.users}
    assert u2 not in {u.user for u in group.users}
    assert group in {g.group for g in u1.group_assocs}
    assert group not in {g.group for g in u2.group_assocs}
