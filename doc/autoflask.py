# -*- coding: utf-8 -*-
import midauth.web.application
import os.path

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'doc.cfg')
application = midauth.web.application.create_app(config=config_path)
