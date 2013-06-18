# -*- coding: utf-8 -*-
import uuid
from datetime import datetime, timedelta

from sqlalchemy import types, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects import postgresql
from dateutil.tz import tzutc
import flufl.enum

from .base import Base, GUID
from .user import User
from .types import FluflEnum


class OAuth2GrantType(flufl.enum.Enum):
    pass


class OAuth2ResponseType(flufl.enum.Enum):
    pass


GrantTypeEnum = FluflEnum(OAuth2GrantType, name='oauth2_grant_type')
ResponseTypeEnum = FluflEnum(OAuth2ResponseType, name='oauth2_response_type')


def generate_client_secret():
    """

    :returns:
    :rtype: basestring

    """
    raise NotImplementedError()


class Client(Base):
    """외부 애플리케이션"""
    __tablename__ = 'auth_client'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    secret = Column(types.Unicode(64), nullable=False)
    name = Column(types.Unicode(40), nullable=False)
    owner_id = Column(GUID, ForeignKey(User.id, onupdate='CASCADE',
                                                ondelete='CASCADE'),
                      nullable=False)
    grant_type = Column(GrantTypeEnum, nullable=False)
    response_type = Column(ResponseTypeEnum, nullable=False)
    scopes = Column(postgresql.ARRAY(types.Unicode(80)), nullable=False)
    redirect_uri = Column(types.Unicode(), nullable=False)
    description = Column(types.UnicodeText, nullable=False)

    owner = orm.relationship(User)

    def __init__(self, name, owner, redirect_uri, description=u'',
                 id=None, secret=None):
        """

        :param name: 애플리케이션의 이름
        :type name: unicode
        :param owner: 애플리케이션을 생성한 소유자
        :type owner: midauth.models.user.User
        :keyword redirect_uri:
        :type redirect_uri: basestring
        :keyword id:
        :type id: uuid.UUID
        :keyword secret:
        :type secret: basestring
        :keyword description:
        :type description: unicode

        """
        self.name = name
        self.owner = owner
        self.redirect_uri = redirect_uri
        if isinstance(id, uuid.UUID):
            self.id = id
        elif id is None:
            # create new id
            self.id = uuid.uuid4()
        else:
            self.id = uuid.UUID(id)
        self.secret = secret or generate_client_secret()
        self.description = description

    def __repr__(self):
        return u'auth.Client(client_id={0.id!r})'.format(self)


class OAuth2Token(Base):
    """OAuth2 인증에 사용되는 토큰들의 기반 클래스"""
    __tablename__ = 'oauth2_token'

    EXPIRATION_TIME = NotImplemented

    type = Column(types.String(20), primary_key=True)
    code = Column(types.Unicode(100), primary_key=True)
    client_id = Column(GUID, ForeignKey(Client.id, onupdate='CASCADE',
                                                   ondelete='CASCADE'),
                       nullable=False)
    user_id = Column(GUID, ForeignKey(User.id, onupdate='CASCADE',
                                               ondelete='CASCADE'),
                     nullable=False)
    scopes = Column(postgresql.ARRAY(types.Unicode(80)), nullable=False)
    expires_at = Column(types.DateTime(timezone=True), nullable=True)

    client = orm.relationship(Client)
    user = orm.relationship(User)

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __init__(self, client, user, code, scopes, expires_in=None):
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
        expires_in = expires_in or self.EXPIRATION_TIME
        self.client = client
        self.user = user
        self.code = code
        self.scopes = scopes
        self.expires_at = datetime.now(tzutc()) + expires_in


class BearerToken(Token):
    """"""
    EXPIRATION_TIME = timedelta(hours=1)

    refresh_token = Column(types.Unicode(100), nullable=True, unique=True)

    __mapper_args__ = {
        'polymorphic_identity': 'bearer_token',
    }

    @hybrid_property
    def access_token(self):
        return self.code

    @access_token.setter
    def access_token(self, value):
        self.code = value

    def __init__(self, refresh_token=None, *args, **kwargs):
        super(BearerToken, self).__init__(*args, **kwargs)
        self.refresh_token = refresh_token


class AuthorizationCode(Token):
    """"""
    EXPIRATION_TIME = timedelta(minutes=10)

    __mapper_args__ = {
        'polymorphic_identity': 'authorization_code',
    }
