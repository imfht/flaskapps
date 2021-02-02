#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
config.py
scaffold create_config
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-05-01'
from textwrap import dedent
from inflector import Inflector


class Config(object):
    """ Config Scaffold
    """

    def __init__(self, db=None, redis=None):
        self.db = db
        self.redis = redis

    def create_config(self, name='config', env='test'):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-

        class {name}(object):
            ENV = '{env}'
            {db}
            {redis}
        """.format(
            name=Inflector().camelize(name),
            env=env,
            db=self.create_sqlalchemy(),
            redis=self.create_redis(),
        )
        return dedent(source_code).strip()

    def create_sqlalchemy(self):
        source_code = ''
        if self.db == 'sqlalchemy':
            source_code = """
            SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@db:3306/app_development?charset=utf8mb4'
            SQLALCHEMY_TRACK_MODIFICATIONS = True
            """
        if self.db == 'mongoengine':
            source_code = """
            MONGODB_HOST = 'app_development'
            MONGODB_PORT = 27017
            MONGODB_DB = 'root'
            """
        return source_code

    def create_redis(self):
        if self.redis == 'redis':
            return "REDIS_URL = 'redis://:@redis:6379/0'"
