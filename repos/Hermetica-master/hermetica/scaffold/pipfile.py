#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
pipfile.py
scaffold pipfile
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-05-09'
from os import system
from textwrap import dedent


class Pipfile(object):
    """ Pipfile Scaffold
    """

    def __init__(self, db=None, redis=None):
        self.db = db
        self.redis = redis

    def lock(self):
        system('pipenv lock')

    def create_pipfile(self):
        source_code = """
        [[source]]

        url = "https://pypi.python.org/simple"
        verify_ssl = true
        name = "pypi"

        [dev-packages]
        {nose}

        [packages]
        {flask}
        {db}
        {redis}

        [requires]

        python_version = "3.6"
        """.format(
            flask=self.create_flask(),
            nose=self.create_nose(),
            db=self.create_db(),
            redis=self.create_redis()
        )
        return dedent(source_code).strip()

    def create_flask(self):
        source_code = """
        flask = "*"
        flask-restful = "*"
        gunicorn = "*"
        """
        return source_code.strip()

    def create_nose(self):
        source_code = """
        nose = "*"
        coverage = "*"
        rednose = "*"
        nose-timer = "*"
        factory-boy = "*"
        """
        return source_code.strip()

    def create_db(self):
        source_code = ''
        if self.db == 'sqlalchemy':
            source_code = """
        pymysql = "*"
        flask-sqlalchemy = "*"
        flask-migrate = "*"
            """
        if self.db == 'mongoengine':
            source_code = """
        pymongo = "*"
        mongoengine = "*"
            """
        return source_code.strip()

    def create_redis(self):
        source_code = ''
        if self.redis == 'redis':
            source_code = """
        redis = "*"
        flask-redis = "*"
            """
        return source_code.strip()
