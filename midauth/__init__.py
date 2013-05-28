VERSION = '0.1.0.dev1'

try:
    from psycopg2cffi import compat as _compat
except ImportError:
    pass
else:
    _compat.register()
