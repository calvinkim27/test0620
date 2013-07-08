# -*- coding: utf-8 -*-
import os.path
from flask.ext import script
import midauth.web.application
import midauth.utils.conf


def create_app(config=None):
    if config is None:
        config_path = os.environ.get('MIDAUTH_CONFIG')
        if not config_path:
            config_path = os.path.abspath('midauth.cfg')
    else:
        config_path = os.path.abspath(config)
    if not os.path.isfile(config_path):
        print "Configuration file '{0}' doesn't exist. Create it..." \
            .format(config_path)
        midauth.utils.conf.create_settings(config_path)
    return midauth.web.application.create_app(config_path)


manager = script.Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)


@manager.command
def initdb():
    import midauth.models
    s = midauth.web.application.get_session()
    engine = s.bind
    midauth.models.Base.metadata.create_all(engine)


def main():
    manager.run()
