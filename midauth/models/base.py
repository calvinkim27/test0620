# -*- coding: utf-8 -*-
import sqlalchemy.ext.declarative
from sqlalchemy import types
from sqlalchemy.dialects import postgresql
import uuid


class Base(object):
    pass

#:
Base = sqlalchemy.ext.declarative.declarative_base(cls=Base)


class GUID(types.TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    .. seealso:: http://docs.sqlalchemy.org/en/rel_0_8/core/types.html#backend-agnostic-guid-type

    """
    impl = types.CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(types.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)
