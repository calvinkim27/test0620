# -*- coding: utf-8 -*-
import flask

from ..application import get_session
from midauth.models import auth


blueprint = flask.Blueprint('admin.oauth', __name__)


@blueprint.route('', endpoint='list')
def list_():
    s = get_session()
    clients = s.query(auth.Client)
    return flask.render_template('admin/oauth/list.html', clients=clients)
