#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
extension.py
scaffold create_extension
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-04-30'
from textwrap import dedent


class Extension(object):
    """ Extension Scaffold
    """

    def __init__(self, db=None, redis=None):
        self.db = db
        self.redis = redis

    def create_extensions(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        {}

        {}
        """.format(
            self.create_header(),
            self.create_instance(),
        )
        return dedent(source_code).strip()

    def create_header(self):
        import_db = ''
        import_redis = ''
        if self.db == 'sqlalchemy':
            import_db = 'from flask_sqlalchemy import SQLAlchemy'
        if self.db == 'mongoengine':
            import_db = 'from flask_mongoengine import MongoEngine'
        if self.redis == 'redis':
            import_redis = 'from flask_redis import FlaskRedis'
        header = """
        {}
        {}
        """.format(import_db, import_redis)
        return header.strip()

    def create_instance(self):
        instance_db = ''
        instance_redis = ''
        if self.db == 'sqlalchemy':
            instance_db = 'db = SQLAlchemy()'
        if self.db == 'mongoeingine':
            instance_db = 'db = MongoEngine()'
        if self.redis:
            instance_redis = 'redis = FlaskRedis()'
        instance = """
        {}
        {}
        """.format(instance_db, instance_redis)
        return instance.strip()
