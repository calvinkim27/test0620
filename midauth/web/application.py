import types
import collections

import flask
from flask import current_app, redirect, url_for
from flask.ext.login import LoginManager
from flask.ext.oauthlib.client import OAuth
import formencode_jinja2
import sqlalchemy.orm
from flask import json

import midauth.models.user
from midauth.utils import importlib
from . import defaults
from . import dispatch
from .ext import OAuth2Provider


login_manager = LoginManager()
login_manager.anonymous_user = midauth.models.user.AnonymousUser

current_user = flask.ext.login.current_user

oauth2 = OAuth2Provider()
oauth_client = OAuth()


def create_app(config):
    app = flask.Flask('midauth.web')
    app.config.from_object(defaults)
    if isinstance(config, collections.Mapping):
        app.config.update(config)
    else:
        app.config.from_pyfile(config)
    login_manager.init_app(app)
    oauth2.init_app(app)
    init_oauth_client(app)
    init_sqla_session(app, app.config['DATABASE_URL'])
    init_error_handlers(app)
    init_blueprints(app, app.config['BLUEPRINTS'])
    login_manager.login_view = 'user.login'
    load_middlewares(app, app.config['WSGI_MIDDLEWARES'])
    init_jinja_env(app)
    return app


def init_sqla_session(app, db_url):
    app.config['SQLALCHEMY_ENGINE'] = engine = sqlalchemy.create_engine(db_url)
    app.config['SQLALCHEMY_SESSION'] = sqlalchemy.orm.sessionmaker(bind=engine)
    app.teardown_appcontext(teardown_sqla_sessions)


def init_error_handlers(app):
    @app.errorhandler(404)
    def handle_page_not_found(e):
        response = respond(None, '404.html')
        response.status_code = 404
        return response


def init_blueprints(app, blueprints):
    for blueprint_name, kwargs in blueprints:
        if isinstance(blueprint_name, basestring):
            blueprint = importlib.import_string(blueprint_name, 'midauth.web')
        else:
            blueprint = blueprint_name
        if isinstance(blueprint, types.ModuleType):
            blueprint = getattr(blueprint, 'blueprint')
        app.register_blueprint(blueprint, **kwargs)
    app.add_url_rule('/', 'home', home)
    app.add_url_rule('/user', 'user', user)


def load_middlewares(app, middlewares):
    for middleware in reversed(middlewares):
        app.wsgi_app = middleware(app.wsgi_app)


def init_jinja_env(app):
    app.jinja_env.add_extension(formencode_jinja2.formfill)
    app.jinja_env.globals.update(
        current_user=current_user,
        resource_url=dispatch.resource_url,
    )


def init_oauth_client(app):
    # TODO: apply https://github.com/lepture/flask-oauthlib/issues/23
    from .user import google_oauth2
    config = app.config['GOOGLE_OAUTH2']
    google_oauth2.consumer_key = config['consumer_key']
    google_oauth2.consumer_secret = config['consumer_secret']
    oauth_client.init_app(app)


def get_session():
    ctx = flask._app_ctx_stack.top
    assert ctx is not None
    session = current_app.config['SQLALCHEMY_SESSION']()
    if not hasattr(ctx, 'sqla_sessions'):
        ctx.sqla_sessions = []
    ctx.sqla_sessions.append(session)
    return session


def teardown_sqla_sessions(exc=None):
    ctx = flask._app_ctx_stack.top
    sessions = getattr(ctx, 'sqla_sessions', [])
    while sessions:
        s = sessions.pop()
        s.close()


def respond(object_to_response, template_name_or_list, **context):
    responders = collections.OrderedDict([
        ('text/html', respond_html),
        ('application/xhtml+xml', respond_html),
        ('application/json', respond_json),
        ('text/javascript', respond_json),
    ])
    match = flask.request.accept_mimetypes.best_match(responders.keys(),
                                                      'text/html')
    if not match:
        flask.abort(406)
    else:
        response = responders[match](object_to_response,
                                     template_name_or_list,
                                     context)
        response = flask.make_response(response)
        response.mimetype = match
        return response


def respond_html(obj, template, context):
    return flask.render_template(template, obj=obj, **context)


def respond_json(obj, template, context):
    simplified = dispatch.simplify(obj)
    if isinstance(simplified, list):
        raise ValueError(
            'Responding a JSON array is restricted.\n'
            'see also: http://flask.pocoo.org/docs/security/#json-security')
    return json.dumps(simplified, indent=None if flask.request.is_xhr else 2)


def home():
    return redirect(url_for(current_app.login_manager.login_view))


def user():
    if not current_user.is_authenticated():
        flask.abort(404)
    else:
        endpoint = current_app.config['USER_PROFILE_VIEW']
        return current_app.view_functions[endpoint](user=current_user.login)
