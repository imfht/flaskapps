import unittest
from flask_cas.cas_urls import create_url
from flask_cas.cas_urls import create_cas_login_url
from flask_cas.cas_urls import create_cas_logout_url
from flask_cas.cas_urls import create_cas_validate_url


class test_create_url(unittest.TestCase):

    def test_base(self):
        self.assertEqual(
            create_url('http://example.com'),
            'http://example.com',
        )

    def test_base_and_path(self):
        self.assertEqual(
            create_url(
                'http://example.com',
                'path',
            ),
            'http://example.com/path',
        )
        self.assertEqual(
            create_url(
                'http://example.com',
                '/path',
            ),
            'http://example.com/path',
        )
        self.assertEqual(
            create_url(
                'http://example.com/',
                'path',
            ),
            'http://example.com/path',
        )
        self.assertEqual(
            create_url(
                'http://example.com/',
                '/path',
            ),
            'http://example.com/path',
        )

    def test_options_with_path(self):
        self.assertEqual(
            create_url(
                'http://example.com',
                'path',
                ('key', 'value'),
            ),
            'http://example.com/path?key=value',
        )
        self.assertEqual(
            create_url(
                'http://example.com/',
                'path/',
                ('key', 'value'),
            ),
            'http://example.com/path/?key=value',
        )

    def test_options_with_out_path(self):
        self.assertEqual(
            create_url(
                'http://example.com',
                None,
                ('key', 'value'),
            ),
            'http://example.com?key=value',
        )
        self.assertEqual(
            create_url(
                'http://example.com/',
                None,
                ('key', 'value'),
            ),
            'http://example.com/?key=value',
        )

    def test_options_with_none_value(self):
        self.assertEqual(
            create_url(
                'http://example.com',
                None,
                ('key', None),
            ),
            'http://example.com',
        )
        self.assertEqual(
            create_url(
                'http://example.com/',
                None,
                ('key1', 'value'),
                ('key2', None),
            ),
            'http://example.com/?key1=value',
        )

    def test_options_which_need_escaping(self):
        self.assertEqual(
            create_url(
                'http://localhost:5000',
                None,
                ('url', 'http://example.com'),
            ),
            'http://localhost:5000?url=http%3A%2F%2Fexample.com',
        )


class test_create_cas_login_url(unittest.TestCase):

    def test_minimal(self):
        self.assertEqual(
            create_cas_login_url(
                'http://sso.pdx.edu',
                '/cas',
                'http://localhost:5000',
            ),
            'http://sso.pdx.edu/cas?service=http%3A%2F%2Flocalhost%3A5000',
        )

    def test_with_renew(self):
        self.assertEqual(
            create_cas_login_url(
                'http://sso.pdx.edu',
                '/cas',
                'http://localhost:5000',
                renew="true",
            ),
            'http://sso.pdx.edu/cas?service=http%3A%2F%2Flocalhost%3A5000&renew=true',
        )

    def test_with_gateway(self):
        self.assertEqual(
            create_cas_login_url(
                'http://sso.pdx.edu',
                '/cas',
                'http://localhost:5000',
                gateway="true",
            ),
            'http://sso.pdx.edu/cas?service=http%3A%2F%2Flocalhost%3A5000&gateway=true',
        )

    def test_with_renew_and_gateway(self):
        self.assertEqual(
            create_cas_login_url(
                'http://sso.pdx.edu',
                '/cas',
                'http://localhost:5000',
                renew="true",
                gateway="true",
            ),
            'http://sso.pdx.edu/cas?service=http%3A%2F%2Flocalhost%3A5000&renew=true&gateway=true',
        )


class test_create_cas_logout_url(unittest.TestCase):

    def test_minimal(self):
        self.assertEqual(
            create_cas_logout_url(
                'http://sso.pdx.edu',
                '/cas/logout'
            ),
            'http://sso.pdx.edu/cas/logout',
        )

    def test_with_url(self):
        self.assertEqual(
            create_cas_logout_url(
                'http://sso.pdx.edu',
                '/cas/logout',
                'http://localhost:5000',
            ),
            'http://sso.pdx.edu/cas/logout?service=http%3A%2F%2Flocalhost%3A5000'
        )


class test_create_cas_validate_url(unittest.TestCase):

    def test_minimal(self):
        self.assertEqual(
            create_cas_validate_url(
                'http://sso.pdx.edu',
                '/cas/serviceValidate',
                'http://localhost:5000/login',
                'ST-58274-x839euFek492ou832Eena7ee-cas'
            ),
            'http://sso.pdx.edu/cas/serviceValidate?service=http%3A%2F%2Flocalhost%3A5000%2Flogin&ticket=ST-58274-x839euFek492ou832Eena7ee-cas'
        )

    def test_with_renew(self):
        self.assertEqual(
            create_cas_validate_url(
                'http://sso.pdx.edu',
                '/cas/serviceValidate',
                'http://localhost:5000/login',
                'ST-58274-x839euFek492ou832Eena7ee-cas',
                renew='true',
            ),
            'http://sso.pdx.edu/cas/serviceValidate?service=http%3A%2F%2Flocalhost%3A5000%2Flogin&ticket=ST-58274-x839euFek492ou832Eena7ee-cas&renew=true'
        )
