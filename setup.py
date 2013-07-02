#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
import os.path
import warnings
from midauth import VERSION

requirements = [
    'SQLAlchemy >= 0.8',
    'Flask >= 0.9',
    'Flask-Script >= 0.5',
    'Flask-Login',
    'libsass > 0.2.4',
    'FormEncode > 1.2',
    'FormEncode-Jinja2 >= 0.1.2',
    'psycopg2cffi',
    'python-dateutil > 2',
    'oauthlib',
    'Flask-OAuthlib >= 0.2',
    'requests',
    'requests-oauthlib',
    'singledispatch',
    'flufl.enum',
    'text-unidecode',
]

extras_require = {
    'doc': [
        'Sphinx',
        'sphinxcontrib-httpdomain',
    ],
    'debug': [
        'wdb',
    ],
}

dependency_links = [
    'git+git://github.com/dahlia/libsass-python.git#egg=libsass-0.2.5.dev1',
]

classifiers = [
    'Development Status :: 1 - Planning',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Natural Language :: Korean',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 2 :: Only',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    'Topic :: Office/Business :: Groupware',
]


def readme():
    try:
        root = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(root, 'README.rst')) as f:
            return f.read()
    except IOError:
        warnings.warn("Couldn't found README.rst", RuntimeWarning)
        return ''


setup(
    name='midauth',
    version=VERSION,
    author='SMARTSTUDY',
    author_email='dev@smartstudy.co.kr',
    maintainer='SMARTSTUDY',
    maintainer_email='dev@smartstudy.co.kr',
    url='http://smartstudy.co.kr/',
    license='MIT License',
    platforms='POSIX',
    description='Authentication adaptor for in-house account management.',
    long_description=readme(),
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    extras_require=extras_require,
    tests_require=[
        'pytest',
    ],
    dependency_links=dependency_links,
    classifiers=classifiers,
)
