import unittest
import flask
import io

try:
    import mock
except ImportError:
    import unittest.mock as mock

from flask_cas import routing
from flask_cas import CAS


class test_routing(unittest.TestCase):

    def setUp(self):

        self.app = flask.Flask(__name__)

        @self.app.route('/')
        def root():
            return ''

        self.app.secret_key = "SECRET_KEY"
        self.cas = CAS(self.app)
        self.app.testing = True

        self.app.config['CAS_SERVER'] = 'http://cas.server.com'
        self.app.config['CAS_TOKEN_SESSION_KEY'] = '_CAS_TOKEN'
        self.app.config['CAS_USERNAME_SESSION_KEY'] = 'CAS_USERNAME'
        self.app.config['CAS_ATTRIBUTES_SESSION_KEY'] = 'CAS_ATTRIBUTES'
        self.app.config['CAS_AFTER_LOGIN'] = 'root'
        self.app.config['CAS_LOGIN_ROUTE'] = '/cas'
        self.app.config['CAS_LOGOUT_ROUTE'] = '/cas/logout'
        self.app.config['CAS_VALIDATE_ROUTE'] = '/cas/serviceValidate'
        self.app.config['CAS_AFTER_LOGOUT'] = 'http://localhost:5000'

    def test_setUp(self):
        pass

    def test_login_by_logged_out_user(self):
        with self.app.test_client() as client:
            response = client.get('/login/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas?service=http%3A%2F%2Flocalhost%2Flogin%2F')

    @mock.patch.object(routing, 'urlopen',
                       return_value=io.BytesIO(b'\n\n'))
    @mock.patch.object(routing, 'parse',
                       return_value={
                           "cas:serviceResponse": {
                               "cas:authenticationSuccess": {
                                   "cas:user": "bob",
                                   "cas:attributes": {
                                   }
                               }
                           }
                       })
    def test_login_by_logged_in_user_valid(self, m, n):
        ticket = '12345-abcdefg-cas'
        with self.app.test_client() as client:
            with client.session_transaction() as s:
                s[self.app.config['CAS_TOKEN_SESSION_KEY']] = ticket
            client.get('/login/')
            self.assertEqual(
                self.cas.username,
                'bob')
            self.assertEqual(
                self.cas.token,
                ticket)

    @mock.patch.object(routing, 'urlopen',
                       return_value=io.BytesIO(b'\n\n'))
    @mock.patch.object(routing, 'parse',
                       return_value={
                           "cas:serviceResponse": {
                               'cas:authenticationFailure': {
                               }
                           }
                       })
    def test_login_by_logged_in_user_invalid(self, m, n):
        ticket = '12345-abcdefg-cas'
        with self.app.test_client() as client:
            with client.session_transaction() as s:
                s[self.app.config['CAS_TOKEN_SESSION_KEY']] = ticket
            client.get('/login/')
            self.assertTrue(
                self.app.config['CAS_USERNAME_SESSION_KEY'] not in flask.session)
            self.assertTrue(
                self.app.config['CAS_ATTRIBUTES_SESSION_KEY'] not in flask.session)
            self.assertTrue(
                self.app.config['CAS_TOKEN_SESSION_KEY'] not in flask.session)

    @mock.patch.object(routing, 'validate', return_value=True)
    def test_login_by_cas_valid(self, m):
        with self.app.test_client() as client:
            ticket = '12345-abcdefg-cas'
            response = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://localhost/')
            self.assertEqual(
                self.cas.token,
                ticket)

    @mock.patch.object(routing, 'validate', return_value=False)
    def test_login_by_cas_invalid(self, m):
        with self.app.test_client() as client:
            ticket = '12345-abcdefg-cas'
            response = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas?service=http%3A%2F%2Flocalhost%2Flogin%2F')

    def test_logout(self):
        with self.app.test_client() as client:
            response = client.get('/logout/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers['Location'],
                'http://cas.server.com/cas/logout?service=http%3A%2F%2Flocalhost%3A5000')

    @mock.patch.object(routing, 'urlopen',
                       return_value=io.BytesIO(b'\n\n'))
    @mock.patch.object(routing, 'parse',
                       return_value={
                           "cas:serviceResponse": {
                               "cas:authenticationSuccess": {
                                   "cas:user": "bob",
                                   "cas:attributes": {
                                   }
                               }
                           }
                       })
    def test_validate_valid(self, m, n):
        with self.app.test_request_context('/login/'):
            ticket = '12345-abcdefg-cas'
            self.assertEqual(routing.validate(ticket), True)
            self.assertEqual(
                self.cas.username,
                'bob')

    @mock.patch.object(routing, 'urlopen',
                       return_value=io.BytesIO(b'\n\n'))
    @mock.patch.object(routing, 'parse',
                       return_value={
                           "cas:serviceResponse": {
                               'cas:authenticationFailure': {
                               }
                           }
                       })
    def test_validate_invalid(self, m, n):
        with self.app.test_request_context('/login/'):
            ticket = '12345-abcdefg-cas'
            self.assertEqual(routing.validate(ticket), False)
            self.assertTrue(
                self.app.config['CAS_USERNAME_SESSION_KEY'] not in flask.session)
            self.assertTrue(
                self.app.config['CAS_ATTRIBUTES_SESSION_KEY'] not in flask.session)
            self.assertTrue(
                self.app.config['CAS_TOKEN_SESSION_KEY'] not in flask.session)
