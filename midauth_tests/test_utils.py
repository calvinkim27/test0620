from __future__ import absolute_import
import pytest

import types
import urllib2

from midauth.utils import gravatar
from midauth.utils import importlib
from midauth.utils import conf


def test_gravatar_image_url():
    url = gravatar.image_url('kroisse@gmail.com')
    assert url.startswith('http://www.gravatar.com')
    response = urllib2.urlopen(url)
    assert response.getcode() < 400
    mime = response.info()
    assert mime.getmaintype() == 'image'


def test_import_module_by_string():
    with pytest.raises(ImportError):
        importlib.import_string('not_existing')
    m = importlib.import_string('.mod', 'midauth_tests')
    assert isinstance(m, types.ModuleType)
    assert m.__name__ == 'midauth_tests.mod'


def test_import_object_by_string():
    answer = importlib.import_string('midauth_tests.mod:answer')
    assert answer == 42
    widget = importlib.import_string('.mod:Widget', 'midauth_tests')
    assert isinstance(widget, type)
    assert widget.__module__ == 'midauth_tests.mod'


def test_import_default():
    m = importlib.import_string('not_existing', default=None)
    assert m is None


def test_conf():
    config = conf.generate_settings()
    namespace = {}
    exec str(config) in namespace
    assert 'SECRET_KEY' in namespace
    assert 'DATABASE_URL' in namespace
