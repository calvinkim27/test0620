import sassutils.wsgi
from . import middlewares


BLUEPRINTS = (
    ('.dashboard', {}),
    ('.user', {'url_prefix': '/users'}),
)


WSGI_MIDDLEWARES = (
    middlewares.MethodRewriteMiddleware,
    lambda app: sassutils.wsgi.SassMiddleware(app, {
        'midauth.web': ('resources/sass', 'static/sass', '/static/sass'),
    }),
)
