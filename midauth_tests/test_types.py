# -*- coding: utf-8 -*-
import pytest
import sqlalchemy
from sqlalchemy.schema import Column
import flufl.enum
from midauth.models.types import FluflEnum


def dump_create_ddl(schema):
    buffer = []
    def dump(sql, *multiparams, **params):
        buffer.append(sql.compile(dialect=engine.dialect))
    engine = sqlalchemy.create_engine('postgresql://', strategy='mock',
                                      executor=dump)
    schema.create(bind=engine, checkfirst=False)
    return str(buffer[0])


class Colors(flufl.enum.Enum):
    red, green, blue = xrange(3)


def test_create_ddl_flufl_enum():
    t = FluflEnum(Colors)
    assert t.enum_cls == Colors
    with pytest.raises(sqlalchemy.exc.CompileError) as e:
        dump_create_ddl(t)
    assert 'ENUM type requires a name' in str(e)
    t = FluflEnum(Colors, name='color')
    expected = 'CREATE TYPE color AS ENUM ({0})'.format(
        ','.join(repr(i.name) for i in Colors))
    assert expected == dump_create_ddl(t)
