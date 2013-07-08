# -*- coding: utf-8 -*-
import datetime
import urllib
import urllib2
import json

from flask import Blueprint
from flask import request
from flask import render_template, redirect, url_for, abort
import flask.ext.login
from flask.ext.login import login_required, current_user
from flask.ext.oauthlib.client import OAuthException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.inspection import inspect
import formencode.schema
import formencode.validators as _v
from formencode.compound import Pipe
from formencode.variabledecode import variable_decode
from dateutil.tz import tzutc

from midauth.models.user import User, UserStatus, Email, _LOGIN_NAME_RE
from midauth.models.cred import GoogleOAuth2
from .application import login_manager, oauth_client, get_session, respond
from .dispatch import resource_url


blueprint = Blueprint('user', __name__)

google_oauth2 = oauth_client.remote_app(
    'google_oauth2',
    request_token_params={'scope': [
        u'https://www.googleapis.com/auth/userinfo.profile',
        u'https://www.googleapis.com/auth/userinfo.email',
    ]},
    base_url=u'https://www.googleapis.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=u'https://accounts.google.com/o/oauth2/token',
    authorize_url=u'https://accounts.google.com/o/oauth2/auth',
    # for lazy loading
    # TODO: apply https://github.com/lepture/flask-oauthlib/issues/23
    consumer_key=None,
    consumer_secret=None,
)


@login_manager.user_loader
def load_user(user_id):
    s = get_session()
    return s.query(User).get(user_id)


@blueprint.route('', endpoint='list')
def list_():
    users = get_session().query(User).filter(User.active)
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

    :param user: 사용자의 login name

    :statuscode 200: 정상 요청

       ====== ===
       키     값
       ====== ===
       id     unique, 변경 불가
       login  사용자의 ID. URI에 쓸 수 있는 형태여야 함. unique, 변경 가능
       name   사용자의 실명, 변경 가능
       nick   사용자의 별명, 변경 가능
       groups 사용자가 소속된 그룹의 URI 목록
       emails 사용자의 이메일 주소 목록
       ====== ===

    :statuscode 404: 해당 이름의 사용자가 없음

    """
    s = get_session()
    try:
        user = s.query(User).filter_by(login=user).one()
    except NoResultFound:
        abort(404)
    return respond(user, 'user/get.html', picture_url=user.picture_url)


@blueprint.route('/login')
def login():
    if current_user.is_authenticated():
        return redirect(resource_url(current_user))
    next_url = request.values.get('next')
    return render_template('user/login.html', next=next_url)


@blueprint.route('/login', methods=['DELETE'])
@login_required
def logout():
    flask.ext.login.logout_user()
    next_url = request.values.get('next', url_for('.login'))
    return redirect(next_url)


class UserRegistrationSchema(formencode.schema.Schema):
    login = Pipe(validators=[
        _v.Regex(_LOGIN_NAME_RE, strip=True),
        _v.MaxLength(inspect(User).c.login.type.length),
        _v.NotEmpty(messages={'empty': 'Please enter an login'}),
    ])
    name = Pipe(validators=[
        _v.MaxLength(inspect(User).c.name.type.length),
        _v.NotEmpty(messages={'empty': 'Please enter your real name'}),
    ])


@blueprint.route('/register', methods=['POST'])
def register():
    form = variable_decode(request.form)
    s = get_session()
    try:
        user_id = form.pop('user_id')
    except KeyError:
        abort(400)
    user = s.query(User).get(user_id)
    next_url = form.pop('next', None)
    if user is None or user.status != UserStatus.unregistered:
        abort(400)
    try:
        data = UserRegistrationSchema().to_python(form)
    except formencode.Invalid as e:
        return render_template('user/register.html',
                               formdata=request.form, formerror=e.error_dict)
    user.status = UserStatus.active
    user.login = data['login']
    user.name = data['name']
    user.created_at = datetime.datetime.now(tzutc())
    s.commit()
    flask.ext.login.login_user(user)
    if not next_url:
        next_url = resource_url(user)
    return redirect(next_url)


def register_form(user):
    if not isinstance(user, User):
        raise TypeError('user should be a {0!r}, not {1!r}'.format(User, user))
    formdata = {
        'login': user.login,
        'name': user.name,
        'next': request.values.get('next', ''),
        'user_id': user.pk,
    }
    return render_template('user/register.html',
                           formdata=formdata)


@blueprint.route('/auth/google')
def auth_google():
    return google_oauth2.authorize(callback=url_for('.auth_google_after',
                                                    _external=True))


@blueprint.route('/auth/google/callback')
@google_oauth2.authorized_handler
def auth_google_after(resp):
    if resp is None:
        return 'Access denied: ' \
               'reason={0.error_reason} error={0.error_description}' \
            .format(request.args)
    elif isinstance(resp, OAuthException):
        return redirect(url_for('.auth_google'))
    id_token = decode_jwt(resp['id_token'])
    user_key = id_token['user_id']
    s = get_session()
    try:
        cred = s.query(GoogleOAuth2).filter_by(key=user_key).one()
    except NoResultFound:
        # 회원가입
        token = (resp['access_token'], '')
        r = google_oauth2.get('oauth2/v3/userinfo', token=token)
        userinfo = r.data
        user = User(None, userinfo['name'], status=UserStatus.unregistered)
        user.emails.append(Email(userinfo['email'], verified=True))
        user.primary_email = userinfo['email']
        cred = GoogleOAuth2(user, resp, user_key=user_key)
        s.add(user)
        s.add(cred)
        s.commit()
    if cred.user.status == UserStatus.unregistered:
        return register_form(cred.user)
    else:
        # 로그인
        cred.token = resp
        s.commit()
        flask.ext.login.login_user(cred.user)
        next_url = request.values.get('next', resource_url(cred.user))
        return redirect(next_url)


def decode_jwt(token):
    """주어진 JWT 토큰을 디코드함

    .. seealso:: `Validating an ID Token <https://developers.google.com/accounts/docs/OAuth2Login?hl=ko#validatinganidtoken>`_

    """
    r = urllib2.urlopen('https://www.googleapis.com/oauth2/v1/tokeninfo',
                        data=urllib.urlencode({'id_token': token}))
    return json.load(r)
