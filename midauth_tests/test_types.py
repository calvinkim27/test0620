# -*- coding: utf-8 -*-
import pytest
import sqlalchemy
from sqlalchemy.schema import Table, Column, MetaData
import flufl.enum
from midauth.models.types import FluflEnum


def dump_create_ddl(schema):
    buffer = []
    def dump(sql, *multiparams, **params):
        buffer.append(sql.compile(dialect=engine.dialect))
    engine = sqlalchemy.create_engine('postgresql://localhost/postgres',
                                      strategy='mock', executor=dump)
    schema.create(bind=engine, checkfirst=False)
    return ';'.join(str(i) for i in buffer)


class Colors(flufl.enum.Enum):
    red, green, blue = xrange(3)


def test_create_ddl_flufl_enum():
    metadata = MetaData()
    table = Table('test1', metadata,
        Column('color', FluflEnum(Colors)),
    )
    assert table.c.color.type.enum_cls == Colors
    expected = 'CREATE TYPE colors AS ENUM ({0})'.format(
        ','.join(repr(i.name) for i in Colors))
    assert expected in dump_create_ddl(table)
    table = Table('test2', metadata,
        Column('color', FluflEnum(Colors, name='color_enum_type')),
    )
    expected = 'CREATE TYPE color_enum_type AS ENUM ({0})'.format(
        ','.join(repr(i.name) for i in Colors))
    assert expected in dump_create_ddl(table)
