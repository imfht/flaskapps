#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
app.py
scaffold create_app
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-04-27'
from textwrap import dedent


class App(object):
    """ App Scaffold
    """

    def __init__(self, api=None, db=None, redis=None):
        self.api = api
        self.db = db
        self.redis = redis

    def create_app__init__(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from flask import Flask
        {header}

        def create_app(env='development'):
            app = Flask(__name__)

            if env == 'development':
                app.config.from_object('config.development.Development')
            elif env == 'production':
                app.config.from_object('config.production.Production')
            else:
                app.config.from_object('config.development.Development')

            {extension}
            {api}

            return app
        """.format(
            header=self.create_header(),
            extension=self.create_extension(),
            api=self.create_api(),
        )
        return dedent(source_code).strip()

    def create_header(self):
        import_db = ''
        import_redis = ''
        import_api = ''
        if self.db:
            import_db = 'from app.extensions import db'
        if self.redis == 'redis':
            import_redis = 'from app.extensions import redis'
        if self.api:
            import_api = 'from app import api'

        header = """
        {}
        {}
        {}
        """.format(import_db, import_redis, import_api)
        return header.strip()

    def create_extension(self):
        create_db = ''
        create_redis = ''
        if self.db:
            create_db = 'db.init_app(app)'
        if self.redis == 'redis':
            create_redis = 'redis.init_app(app)'
        source_code = """
            {}
            {}
        """.format(create_db, create_redis)
        return source_code.strip()

    def create_api(self):
        if self.api in ('restful', 'class'):
            return "app.register_blueprint(api.api_v1, url_prefix='/api/v1')"
        else:
            # TODO register dynamic api name
            return "app.register_blueprint(api.root, url_prefix='/api/v1')"
