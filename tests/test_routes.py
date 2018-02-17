import unittest

from app.database import init_db
from run import app


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            init_db()

    def test_get_home(self):
        # When
        resp = self.app.get('/')

        # Then
        assert b'Sign Up' in resp.data
        assert b'Login' in resp.data

    def test_get_register(self):
        # When
        resp = self.app.get('/register')

        # Then
        assert b'Register' in resp.data
        assert b'Back' in resp.data

    def test_register_account(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }

        # When
        resp = self.app.post('/register', data=data)

        # Then
        assert 302 == resp.status_code
        assert 'http://localhost/' == resp.location

    def test_register_invalid_email(self):
        # Given
        data = {
            'email': '@example.com',
            'password': 'password'
        }

        # When
        resp = self.app.post('/register', data=data)

        # Then
        assert b'Enter a valid email and password' in resp.data

    def test_register_no_password(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': ''
        }

        # When
        resp = self.app.post('/register', data=data)

        # Then
        assert b'Enter a valid email and password' in resp.data

    def test_register_short_password(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'abc'
        }

        # When
        resp = self.app.post('/register', data=data)

        # Then
        assert b'Password must be more than 8 characters' in resp.data

    def test_login(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)

        # When
        resp = self.app.post('/', data=data)

        # Then
        assert 'http://localhost/subscribe' == resp.location

    def test_login_mixed_case_email(self):
        # Given
        data = {
            'email': 'TEST@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)

        # When
        resp = self.app.post('/', data=data)

        # Then
        assert 'http://localhost/subscribe' == resp.location

    def test_login_wrong_password(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)

        # When
        data['password'] = 'abc'
        resp = self.app.post('/', data=data)

        # Then
        assert b'Invalid email or password' in resp.data

    def test_login_wrong_email(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)

        # When
        data['email'] = 'test1@example.com'
        resp = self.app.post('/', data=data)

        # Then
        assert b'Invalid email or password' in resp.data

    def test_get_subscriptions_first_time(self):
        # Given
        data = {
            'email': 'test_get_subscriptions_first_time@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        resp = self.app.get('/subscribe')

        # Then
        assert b'Welcome to Nanotify!' in resp.data

    def test_get_subscriptions_after_subscribing(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        resp = self.app.post('/subscribe', data={'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44oh',
                                            'action': 'subscribe'})

        # Then
        assert b'Welcome to Nanotify!' not in self.app.get('/subscribe').data

    def test_get_subscription_to_account(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)
        self.app.post('/subscribe', data={'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44oh',
                                            'action': 'subscribe'})

        # When
        self.app.get('/subscribe')

        # Then
        assert b'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44oh' in self.app.get('/subscribe').data

    def test_subscribe_to_invalid_format_account(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        resp = self.app.post('/subscribe', data={'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6z_my_account',
                                            'action': 'subscribe'})

        # Then
        assert b'Add an account in the correct format' in resp.data