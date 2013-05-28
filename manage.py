#!/usr/bin/env python
import os.path
from flask.ext import script
import midauth.web.application


def create_app(config=None):
    if config is not None:
        config = os.path.abspath(config)
    return midauth.web.application.create_app(config)


manager = script.Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=True)


@manager.command
def initdb():
    import midauth.models
    s = midauth.web.application.get_session()
    engine = s.bind
    midauth.models.Base.metadata.create_all(engine)


if __name__ == '__main__':
    manager.run()
