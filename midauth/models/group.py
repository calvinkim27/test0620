# -*- coding: utf-8 -*-
import uuid

from sqlalchemy import types, sql
from sqlalchemy.schema import Column, ForeignKey

from .base import Base, GUID
from .user import User

__all__ = ['Group']


class Group(Base):
    __tablename__ = 'group'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(types.Unicode(64), nullable=False)
    slug = Column(types.Unicode(32), nullable=False)
    created_at = Column(types.DateTime(timezone=True), nullable=False,
                        default=sql.functions.now)



class UserGroup(Base):
    __tablename__ = 'user_group'

    user_id = Column(GUID, ForeignKey(User.id, onupdate='CASCADE',
                                               ondelete='CASCADE'),
                     primary_key=True)
    group_id = Column(GUID, ForeignKey(Group.id, onupdate='CASCADE',
                                                 ondelete='CASCADE'),
                      primary_key=True)
