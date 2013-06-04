# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint
from flask import request, session, current_app
from flask import render_template, redirect, url_for, abort
import flask.ext.login
from flask.ext.login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.inspection import inspect
import formencode.schema
import formencode.validators as _v
from formencode.compound import Pipe
from formencode.variabledecode import variable_decode
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import InvalidGrantError
from dateutil.tz import tzutc

from midauth.models.user import User, Email, _USERNAME_RE
from midauth.models.cred import GoogleOAuth2
from .application import login_manager, get_session


blueprint = Blueprint('user', __name__)


@login_manager.user_loader
def load_user(user_id):
    s = get_session()
    return s.query(User).get(user_id)


@blueprint.route('', endpoint='list')
def list_():
    users = []
    return render_template('user/list.html', users=users)


@blueprint.route('/<user>')
def get(user):
    """사용자 정보를 불러옵니다.

    **응답 예시**:

    .. code-block:: http

       HTTP/1.1 200 OK
       Vary: Accept
       Content-Type: application/json

       {
         “id” : “19b76b9c3b924a9bb3cc482732f019e4”,
         “uid”: “kroisse”,
         “name”: “유은총”,
         “nick”: “가제트”,
         “groups”: [
           “http://midauth-sample.smartstudy.co.kr/groups/devops”,
           “http://midauth-sample.smartstudy.co.kr/groups/developers”,
           “http://midauth-sample.smartstudy.co.kr/groups/task-force”,
         ],
         “emails”: [
           “kroisse@smartstudy.co.kr”,
           “kroisse@gmail.com”,
         ]
       }

    :param user_name: 사용자의 username

    :statuscode 200: 정상 요청

       ====== ===
       키     값
       ====== ===
       id     unique, 변경 불가
       uid    사용자의 ID. URI에 쓸 수 있는 형태여야 함. unique, 변경 가능
       name   사용자의 실명, 변경 가능
       nick   사용자의 별명, 변경 가능
       groups 사용자가 소속된 그룹의 URI 목록
       emails 사용자의 이메일 주소 목록
       ====== ===

    :statuscode 404: 해당 이름의 사용자가 없음

    """
    s = get_session()
    try:
        user = s.query(User).filter_by(username=user).one()
    except NoResultFound:
        abort(404)
    return render_template('user/get.html', user=user)


@blueprint.route('/login')
def login():
    if current_user.is_authenticated():
        return redirect(url_for('.get', user=current_user.username))
    next_url = request.values.get('next', url_for('dashboard.home'))
    return render_template('user/login.html', next=next_url)


@blueprint.route('/login', methods=['DELETE'])
@login_required
def logout():
    flask.ext.login.logout_user()
    next_url = request.values.get('next', url_for('dashboard.home'))
    return redirect(next_url)


class UserRegistrationSchema(formencode.schema.Schema):
    username = Pipe(validators=[
        _v.Regex(_USERNAME_RE, strip=True),
        _v.MaxLength(inspect(User).c.username.type.length),
        _v.NotEmpty(messages={'empty': 'Please enter an username'}),
    ])
    name = Pipe(validators=[
        _v.MaxLength(inspect(User).c.name.type.length),
        _v.NotEmpty(messages={'empty': 'Please enter your real name'}),
    ])


@blueprint.route('/register', methods=['POST'])
def register():
    form = variable_decode(request.form)
    s = get_session()
    user = s.query(User).get(form.pop('user_id'))
    next_url = form.pop('next', url_for('dashboard.home'))
    if user.status != User.UNREGISTERED:
        abort(400)
    try:
        data = UserRegistrationSchema().to_python(form)
    except formencode.Invalid as e:
        return render_template('user/register.html',
                               formdata=request.form, formerror=e.error_dict)
    user.status = User.ACTIVE
    user.username = data['username']
    user.name = data['name']
    user.created_at = datetime.datetime.now(tzutc())
    s.commit()
    flask.ext.login.login_user(user)
    return redirect(next_url)


def get_oauth_session(cred, sqla_session=None):
    def token_updater(token):
        cred.value = token
    return OAuth2Session(
        current_app.config['GOOGLE_CLIENT_ID'],
        token=cred.value,
        auto_refresh_url='https://accounts.google.com/o/oauth2/token',
        auto_refresh_kwargs={
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'grant_type': 'refresh_token',
        },
        token_updater=token_updater
    )


def register_form(user):
    formdata = {
        'username': user.username,
        'name': user.name,
        'next': request.values.get('next', ''),
        'user_id': user.id,
    }
    return render_template('user/register.html',
                           formdata=formdata)


@blueprint.route('/auth/google')
def auth_google():
    client_id = current_app.config['GOOGLE_CLIENT_ID']
    auth_url = u'https://accounts.google.com/o/oauth2/auth'
    oauth_session = OAuth2Session(
        client_id,
        scope=[
            u'https://www.googleapis.com/auth/userinfo.profile',
            u'https://www.googleapis.com/auth/userinfo.email',
        ],
        redirect_uri=url_for('.auth_google_after', _external=True),
    )
    dest, session['state'] = oauth_session.authorization_url(
        auth_url, access_type='offline')
    return redirect(dest)


@blueprint.route('/auth/google/callback')
def auth_google_after():
    if request.args['state'] != session.get('state'):
        return redirect(url_for('.auth_google'))
    if 'error' in request.args:
        abort(401)
    client_id = current_app.config['GOOGLE_CLIENT_ID']
    client_secret = current_app.config['GOOGLE_CLIENT_SECRET']
    token_url = u'https://accounts.google.com/o/oauth2/token'
    oauth_session = OAuth2Session(
        client_id,
        redirect_uri=url_for('.auth_google_after', _external=True),
    )
    try:
        token = oauth_session.fetch_token(token_url, request.args['code'],
                                          client_secret=client_secret)
    except InvalidGrantError:
        return redirect(url_for('.auth_google'))
    id_token = decode_jwt(token['id_token'])
    user_key = id_token['user_id']
    s = get_session()
    try:
        cred = s.query(GoogleOAuth2).filter_by(key=user_key).one()
    except NoResultFound:
        # 회원가입
        r = oauth_session.get('https://www.googleapis.com/oauth2/v3/userinfo')
        userinfo = r.json()
        user = User(None, userinfo['name'], status=User.UNREGISTERED)
        user.emails.append(Email(userinfo['email'], verified=True))
        user.primary_email = userinfo['email']
        cred = GoogleOAuth2(user, token, user_key=user_key)
        s.add(user)
        s.add(cred)
        s.commit()
    if cred.user.status == User.UNREGISTERED:
        return register_form(cred.user)
    else:
        # 로그인
        cred.token = token
        s.commit()
        flask.ext.login.login_user(cred.user)
        next_url = request.values.get('next', url_for('dashboard.home'))
        return redirect(next_url)


def decode_jwt(token):
    """주어진 JWT 토큰을 디코드함

    .. seealso:: `Validating an ID Token <https://developers.google.com/accounts/docs/OAuth2Login?hl=ko#validatinganidtoken>`_

    """
    r = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo',
                     params={'id_token': token})
    return r.json()
