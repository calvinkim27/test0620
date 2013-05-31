# -*- coding: utf-8 -*-
from werkzeug.urls import url_decode, url_encode


class MethodRewriteMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if '_method=' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.pop('_method', None)
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
                environ['QUERY_STRING'] = url_encode(args)
        return self.app(environ, start_response)
