"""
flask_cas.__init__
"""

import flask
from flask import current_app

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from . import routing

from functools import wraps

class CAS(object):
    """
    Required Configs:

    |Key             |
    |----------------|
    |CAS_SERVER      |
    |CAS_AFTER_LOGIN |

    Optional Configs:

    |Key                        | Default               |
    |---------------------------|-----------------------|
    |CAS_TOKEN_SESSION_KEY      | _CAS_TOKEN            |
    |CAS_USERNAME_SESSION_KEY   | CAS_USERNAME          |
    |CAS_ATTRIBUTES_SESSION_KEY | CAS_ATTRIBUTES        |
    |CAS_LOGIN_ROUTE            | '/cas'                |
    |CAS_LOGOUT_ROUTE           | '/cas/logout'         |
    |CAS_VALIDATE_ROUTE         | '/cas/serviceValidate'|
    |CAS_AFTER_LOGOUT           | None                  |
    """

    def __init__(self, app=None, url_prefix=None):
        self._app = app
        if app is not None:
            self.init_app(app, url_prefix)

    def init_app(self, app, url_prefix=None):
        # Configuration defaults
        app.config.setdefault('CAS_TOKEN_SESSION_KEY', '_CAS_TOKEN')
        app.config.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')
        app.config.setdefault('CAS_ATTRIBUTES_SESSION_KEY', 'CAS_ATTRIBUTES')
        app.config.setdefault('CAS_LOGIN_ROUTE', '/cas')
        app.config.setdefault('CAS_LOGOUT_ROUTE', '/cas/logout')
        app.config.setdefault('CAS_VALIDATE_ROUTE', '/cas/serviceValidate')
        # Requires CAS 2.0
        app.config.setdefault('CAS_AFTER_LOGOUT', None)
        # Register Blueprint
        app.register_blueprint(routing.blueprint, url_prefix=url_prefix)

        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        ctx = stack.top
    
    @property
    def app(self):
        return self._app or current_app

    @property
    def username(self):
        return flask.session.get(
            self.app.config['CAS_USERNAME_SESSION_KEY'], None)

    @property
    def attributes(self):
        return flask.session.get(
            self.app.config['CAS_ATTRIBUTES_SESSION_KEY'], None)

    @property
    def token(self):
        return flask.session.get(
            self.app.config['CAS_TOKEN_SESSION_KEY'], None)

def login():
    return flask.redirect(flask.url_for('cas.login', _external=True))

def logout():
    return flask.redirect(flask.url_for('cas.logout', _external=True))

def login_required(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if 'CAS_USERNAME' not in flask.session:
            flask.session['CAS_AFTER_LOGIN_SESSION_URL'] = (
                flask.request.script_root +
                flask.request.full_path
            )
            return login()
        else:
            return function(*args, **kwargs)
    return wrap
