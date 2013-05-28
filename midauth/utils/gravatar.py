import urllib
import hashlib


gravatar_url = u'http://www.gravatar.com/avatar/{0}?{1}'


def image_url(email, size=44, default=u'identicon'):
    if not isinstance(email, basestring):
        raise TypeError('email should be a basestring, not {0!r}'
                        .format(email))
    hashed = hashlib.md5(email.lower()).hexdigest()
    params = urllib.urlencode({u'd': default, u's': size})
    return gravatar_url.format(hashed, params)
