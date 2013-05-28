import sassutils.wsgi


BLUEPRINTS = (
    ('.dashboard', {}),
    ('.user', {'url_prefix': '/users'}),
)


WSGI_MIDDLEWARES = (
    lambda app: sassutils.wsgi.SassMiddleware(app, {
        'midauth.web': ('resources/sass', 'static/sass', '/static/sass'),
    }),
)
