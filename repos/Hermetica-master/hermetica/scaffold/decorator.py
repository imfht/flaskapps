#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
decorator.py
scaffold decorator
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-05-24'
from textwrap import dedent
from inflector import Inflector


class Decorator(object):
    """ Decorator Scaffold
    """

    def __init__(self, name=None):
        self.name = name

    def create_decorators(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from functools import wraps

        def {name}(func):
            @wraps(func)
            def wrapper(*ar, **kw):
                # something hear
                return func(*ar, **kw)
            return wrapper
        """.format(
            name=Inflector().underscore(self.name)
        )
        return dedent(source_code).strip()

    def create_decorator(self):
        source_code = """

        def {name}(func):
            @wraps(func)
            def wrapper(*ar, **kw):
                # something hear
                return func(*ar, **kw)
            return wrapper
        """.format(
            name=Inflector().underscore(self.name)
        )
        return dedent(source_code)
