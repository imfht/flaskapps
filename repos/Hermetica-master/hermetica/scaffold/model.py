#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
model.py
scaffold model
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-04-27'
from textwrap import dedent
from inflector import Inflector


class Model(object):
    """ Model Scaffold
    """

    def __init__(self, db=None, name=None):
        self.db = db
        self.name = name

    def create__init__(self):
        if self.db == 'sqlalchemy':
            return self.create_sqlalchemy__init__()
        if self.db == 'mongoengine':
            return self.create_mongoengine__init__()

    def create_model(self):
        if self.db == 'sqlalchemy':
            return self.create_sqlalchmey_model()
        if self.db == 'mongoengine':
            return self.create_mongoengine_model()

    def create_sqlalchemy__init__(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from datetime import datetime
        from sqlalchemy.ext.declarative import declared_attr
        from app.extensions import db


        class Model(db.Model):
            __abstract__ = True

            id = db.Column(db.Integer, primary_key=True)

            @declared_attr
            def created_at(cls):
                return db.Column(db.DateTime, default=datetime.utcnow)

            @declared_attr
            def updated_at(cls):
                return db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        """
        return dedent(source_code).strip()

    def create_sqlalchmey_model(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from app.models import Model

        class {name}(Model):
            pass
        """.format(
            name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()

    def create_mongoengine__init__(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from datetime import datetime
        from mongoengine import Document, DateTimeField

        class Model(Document):
            created_at = DateTimeField()
            updated_at = DateTimeField(default=datetime.datetime.now)

            def save(self, *args, **kwargs):
                if not self.created_at:
                    self.created_at = datetime.datetime.now()
                self.updated_at = datetime.datetime.now()
                return super(Model, self).save(*args, **kwargs)
        """
        return dedent(source_code).strip()

    def create_mongoengine__model(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        from app.models import Model

        class {name}(Model):
            pass
        """.format(
            name=Inflector().camelize(self.name)
        )
        return dedent(source_code).strip()
