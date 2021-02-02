#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
api.py
scaffold create_api
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-05-01'
from textwrap import dedent
from inflector import Inflector


class API(object):
    """ API Scaffold
    """

    def __init__(self, api=None, name=None):
        self.api = api
        self.name = name

    def create__init__(self):
        if self.api == 'restful':
            return self.create_restful__init__()
        if self.api == 'decorator':
            return self.create_decorator__init__()
        if self.api == 'class':
            return self.create_method_view__init__()

    def create_api(self):
        if self.api == 'restful':
            return self.create_restful()
        if self.api == 'decorator':
            return self.create_decorator()
        if self.api == 'class':
            return self.create_method_view()

    def create_restful__init__(self):
        name=Inflector().camelize(self.name)
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from flask import Blueprint
        from flask_restful import Api
        from app.api.v1.{name} import {Name}

        api_v1 = Blueprint('api/v1', __name__)
        api = Api(api_v1)
        api.add_resource({Name}, '/{names}', '/{names}/<int:id>')
        """.format(
            name=Inflector().underscore(self.name),
            names=Inflector().pluralize(self.name),
            Name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()

    def create_restful(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from flask_restful import Resource, fields, marshal_with, reqparse

        resource_fields = {{
            'id': fields.Integer,
            'created_at': fields.DateTime,
            'updated_at': fields.DateTime,
        }}

        class {name}(Resource):

            parser = reqparse.RequestParser()
            parser.add_argument('query', type=str, help="query string")
            parser.add_argument('body', type=str, help="body string")

            @marshal_with(resource_fields)
            def get(self, id=None):
                args = self.parser.parse_args()
                if id is None:
                    return {{}}, 200
                return [], 200

            @marshal_with(resource_fields)
            def post(self):
                args = self.parser.parse_args()
                return {{}}, 201

            @marshal_with(resource_fields)
            def put(self, id=None):
                args = self.parser.parse_args()
                return {{}}, 204

            @marshal_with(resource_fields)
            def delete(self, id=None):
                return {{}}, 204
        """.format(
            name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()

    def create_method_view__init__(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from flask import Blueprint
        from app.api.v1.{name} import {Name}

        api_v1 = Blueprint('api/v1', __name__)
        api_v1.add_url_rule('/{names}', view_func={Name}.as_view('{name}'), methods=['GET', 'POST'])
        api_v1.add_url_rule('/{names}/<int:id>', view_func={Name}.as_view('{name}'), methods=['GET', 'PUT', 'DELETE'])
        """.format(
            name=Inflector().underscore(self.name),
            names=Inflector().pluralize(self.name),
            Name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()

    def create_method_view(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from flask.views import MethodView

        class {name}(MethodView):
            def get(self, id=None):
                if not id: return 'index'
                return 'show'

            def post(self):
                return 'create'

            def put(self, id):
                return 'update'

            def delete(self, id):
                return 'destroy'

        """.format(
            name=Inflector().camelize(self.name),
        )
        return dedent(source_code).strip()

    def create_decorator__init__(self):
        instance = Inflector().underscore(self.name)
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from app.api.v1.{instance} import {instance}
        """.format(
            instance=instance,
        )
        return dedent(source_code).strip()

    def create_decorator(self):
        instance = Inflector().underscore(self.name)
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from flask import Blueprint

        {instance} = Blueprint('{instances}', __name__)

        @{instance}.route('/{instances}', methods=['GET'])
        def index():
            return 'index'

        @{instance}.route('/{instances}/<int:id>', methods=['GET'])
        def show(id):
            return 'show'

        @{instance}.route('/{instances}/', methods=['POST'])
        def create():
            return 'create'

        @{instance}.route('/{instances}/<int:id>', methods=['PUT'])
        def update(id):
            return 'update'

        @{instance}.route('/{instances}/<int:id>', methods=['DELETE'])
        def destroy(id):
            return 'destroy'

        """.format(
            instance=instance,
            instances=Inflector().pluralize(instance)
        )
        return dedent(source_code).strip()
