import unittest
import flask
from flask_cas import CAS


class test_flask_cas(unittest.TestCase):

    def test_cas_constructor(self):
        self.app = flask.Flask(__name__)
        CAS(self.app)

        self.app.secret_key = "SECRET_KEY"
        self.app.testing = True

        self.app.config['CAS_SERVER'] = 'http://cas.server.com'
        self.app.config['CAS_AFTER_LOGIN'] = 'root'

        with self.app.test_client() as client:
            response = client.get('/login/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas?service=http%3A%2F%2Flocalhost%2Flogin%2F')

    def test_cas_constructor_with_url_prefix(self):
        self.app = flask.Flask(__name__)
        CAS(self.app, '/cas')

        self.app.secret_key = "SECRET_KEY"
        self.app.testing = True

        self.app.config['CAS_SERVER'] = 'http://cas.server.com'
        self.app.config['CAS_AFTER_LOGIN'] = 'root'

        with self.app.test_client() as client:
            response = client.get('/cas/login/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas?service=http%3A%2F%2Flocalhost%2Fcas%2Flogin%2F')

    def test_cas_constructor_properties(self):
        
        self.app = flask.Flask(__name__)
        cas = CAS(self.app)

        with self.app.test_request_context():
            self.assertEqual(
                cas.username,
                None)

            self.assertEqual(
                cas.token,
                None)

    def test_cas_init_app(self):
        self.app = flask.Flask(__name__)
        cas = CAS()
        cas.init_app(self.app)

        self.app.secret_key = "SECRET_KEY"
        self.app.testing = True

        self.app.config['CAS_SERVER'] = 'http://cas.server.com'
        self.app.config['CAS_AFTER_LOGIN'] = 'root'

        with self.app.test_client() as client:
            response = client.get('/login/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas?service=http%3A%2F%2Flocalhost%2Flogin%2F')

    def test_cas_init_app_with_prefix_url(self):
        self.app = flask.Flask(__name__)
        cas = CAS()
        cas.init_app(self.app, '/cas')

        self.app.secret_key = "SECRET_KEY"
        self.app.testing = True

        self.app.config['CAS_SERVER'] = 'http://cas.server.com'
        self.app.config['CAS_AFTER_LOGIN'] = 'root'

        with self.app.test_client() as client:
            response = client.get('/cas/login/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas?service=http%3A%2F%2Flocalhost%2Fcas%2Flogin%2F')
    
    def test_cas_init_app_properties(self):
        
        self.app = flask.Flask(__name__)
        cas = CAS()

        cas.init_app(self.app)

        with self.app.test_request_context():
            self.assertEqual(
                cas.username,
                None)

            self.assertEqual(
                cas.token,
                None)
