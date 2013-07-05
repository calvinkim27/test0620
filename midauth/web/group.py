# -*- coding: utf-8 -*-
from flask import Blueprint, abort, render_template
from sqlalchemy.orm.exc import NoResultFound

from .application import get_session, respond
from midauth.models.group import Group


blueprint = Blueprint('group', __name__)


@blueprint.route('', endpoint='list')
def list_():
    s = get_session()
    groups = s.query(Group)
    return render_template('group/list.html', groups=groups)


@blueprint.route('/<group>')
def get(group):
    """그룹의 정보와 그룹에 속한 사용자의 목록을 불러옵니다.

    :param group: 그룹의 slug

    :statuscode 200: 정상 요청

       ====== ===
       키     값
       ====== ===
       id     unique, 변경 불가
       slug   URI에 쓸 수 있는 형태의 그룹 이름. unique, 변경 가능
       name   그룹 이름, 변경 가능
       users  그룹에 소속된 사용자의 URI 목록
       ====== ===

    :statuscode 404: 해당 이름의 그룹이 없음

    """
    s = get_session()
    try:
        group = s.query(Group).filter_by(slug=group).one()
    except NoResultFound:
        abort(404)
    response = {
        'id': group.pk,
        'slug': group.slug,
        'name': group.name,
        'users': (u.user for u in group.users),
    }
    return respond(response, 'group/get.html')
