# -*- coding: utf-8 -*-
import uuid
import os
import base64
from datetime import datetime, timedelta

from sqlalchemy import types, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects import postgresql
from dateutil.tz import tzutc

from .base import Base, GUID
from .user import User


def generate_client_secret():
    """

    :returns:
    :rtype: bytes

    """
    return base64.urlsafe_b64encode(os.urandom(48))


class Client(Base):
    """외부 애플리케이션

    .. seealso:: https://flask-oauthlib.readthedocs.org/en/latest/api.html#flask_oauthlib.provider.OAuth2Provider.clientgetter

    """
    __tablename__ = 'oauth2_client'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    secret = Column(types.String(64), nullable=False)
    name = Column(types.Unicode(40), nullable=False)
    description = Column(types.UnicodeText, nullable=False)
    default_scopes = Column(postgresql.ARRAY(types.Unicode(80)), nullable=False)
    redirect_uris = Column(postgresql.ARRAY(types.Unicode(255)), nullable=False)

    @property
    def client_id(self):
        return self.id.hex

    @hybrid_property
    def client_secret(self):
        return self.secret

    @property
    def client_type(self):
        return 'public'

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    def __init__(self, name, redirect_uris, description=u'',
                 id=None, secret=None):
        """

        :param name: 애플리케이션의 이름
        :type name: unicode
        :keyword redirect_uris:
        :type redirect_uris: collections.Iterable
        :keyword id:
        :type id: uuid.UUID
        :keyword secret:
        :type secret: basestring
        :keyword description:
        :type description: unicode

        """
        self.name = name
        self.redirect_uris = redirect_uris
        if isinstance(id, uuid.UUID):
            self.id = id
        elif id is None:
            # create new id
            self.id = uuid.uuid4()
        else:
            self.id = uuid.UUID(id)
        self.secret = secret or generate_client_secret()
        self.description = description
        self.default_scopes = [u'user']

    def __repr__(self):
        return u'auth.Client(id={0.id!r})'.format(self)


class GrantToken(Base):
    __tablename__ = 'oauth2_grant_token'

    EXPIRATION_TIME = timedelta(minutes=5)

    code = Column(types.Unicode(100), primary_key=True)
    client_id = Column(GUID, ForeignKey(Client.id, onupdate='CASCADE',
                                                   ondelete='CASCADE'),
                       nullable=False)
    user_id = Column(GUID, ForeignKey(User.id, onupdate='CASCADE',
                                               ondelete='CASCADE'),
                     nullable=False)
    scopes = Column(postgresql.ARRAY(types.Unicode(80)), nullable=False)
    expires_at = Column(types.DateTime(timezone=True), nullable=False)
    redirect_uri = Column(types.Unicode(255), nullable=False)

    client = orm.relationship(Client)
    user = orm.relationship(User)

    @property
    def expires(self):
        return self.expires_at.astimezone(tzutc()).replace(tzinfo=None)

    def delete(self):
        session = orm.session.object_session(self)
        session.delete(self)
        session.commit()
        return self

    def __init__(self, client, user, code, scopes, redirect_uri):
        """

        :param client:
        :type client: Client
        :param user:
        :type user: User
        :param code:
        :type code: basestring
        :param scopes:
        :type scopes: collections.Iterable
        :keyword expires_in:
        :type expires_in: datetime.timedelta

        """
        self.client = client
        self.user = user
        self.code = code
        self.scopes = scopes
        self.expires_at = datetime.now(tzutc()) + self.EXPIRATION_TIME
        self.redirect_uri = redirect_uri


class BearerToken(Base):
    __tablename__ = 'oauth2_bearer_token'

    access_token = Column(types.Unicode(100), primary_key=True)
    client_id = Column(GUID, ForeignKey(Client.id, onupdate='CASCADE',
                                                   ondelete='CASCADE'),
                       nullable=False)
    user_id = Column(GUID, ForeignKey(User.id, onupdate='CASCADE',
                                               ondelete='CASCADE'),
                     nullable=False)
    scopes = Column(postgresql.ARRAY(types.Unicode(80)), nullable=False)
    expires_at = Column(types.DateTime(timezone=True), nullable=True)
    refresh_token = Column(types.Unicode(100), nullable=True, unique=True)

    client = orm.relationship(Client)
    user = orm.relationship(User)

    @hybrid_property
    def expires(self):
        """

        .. seealso:: https://flask-oauthlib.readthedocs.org/en/latest/api.html#flask_oauthlib.provider.OAuth2Provider.tokengetter

        """
        return self.expires_at.astimezone(tzutc()).replace(tzinfo=None)

    def __init__(self, client, user, access_token, scopes, expires_in,
                 refresh_token=None):
        """

        :param client:
        :type client: Client
        :param user:
        :type user: User
        :param access_token:
        :type access_token: basestring
        :keyword scopes:
        :type scopes: collections.Iterable
        :keyword expires_in:
        :type expires_in: datetime.timedelta

        """
        if not isinstance(expires_in, timedelta):
            expires_in = timedelta(seconds=expires_in)
        self.client = client
        self.user = user
        self.access_token = access_token
        self.scopes = scopes
        self.expires_at = datetime.now(tzutc()) + expires_in
        self.refresh_token = refresh_token
