설치하기
========


코드 받기
---------

.. code-block:: console

   $ git clone https://github.com/smartstudy/midauth.git
   $ cd midauth
   midauth$


PostgreSQL 설치
---------------

현재 midauth는 `PostgreSQL`_\ 만 지원하며, 아직 다른 DB를 지원할
계획은 없습니다.

.. _PostgreSQL: http://www.postgresql.org/

Mac OS X
~~~~~~~~

가장 쉬운 방법은 `Postgres.app`_\ 을 설치하는 것입니다.

.. _Postgres.app: http://postgresapp.com/

다른 플랫폼
~~~~~~~~~~~

http://www.postgresql.org/download/\ 를 참조하세요.


DB 초기화
---------

.. code-block:: console

   midauth$ python manage.py initdb -c midauth.cfg


개발 서버 실행
--------------

.. code-block:: console

   midauth$ python manage.py runserver -c midauth.cfg
