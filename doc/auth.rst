인증 서비스
===========

개요
----

.. image:: _images/introduce-auth-service.svg
   :width: 80%
   :alt: 개략적인 인증 서비스 구조


API
---

.. http:get:: /users/(user_name)

   사용자 정보를 불러옵니다.

   :param user_name: 사용자의 username

   :statuscode 200: 정상 요청

      .. code-block:: http

         HTTP/1.1 200 OK
         Vary: Accept
         Content-Type: application/json

         {
           "username": "kroisse",
           "name": "유은총",
           "nickname": "가제트",
           "groups": [
             "/groups/devops",
             "/groups/developers",
             "/groups/task-force",
           ]
         }

   :statuscode 404: 해당 이름의 사용자가 없음

      .. code-block:: http

         HTTP/1.1 404 Not Found
         Vary: Accept
         Content-Type: application/json

         null


.. http:get:: /groups/(group_name)

   그룹의 정보와 그룹에 속한 사용자의 목록을 불러옵니다.

   :statuscode 200: 정상 요청
   :statuscode 404: 해당 이름의 그룹이 없음
