# -*- coding: utf-8 -*-
from sqlalchemy import types
import flufl.enum

from midauth.utils import text


class FluflEnum(types.SchemaType, types.TypeDecorator):
    """

    .. seealso::

       - http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/

    """
    def __init__(self, enum_cls, name=None):
        """

        :type enum_cls: flufl.enum.Enum

        """
        if not issubclass(enum_cls, flufl.enum.Enum):
            raise TypeError('enum_cls should be a flufl.enum.Enum, not {0!r}'
                            .format(enum_cls))
        args = tuple(i.name for i in enum_cls)
        name = name or text.underscored(enum_cls.__name__)
        self.impl = types.Enum(*args, name=name)
        self.enum_cls = enum_cls

    def _set_table(self, table, column):
        self.impl._set_table(table, column)

    def copy(self):
        return FluflEnum(self.enum_cls, name=self.impl.name)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.name
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = self.enum_cls[value]
        return value
