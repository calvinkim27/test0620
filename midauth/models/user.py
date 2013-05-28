# -*- coding: utf-8 -*-
import re
import datetime
import uuid

from sqlalchemy import types, sql, orm
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.tz import tzutc

from .base import Base, ID
from midauth.utils import gravatar

__all__ = ['User', 'AnonymousUser', 'Email']

_USERNAME_RE = re.compile('^[\w.-]+$')


class User(Base):
    """사용자를 나타내는 모델

    """
    __tablename__ = 'user'

    #: 사용자가 등록되기 전임
    UNREGISTERED = 'unregistered'
    #: 가입된 사용자
    ACTIVE = 'active'
    #: 사용자가 탈퇴하거나 계정이 정지됨
    INACTIVE = 'inactive'

    USER_STATUS = UNREGISTERED, ACTIVE, INACTIVE

    id = Column(ID, primary_key=True, default=uuid.uuid4)
    username = Column(
        types.Unicode(30), unique=True, nullable=True,
        doc="""로그인할 때 사용되는 계정 이름

            30자 미만의 영문자, 숫자, 또는 ./-/_로 이루어집니다.

        """,
    )
    name = Column(types.Unicode(60), nullable=False)
    status = Column(
        types.Enum(name='user_status', *USER_STATUS),
        nullable=False, default=UNREGISTERED,
        doc="""계정의 현재 상태""")
    created_at = Column(types.DateTime(timezone=True),
                        default=sql.functions.now())

    emails = orm.relationship(
        lambda: Email,
        doc="""사용자의 이메일 목록""",
    )
    primary_email = Column(
        types.Unicode, nullable=True,
        doc="""사용자의 주 이메일"""
    )

    @hybrid_property
    def active(self):
        """사용자가 활성화된 상태인지를 결정

        계정을 삭제하는 대신 이 값을 해제하세요.

        """
        return self.status == self.ACTIVE

    @active.setter
    def active(self, value):
        self.status = self.ACTIVE if value else self.INACTIVE

    @orm.validates('username')
    def validate_username(self, key, username):
        if self.status == self.UNREGISTERED:
            assert username is None
        else:
            assert username not in ('.', '_')
            assert _USERNAME_RE.match(username), 'Enter a valid username.'
        return username

    @orm.validates('primary_email')
    def validate_primary_email(self, key, email):
        if email is None:
            return email
        assert email in (e.address for e in self.emails if e.verified)
        return email

    def __init__(self, username, name, emails=(),
                 status=UNREGISTERED, created_at=None):
        """

        :param unicode username: 계정명
        :param unicode name: 사용자의 실명
        :keyword collections.Iterable emails: 이메일 목록
        :keyword status: 계정 활성화 여부
        :type status: :obj:`UNREGISTERED` or :obj:`ACTIVE` or :obj:`INACTIVE`
        :keyword datetime created_at: 계정 생성 시각

        """
        if not created_at:
            created_at = datetime.datetime.now(tzutc())
        # status에 따라 다른 필드를 어떻게 검증할지가 바뀌기 때문에,
        # 가장 먼저 대입되어야 함.
        self.status = status
        self.username = username
        self.name = name
        self.created_at = created_at
        self.emails = [Email(address=e) for e in emails]

    def __repr__(self):
        return u'User({0.username!r}, {0.name!r}, active={0.active!r})' \
            .format(self)

    def picture_url(self, size=44):
        """사용자의 프로필 사진을 가리키는 URL

        """
        email = self.primary_email or self.emails[0].address
        return gravatar.image_url(email, size=size)

    def is_authenticated(self):
        """인증된 사용자인지의 여부"""
        return self.active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class AnonymousUser(object):
    """인증되지 않은 익명의 사용자"""
    id = None
    active = False

    def is_authenticated(self):
        return self.active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return True

    def get_id(self):
        return None


class Email(Base):
    __tablename__ = 'email'

    user_id = Column(ID, ForeignKey(User.id, onupdate='CASCADE',
                                             ondelete='CASCADE'),
                     primary_key=True)
    address = Column(types.Unicode, primary_key=True, unique=True)
    verified = Column(types.Boolean, nullable=False, default=False)

    def __init__(self, address, verified=False):
        self.address = address
        self.verified = verified
