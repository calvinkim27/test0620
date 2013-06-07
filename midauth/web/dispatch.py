# -*- coding: utf-8 -*-
import datetime
import uuid

import flask
from singledispatch import singledispatch

from midauth import models
from midauth.utils import gravatar


@singledispatch
def resource_url(obj):
    raise NotImplementedError


@resource_url.register(models.user.User)
def _(obj):
    return flask.url_for('user.get', user=obj.username, _external=True)


@singledispatch
def simplify(value):
    """"""
    raise NotImplementedError


def simplified_obj(**attributes):
    return {k: simplify(v) for k, v in attributes.iteritems()}


@simplify.register(int)
@simplify.register(long)
@simplify.register(float)
@simplify.register(basestring)
@simplify.register(type(None))
def _(value):
    return value


@simplify.register(list)
def _(value):
    return [simplify(i) for i in value]


@simplify.register(dict)
def _(value):
    return {simplify(k): simplify(v) for k, v in value.iteritems()}


@simplify.register(uuid.UUID)
def _(value):
    assert isinstance(value, uuid.UUID)
    return value.hex


@simplify.register(datetime.datetime)
def _(value):
    assert isinstance(value, datetime.datetime)
    return value.isoformat('T')


@simplify.register(models.user.User)
def _(value):
    assert isinstance(value, models.user.User)
    return simplified_obj(
        login=value.username,
        id=value.id,
        avatar_url=value.picture_url(),
        gravatar_id=gravatar.gravatar_id(value.primary_email),
        url=resource_url(value),
        name=value.name,
        email=value.primary_email,
        created_at=value.created_at,
        type=u'User',
    )
