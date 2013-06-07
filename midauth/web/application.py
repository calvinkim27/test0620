import types
import collections

import flask
from flask import current_app, redirect, url_for
from flask.ext.login import LoginManager
import formencode_jinja2
import sqlalchemy.orm

import midauth.models.user
from midauth.utils import importlib
from . import defaults
from . import dispatch


login_manager = LoginManager()
login_manager.anonymous_user = midauth.models.user.AnonymousUser

current_user = flask.ext.login.current_user


def create_app(config):
    app = flask.Flask(__name__)
    app.config.from_object(defaults)
    if isinstance(config, collections.Mapping):
        app.config.update(config)
    else:
        app.config.from_pyfile(config)
    login_manager.init_app(app)
    init_sqla_session(app, app.config['DATABASE_URL'])
    init_blueprints(app, app.config['BLUEPRINTS'])
    login_manager.login_view = 'user.login'
    load_middlewares(app, app.config['WSGI_MIDDLEWARES'])
    init_jinja_env(app)
    return app


def init_sqla_session(app, db_url):
    app.config['SQLALCHEMY_ENGINE'] = engine = sqlalchemy.create_engine(db_url)
    app.config['SQLALCHEMY_SESSION'] = sqlalchemy.orm.sessionmaker(bind=engine)
    app.teardown_appcontext(teardown_sqla_sessions)


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


def load_middlewares(app, middlewares):
    for middleware in reversed(middlewares):
        app.wsgi_app = middleware(app.wsgi_app)


def init_jinja_env(app):
    app.jinja_env.add_extension(formencode_jinja2.formfill)
    app.jinja_env.globals.update(
        current_user=current_user,
    )


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
    simplified = dispatch.simplify(object_to_response)
    if flask.request.accept_mimetypes.accept_html:
        simplified.update(context)
        return flask.render_template(template_name_or_list, **simplified)
    if flask.request.accept_mimetypes.accept_json:
        return flask.jsonify(**simplified)
    else:
        flask.abort(406)


def home():
    return redirect(url_for(current_app.login_manager.login_view))
