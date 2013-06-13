# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app
from flask.ext.login import current_user


blueprint = Blueprint('admin.dashboard', __name__)


@blueprint.before_request
def restrict_blueprint_to_admins():
    """

    .. seealso:: http://flask.pocoo.org/snippets/59/

    """
    if not current_user.is_authenticated():
        return current_app.login_manager.unauthorized()


@blueprint.route('')
def home():
    return render_template('admin/dashboard.html')


@blueprint.route('/status')
def status():
    config = dict(current_app.config)
    return render_template('admin/status.html', config=config)
