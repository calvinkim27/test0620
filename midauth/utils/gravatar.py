import urllib
import hashlib


gravatar_url = u'http://www.gravatar.com/avatar/{0}?{1}'


def gravatar_id(email):
    if not isinstance(email, basestring):
        raise TypeError('email should be a basestring, not {0!r}'
                        .format(email))
    return hashlib.md5(email.lower()).hexdigest()


def image_url(email, size=44, default=u'identicon'):
    hashed = gravatar_id(email)
    params = urllib.urlencode({u'd': default, u's': size})
    return gravatar_url.format(hashed, params)
