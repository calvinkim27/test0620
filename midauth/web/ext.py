# -*- coding: utf-8 -*-
import uuid
from sqlalchemy.orm.session import object_session
from flask.ext.login import current_user
from flask.ext.oauthlib.provider import OAuth2Provider as BaseProvider

from midauth.models.auth import Client, GrantToken, BearerToken


class OAuth2Provider(BaseProvider):
    def get_session(self):
        """

        :return:
        :rtype: sqlalchemy.orm.session.Session

        """
        from .application import get_session
        return get_session()

    def _clientgetter(self, client_id):
        """

        :param client_id:
        :return:
        :rtype: midauth.models.auth.Client

        """
        client_pk = uuid.UUID(client_id)
        s = self.get_session()
        client = s.query(Client).get(client_pk)
        return client

    def _grantgetter(self, client_id, code):
        client_pk = uuid.UUID(client_id)
        s = self.get_session()
        g = s.query(GrantToken).filter_by(client_pk=client_pk, code=code).one()
        return g

    def _grantsetter(self, client_id, code, request, *args, **kwargs):
        client = self._clientgetter(client_id)
        s = object_session(client)
        user = s.merge(current_user._get_current_object())
        assert client.client_id == request.client.client_id
        grant = GrantToken(
            client=client,
            user=user,
            code=code['code'],
            scopes=request.scopes,
            redirect_uri=request.redirect_uri,
        )
        s.add(grant)
        s.commit()
        return grant

    def _tokengetter(self, access_token=None, refresh_token=None):
        """

        :param access_token:
        :param refresh_token:
        :return:
        :rtype: midauth.models.auth.BearerToken

        """
        s = self.get_session()
        query = s.query(BearerToken)
        if access_token:
            return query.filter_by(access_token=access_token).one()
        elif refresh_token:
            return query.filter_by(refresh_token=refresh_token).one()
        return None

    def _tokensetter(self, token, request, *args, **kwargs):
        s = self.get_session()
        query = s.query(BearerToken)
        # clear old tokens
        query.filter_by(client=request.client, user=request.user).delete()

        client = s.merge(request.client)
        user = s.merge(request.user)
        scopes = token['scope'].split(' ')
        token = BearerToken(
            client=client,
            user=user,
            scopes=scopes,
            access_token=token['access_token'],
            expires_in=token['expires_in'],
            refresh_token=token['refresh_token'],
        )
        s.add(token)
        s.commit()
        return token
