# -*- coding: utf-8 -*-
from werkzeug.urls import url_decode, url_encode


class MethodRewriteMiddleware(object):
    """HTTP 메서드를 URL 쿼리 인자로 대신 받아들이는 WSGI 미들웨어

    .. seealso:: http://flask.pocoo.org/snippets/38/

    .. note::

       원래 계획은 `jquery-ujs`_\ 의 ``data-method`` 동작에 맞춰
       ``_method``\ 를 URL 쿼리 인자가 아니라 요청 본문(request body)으로
       전달하는 것이었으나, 이 경우 아래와 같은 문제가 발생합니다.

       1. :mailheader:`REQUEST_METHOD`\ 가 결정되기도 전에 요청 본문을 읽고
          파싱해야 함.
       2. URL과 달리 요청 본문은 매우 클 수 있고, 따라서 ``_method`` 값이
          전달되었는지 확인하기 위해서 스트림을 전부 훑어봐야 함.
       3. 본문 스트림은 한 번만 읽을 수 있게 되어 있으며, 이는
          ``environ['wsgi.input']``\ 도 마찬가지임. 따라서 별도의 메모리나
          디스크에 버퍼링을 해야 하며, 이 경우 DOS 공격에 매우 취약해짐.

       따라서 `jquery-ujs`_\ 의 :js:func:`$.rails.handleMethod()` 함수를
       교체해서 요청 본문 대신 URL 쿼리 인자로 ``_method`` 값을 전송하도록
       했습니다.

       .. _jquery-ujs: https://github.com/rails/jquery-ujs

    """
    def __init__(self, app, param='_method'):
        self.app = app
        self.method_param = param
        self.method_param_q = param + '='

    def __call__(self, environ, start_response):
        if self.method_param_q in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.pop(self.method_param, None)
            if method:
                method = method.upper().encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
                environ['QUERY_STRING'] = url_encode(args)
        return self.app(environ, start_response)
