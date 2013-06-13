# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

from ..application import get_session
from midauth.models.user import User
from midauth.models.group import Group
from .dashboard import restrict_blueprint_to_admins


blueprint = Blueprint('admin.user', __name__)

blueprint.before_request(restrict_blueprint_to_admins)


@blueprint.route('', endpoint='list')
def list_():
    s = get_session()
    groups = s.query(Group)
    users = s.query(User).filter(~User.group_assocs.any())
    return render_template('admin/user/list.html', groups=groups, users=users)
