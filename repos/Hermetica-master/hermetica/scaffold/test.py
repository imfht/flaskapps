#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
test.py
Test Scaffold
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-04-27'
from textwrap import dedent
from inflector import Inflector

class Test(object):

    def __init__(self, name=None, db=None):
        self.db =db
        self.name = name

    def create__init__(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        import json
        from contextlib import contextmanager
        from unittest import TestCase
        from app import create_app

        app = create_app()

        class Experiment(TestCase):

            def setUp(self):
                app.testing = True
                self.client = app.test_client()
                self.app_config = app.config
                self.app_context = app.app_context()
                self.app_context.push()

            def tearDown(self):
                self.app_context.pop()

            def response_to_dict(self, response):
                return json.loads(response.data)

            @contextmanager
            def authenticate(self, user=None):
                pass
        """
        return dedent(source_code).strip()

    def create_nose_cfg(self):
        source_code = """
        [nosetests]
        verbosity=2
        with-timer=1
        rednose=True
        nocapture=True
        with-coverage=1
        cover-package=.
        """
        return dedent(source_code).strip()

    def create_api_test(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from test import Experiment
        from test.factories.{name}_factory import {Name}Factory
        from app.models.{name} import {Name}

        class {Name}APITest(Experiment):

            def setUp(self):
                super().setUp()
                {Name}Factory.create_batch(5)

            def test_get_list_200(self):
                {name} = {Name}.query.first()
                url = "/api/v1/{names}"
                response = self.client.get(url, data={})
                assert response.status_code == 200

            def test_get_200(self):
                {name} = {Name}.query.first()
                url = "/api/v1/{names}/{{}}".format({name}.id)
                response = self.client.get(url, data={})
                assert response.status_code == 200

            def test_post_201(self):
                url = "/api/v1/{names}"
                response = self.client.post(url, data={})
                assert response.status_code == 201

            def test_put_204(self):
                {name} = {Name}.query.first()
                url = "/api/v1/{names}/{{}}".format({name}.id)
                response = self.client.put(url, data={})
                assert response.status_code == 204

            def test_delete_204(self):
                {name} = {Name}.query.first()
                url = "/api/v1/{names}/{{}}".format({name}.id)
                response = self.client.delete(url, data={})
                assert response.status_code == 204
        """.format(
            name=Inflector().underscore(self.name),
            names=Inflector().pluralize(self.name),
            Name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()

    def create_model_test(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from test import Experiment
        from test.factories.{name}_factory import {Name}Factory
        from app.models.{name} import {Name}

        class {Name}ModelTest(Experiment):

            def setUp(self):
                {Name}Factory.create_batch(5)

            def something(self):
                pass
        """.format(
            name=Inflector().underscore(self.name),
            Name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()

    def create_factoryboy(self):
        if self.db == 'sqlalchemy':
            return self.create_sqlalchemy_factoryboy()
        if self.db == 'mongoengine':
            return self.create_mongoengine_factoryboy()
        return ''

    def create_sqlalchemy_factoryboy(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from factory import Sequence, SubFactory, Iterator, fuzzy
        from factory.alchemy import SQLAlchemyModelFactory
        from app.extensions import db
        from app.models.{name} import {Name}

        class {Name}Factory(SQLAlchemyModelFactory):
            class Meta:
                model = {Name}
                sqlalchemy_session = db.session

            id = Sequence(lambda n: n+1)
        """.format(
            name=self.name,
            Name=Inflector().camelize(self.name),
        )
        return dedent(source_code).strip()

    def create_mongoengine_factoryboy(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from factory import Sequence, SubFactory, Iterator, fuzzy
        from factory.mongoengine import MongoEngineFactory
        from app.models.{name} import {Name}

        class {Name}Factory(MongoEngineFactory):
            class Meta:
                model = {Name}
        """.format(
            name=self.name,
            Name=Inflector().camelize(self.name),
        )
        return dedent(source_code).strip()
