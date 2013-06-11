# -*- coding: utf-8 -*-
import re
from text_unidecode import unidecode

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:;]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug

    :param text: text to be translated into a slug
    :type text: unicode
    :param delim: delimiter that replace any punctuations and whitespaces
    :type delim: unicode
    :returns: an URL-safe, ASCII-only slug
    :rtype: unicode

    .. seealso:: http://flask.pocoo.org/snippets/5/

    """
    if not isinstance(text, unicode):
        raise TypeError('text should be an unicode, not {0}'.format(text))
    text = text.lower()
    result = (w for word in _punct_re.split(text)
                for w in unidecode(word).split())
    return unicode(delim.join(result))


def underscored(text):
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
