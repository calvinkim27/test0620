# -*- coding: utf-8 -*-
import uuid

from sqlalchemy import types, sql, orm
from sqlalchemy.schema import Column, ForeignKey

from .base import Base, GUID
from .user import User
from midauth.utils.text import slugify

__all__ = ['Group']


class Group(Base):
    __tablename__ = 'group'

    pk = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(types.Unicode(64), nullable=False)
    slug = Column(types.Unicode(32), nullable=False)
    created_at = Column(types.DateTime(timezone=True), nullable=False,
                        default=sql.functions.now())

    users = orm.relationship(lambda: GroupAssociation, collection_class=set)

    def __init__(self, name, slug=None, users=()):
        slug = slug or slugify(name)
        self.name = name
        self.slug = slug
        self.users = set(GroupAssociation(group=self, user=u) for u in users)

    def __repr__(self):
        return u'{class_name}({0.name!r}, slug={0.slug!r})' \
            .format(self, class_name=type(self).__name__)


class GroupAssociation(Base):
    __tablename__ = 'group_association'

    user_pk = Column(GUID, ForeignKey(User.pk, onupdate='CASCADE',
                                               ondelete='CASCADE'),
                     primary_key=True)
    group_pk = Column(GUID, ForeignKey(Group.pk, onupdate='CASCADE',
                                                 ondelete='CASCADE'),
                      primary_key=True)
    created_at = Column(types.DateTime(timezone=True), nullable=False,
                        default=sql.functions.now())
    primary = Column(types.Boolean, nullable=False, default=False)

    group = orm.relationship(Group)
    user = orm.relationship(User, backref=orm.backref('group_assocs',
                                                      collection_class=set))
