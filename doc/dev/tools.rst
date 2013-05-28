개발 도구
=========


.. _using-flake8:

Flake8
------

`flake8`_\ 을 사용하면 작성한 코드가 :pep:`8`\ 을 따르고 있는지 쉽게 체크할 수
있습니다. 덤으로 `pyflakes`_\ 가 제공하는 정적 분석 기능도 함께 제공하니
설치하신 뒤 편집기에 연동하는 것을 추천합니다.

.. _flake8: http://flake8.readthedocs.org/
.. _pyflakes: https://pypi.python.org/pypi/pyflakes


명령행
~~~~~~

.. code-block:: console

   $ pip install flake8
   $ flake8 midauth/
   midauth/models/user.py:11:13: W291 trailing whitespace
   midauth/utils/conf.py:22:80: E501 line too long (101 > 79 characters)
   ......

만약 virtualenv를 사용하고 계시다면, 편집기에 연동하기 쉽도록 virtualenv 바깥에
:program:`flake8`\ 을 설치하는 것을 추천합니다.


Emacs
~~~~~

먼저 :program:`flake8`\ 이 실행 가능한 위치에 설치되어 있어야 합니다.
:file:`~/.emacs` 파일에 다음 코드를 추가합니다.

.. code-block:: scheme

   (when (load "flymake" t)
     (defun flymake-pyflakes-init ()
        ; Make sure it's not a remote buffer or flymake would not work
        (when (not (subsetp (list (current-buffer)) (tramp-list-remote-buffers)))
         (let* ((temp-file (flymake-init-create-temp-buffer-copy
                            'flymake-create-temp-inplace))
                (local-file (file-relative-name
                             temp-file
                             (file-name-directory buffer-file-name))))
           (list "flake8" (list local-file)))))
     (add-to-list 'flymake-allowed-file-name-masks
                  '("\\.py\\'" flymake-pyflakes-init)))

.. seealso:: `Using flymake with pyflakes <http://emacswiki.org/emacs/PythonProgrammingInEmacs#toc14>`_
