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


.. http:get:: /groups/(group_name)

   그룹의 정보와 그룹에 속한 사용자의 목록을 불러옵니다.

   :statuscode 200: 정상 요청

       ====== ===
       키     값
       ====== ===
       id     unique, 변경 불가
       uid    URI에 쓸 수 있는 형태의 그룹 이름. unique, 변경 가능
       name   그룹 이름, 변경 가능
       users  그룹에 소속된 사용자의 URI 목록
       ====== ===

   :statuscode 404: 해당 이름의 그룹이 없음
