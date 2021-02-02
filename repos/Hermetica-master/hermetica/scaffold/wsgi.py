#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
wsgi.py
scaffold create_wsgi
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-05-01'
from textwrap import dedent


class WSGI(object):
    """ wsgi Scaffold
    """

    def __init__(self, db):
        self.db = db

    def create_wsgi(self):
        source_code = """
        #! /usr/bin/env python3
        # -*- encoding: utf-8 -*-
        import os
        {header}

        app = create_app(os.getenv('FLASK_ENV', None))
        {migrate}

        if __name__ == '__main__':
            app.run(host='0.0.0.0')
        """.format(
            header=self.create_header(),
            migrate=self.create_migrate()
        )

        return dedent(source_code).strip()

    def create_header(self):
        if self.db == 'sqlalchemy':
            return 'from app import create_app, db'
        return 'from app import create_app'

    def create_migrate(self):
        if self.db == 'sqlalchemy':
            return 'migrate = Migrate(app, db)'
        return ''
