# -*- coding: utf-8 -*-
import uuid
from flask.ext.login import current_user
from flask.ext.oauthlib.provider import OAuth2Provider as BaseProvider

from midauth.models.auth import Client, GrantToken, BearerToken


class OAuth2Provider(BaseProvider):
    def get_session(self):
        from .application import get_session
        return get_session()

    def _clientgetter(self, client_id):
        """

        :param client_id:
        :return:
        :rtype: midauth.models.auth.Client

        """
        client_id = uuid.UUID(client_id)
        s = self.get_session()
        client = s.query(Client).get(client_id)
        return client

    def _grantgetter(self, client_id, code):
        client_id = uuid.UUID(client_id)
        s = self.get_session()
        g = s.query(GrantToken).filter_by(client_id=client_id, code=code).one()
        return g

    def _grantsetter(self, client_id, code, request, *args, **kwargs):
        client = self._clientgetter(client_id)
        user = current_user._get_current_object()
        assert client is request.client
        assert user is request.user
        grant = GrantToken(
            client=client,
            user=user,
            code=code['code'],
            scopes=request.scopes,
            redirect_uri=request.redirect_uri,
        )
        s = self.get_session()
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
        old_tokens = query.filter_by(client=request.client, user=request.user)
        s.delete(old_tokens)
        token = BearerToken(
            client=request.client,
            user=request.user,
            **token
        )
        s.add(token)
        s.commit()
        return token
