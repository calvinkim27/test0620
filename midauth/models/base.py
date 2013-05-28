# -*- coding: utf-8 -*-
import sqlalchemy.ext.declarative
from sqlalchemy.dialects import postgresql


class Base(object):
    pass

#:
Base = sqlalchemy.ext.declarative.declarative_base(cls=Base)


#: .. todo::
#:
#:    다른 DB와의 호환을 고려한다면 제일 먼저 이 컬럼을 손봐야 함.
#:    다행히, PostgreSQL UUID도 특별한 기능이 있는 건 아님.
#:    bigint나 char 등으로 쉽게 대체 가능할 듯.
ID = postgresql.UUID(as_uuid=True)
