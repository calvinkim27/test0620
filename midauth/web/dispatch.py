# -*- coding: utf-8 -*-
import collections
import datetime
import uuid

import flask
import werkzeug.local
from singledispatch import singledispatch
from dateutil.tz import tzutc

from midauth import models
from midauth.utils import gravatar


@singledispatch
def resource_url(obj):
    raise NotImplementedError('resource_url() is not implemented for {!r}'
                              .format(obj))


@resource_url.register(werkzeug.local.LocalProxy)
def _(obj):
    return resource_url(obj._get_current_object())


@resource_url.register(models.user.User)
def _(obj):
    return flask.url_for('user.get', user=obj.login, _external=True)


@resource_url.register(models.group.Group)
def _(obj):
    return flask.url_for('group.get', group=obj.slug, _external=True)


@singledispatch
def simplify(value):
    """"""
    raise NotImplementedError('simplify() is not implemented for {!r}'
                              .format(value))


def simplified_obj(**attributes):
    return {k: simplify(v) for k, v in attributes.iteritems()}


@simplify.register(int)
@simplify.register(long)
@simplify.register(float)
@simplify.register(basestring)
@simplify.register(type(None))
def _(value):
    return value


@simplify.register(collections.Iterable)
@simplify.register(list)
def _(value):
    return [simplify(i) for i in value]


@simplify.register(collections.Mapping)
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
    return value.astimezone(tzutc()).isoformat('T')


@simplify.register(models.user.User)
def _(value):
    assert isinstance(value, models.user.User)
    return simplified_obj(
        login=value.login,
        id=value.id,
        avatar_url=value.picture_url(),
        gravatar_id=gravatar.gravatar_id(value.primary_email),
        url=resource_url(value),
        name=value.name,
        email=value.primary_email,
        created_at=value.created_at,
        type=u'User',
    )
