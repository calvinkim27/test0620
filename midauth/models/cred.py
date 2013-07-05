# -*- coding: utf-8 -*-
"""Google이나 Facebook 같은 외부 서비스에서 제공하는 인증 정보를 다룹니다.

"""
import collections

from sqlalchemy import types, sql, orm
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects import postgresql

from .base import Base, GUID
from .user import User


__all__ = ['Credential', 'GoogleOAuth2']


class Credential(Base):
    """:class:`User`\ 가 가진 인증 수단"""
    __tablename__ = 'credential'

    user_pk = Column(GUID, ForeignKey(User.pk, onupdate='CASCADE',
                                               ondelete='CASCADE'),
                     primary_key=True)
    type = Column(types.Unicode(20), primary_key=True)
    key = Column(types.Unicode(256), primary_key=True)
    value = Column(postgresql.HSTORE, nullable=False)
    created_at = Column(types.DateTime(timezone=True),
                        default=sql.functions.now())
    updated_at = Column(types.DateTime(timezone=True),
                        onupdate=sql.functions.now())

    user = orm.relationship(User)

    __mapper_args__ = {
        'polymorphic_on': type,
    }


class GoogleOAuth2(Credential):
    """Google OAuth2 인증

    .. seealso:: `Using OAuth 2.0 for Login <https://developers.google.com/accounts/docs/OAuth2Login>`_

    """
    __mapper_args__ = {
        'polymorphic_identity': 'google_oauth2',
    }

    def __init__(self, user, token, user_key=None):
        """

        :param midauth.models.user.User user:
        :param dict token:

        """
        self.user = user
        self.key = user_key
        self.token = token

    @hybrid_property
    def token(self):
        return self.value

    @token.setter
    def token(self, value):
        if not isinstance(value, collections.Mapping):
            raise TypeError('value should be a collections.Mapping, not {0!r}'
                            .format(value))
        self.value = dict((k, unicode(v)) for k, v in value.iteritems())

    @orm.validates('token')
    def validate_token(self, key, token):
        assert 'access_token' in token
