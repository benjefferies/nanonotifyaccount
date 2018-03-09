import json
import unittest

import requests_mock
from requests import ConnectTimeout

from app.database import init_db, db_session
from app.models import Subscription
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

    def test_get_subscriptions_with_webhook(self):
        # Given
        data = {
            'email': 'test_get_subscriptions_with_webhook@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)
        resp = self.app.post('/settings', data={'webhook': 'http://mywebhook.com'})

        # When
        self.app.post('/subscribe', data={'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44oh',
                                            'action': 'subscribe'})

        # Then
        subscription = db_session.query(Subscription).filter(Subscription.email == data['email']).first()
        assert 'http://mywebhook.com' == subscription.webhook

    def test_get_subscriptions_after_subscribing(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        self.app.post('/subscribe', data={'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44oh',
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

    def test_mobile_subscribe_to_invalid_format_account(self):
        # Given
        account = {'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6z_my_account'}

        # When
        resp = self.app.post('/mobile/subscribe', content_type='application/json', data=json.dumps(account))

        # Then
        assert 400 == resp.status_code

    def test_mobile_subscribe_to_account(self):
        # Given
        account = {'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44op'}

        # When
        resp = self.app.post('/mobile/subscribe', content_type='application/json', data=json.dumps(account))

        # Then
        assert 201 == resp.status_code

    def test_mobile_double_subscribe_to_account(self):
        # Given
        account = {'account': 'xrb_1niabkx3gbxit5j5yyqcpas71dkffggbr6zpd3heui8rpoocm5xqbdwq44oh'}
        self.app.post('/mobile/subscribe', content_type='application/json', data=json.dumps(account))

        # When
        resp = self.app.post('/mobile/subscribe', content_type='application/json', data=json.dumps(account))

        # Then
        assert 409 == resp.status_code

    def test_get_settings_page(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        resp = self.app.get('/settings')

        # Then
        assert 200 == resp.status_code
        assert b'Add' in resp.data

    def test_save_webhook_on_settings_page(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        resp = self.app.post('/settings', data={'webhook': 'http://mywebhook.com'})

        # Then
        assert b'http://mywebhook.com' in resp.data

    def test_settings_after_save_webhook(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)
        resp = self.app.post('/settings', data={'webhook': 'http://mywebhook.com'})

        # When
        resp = self.app.get('/settings')

        # Then
        assert b'http://mywebhook.com' in resp.data

    def test_save_invalid_webhook_on_settings_page(self):
        # Given
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        self.app.post('/register', data=data)
        self.app.post('/', data=data)

        # When
        resp = self.app.post('/settings', data={'webhook': 'htt://mywebhook.com'})

        # Then
        assert b'Webhook is invalid' in resp.data

    @requests_mock.mock()
    def test_get_transaction_history(self, mock_request):
        # Given
        data = {
            "history": [
                {
                    "type": "receive",
                    "account": "xrb_3txm99yb6yq1t56iznzthbmjy9wntg61itxusqkhiixh4fz38i7rhsmyjt7a",
                    "amount": "120568492000000000000000000000",
                    "hash": "89F14F380D84746B014323E78985FC1750D64C1345A9870AC4F749250AA6C82D"
                }
            ]
        }
        mock_request.post('http://[::1]:7076', text=json.dumps(data))

        # When
        resp = self.app.get('/transactions/xrb_3txm99yb6yq1t56iznzthbmjy9wntg61itxusqkhiixh4fz38i7rhsmyjt7a')

        # Then
        assert 200 == resp.status_code
        history = json.loads(resp.data)
        assert history[0]['type'] == "receive"
        assert history[0]['account'] == "xrb_3txm99yb6yq1t56iznzthbmjy9wntg61itxusqkhiixh4fz38i7rhsmyjt7a"
        assert history[0]['amount'] == "120568492000000000000000000000"
        assert history[0]['hash'] == "89F14F380D84746B014323E78985FC1750D64C1345A9870AC4F749250AA6C82D"

    @requests_mock.mock()
    def test_get_transaction_history_raises_exception(self, mock_request):
        # Given
        mock_request.post('http://[::1]:7076', exc=ConnectTimeout)

        # When
        resp = self.app.get('/transactions/xrb_3txm99yb6yq1t56iznzthbmjy9wntg61itxusqkhiixh4fz38i7rhsmyjt7a')

        # Then
        assert 500 == resp.status_code

    @requests_mock.mock()
    def test_get_transaction_history_invalid_account(self, mock_request):
        # Given
        account = "nano_account"
        # When
        resp = self.app.get(f'/transactions/{account}')

        # Then
        assert 400 == resp.status_code
