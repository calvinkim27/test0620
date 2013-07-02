# -*- coding: utf-8 -*-
import uuid

import flask
from flask.ext.login import login_required

from .application import oauth2, get_session
from midauth.models import auth


blueprint = flask.Blueprint('oauth', __name__)


@blueprint.route('/authorize')
@login_required
@oauth2.authorize_handler
def authorize(client_id, **kwargs):
    if flask.request.method == 'GET':
        client_id = uuid.UUID(client_id)
        s = get_session()
        client = s.query(auth.Client).get(client_id)
        return flask.render_template('oauth/authorize.html',
                                     client=client, **kwargs)
    else:
        confirm = flask.request.form.get('confirm', 'no')
        return confirm == 'yes'


@blueprint.route('/token', methods=['POST'])
@oauth2.token_handler
def access_token():
    return None


@blueprint.route('/error')
def error():
    flask.abort(400)
