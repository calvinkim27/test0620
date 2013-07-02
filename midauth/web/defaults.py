import sassutils.wsgi
from . import middlewares


BLUEPRINTS = (
    ('.user', {'url_prefix': '/users'}),
    ('.group', {'url_prefix': '/groups'}),

    ('.oauth', {'url_prefix': '/oauth2'}),

    ('.admin.dashboard', {'url_prefix': '/admin'}),
    ('.admin.user', {'url_prefix': '/admin/users'}),
)


USER_PROFILE_VIEW = 'user.get'


WSGI_MIDDLEWARES = (
    middlewares.MethodRewriteMiddleware,
    lambda app: sassutils.wsgi.SassMiddleware(app, {
        'midauth.web': ('resources/sass', 'static/sass', '/static/sass'),
    }),
)
