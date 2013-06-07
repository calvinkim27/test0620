import sassutils.wsgi
from . import middlewares


BLUEPRINTS = (
    ('.user', {'url_prefix': '/users'}),
)


USER_PROFILE_VIEW = 'user.get'


WSGI_MIDDLEWARES = (
    middlewares.MethodRewriteMiddleware,
    lambda app: sassutils.wsgi.SassMiddleware(app, {
        'midauth.web': ('resources/sass', 'static/sass', '/static/sass'),
    }),
)
