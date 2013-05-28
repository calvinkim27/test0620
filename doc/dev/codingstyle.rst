코딩 스타일
===========

인코딩
------

* 모든 소스 코드의 인코딩은 `UTF-8`_\ 이어야 합니다.

.. _UTF-8: http://ko.wikipedia.org/wiki/UTF-8


Python
------

* 기본적으로 모든 파이썬 코드에서 :pep:`8`\ 을 따릅니다.

  .. seealso:: :ref:`Flake8로 파이썬 코드 쉽게 체크하기 <using-flake8>`

* ASCII 문자 이외의 문자가 파이썬 소스 파일에 포함된다면, 그 문자는 UTF-8이어야만 하며,
  해당 소스 파일의 제일 위에 ``# -*- coding: utf-8 -*-``\ 과 같이 인코딩을 명시해야만
  합니다. 소스 파일이 ASCII 문자로만 이루어져 있을 경우 이 주석은 생략 가능합니다.
* 가능하면 한글 등 ASCII 이외의 문자는 문서화 주석이나 한줄 주석에만 쓰여야 합니다.
* 일반적인 문자를 다루는 모든 코드는 문자열을 :obj:`unicode`\ 로 취급해야 합니다.
  절대로 :obj:`unicode`\ 와 :obj:`str`\ 을 혼용하는 코드를 작성해선 안 됩니다.

  .. seealso:: `Tips for Writing Unicode-aware Programs`__ in `Python Unicode HOWTO`_

     __ http://docs.python.org/2/howto/unicode.html#tips-for-writing-unicode-aware-programs
     .. _Python Unicode HOWTO: http://docs.python.org/2/howto/unicode.html


CSS
---

* 들여쓰기는 빈칸 4개로 합니다. 하드 탭은 쓰지 않습니다.

* 속성은 한 줄에 하나씩 쓰는 것을 원칙으로 합니다.

  .. code-block:: css

     /* YES: */
     section {
         width: 90%;
         max-width: 960px;
         padding: 15px 10px;
         margin: 0 auto;
         background-color: white;
     }
     /* NO: */
     section { width: 90%; max-width: 960px; padding: 15px 10px; margin: 0 auto; background-color: white; }

  * 단, 속성이 2개 이내인 규칙(rule)은 한 줄에 쓸 수 있습니다.

    .. code-block:: css

       a:visited { color: #808; text-decoration: underline; }

* 콜론(``:``) 뒤에는 항상 빈칸을 하나 넣습니다.

  .. code-block:: css

     /* YES: */ color: #abc;
     /* NO:  */ color:#abc;

* 여는 중괄호(``{``) 앞에 빈칸을 하나 넣습니다.

  .. code-block:: css

     /* YES: */ body {
     /* NO:  */ body{

* 한 줄에 쓸 경우, 중괄호(``{``, ``}``) 안쪽에 빈칸을 하나씩 넣습니다.

  .. code-block:: css

     /* YES: */ body { color: #333; }
     /* NO:  */ body {color: #333;}

* 마지막 속성의 세미콜론(``;``)은 생략하지 않습니다.

  .. code-block:: css

     /* YES: */ color: #333; }
     /* NO:  */ color: #333 }


JavaScript
----------

* 들여쓰기는 빈칸 4개로 합니다. 하드 탭은 쓰지 않습니다.

* 인라인 스크립트는 특별한 목적이 없는 이상 사용해선 안 됩니다.

* 가능하다면 `Strict mode`_\ 를 사용해야 합니다.

  * 소스 파일의 가장 위, 혹은 모든 코드를 감싸는 함수의 가장 위에 아래 문장을 삽입합니다.
    
    .. code-block:: js

       "use strict";


.. _Strict mode: https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Functions_and_function_scope/Strict_mode
