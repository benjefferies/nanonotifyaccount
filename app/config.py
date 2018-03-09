import os

RECAPTCHA_SECRET=os.getenv('RECAPTCHA_SECRET')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
BCRYPT_SECRET = os.getenv('BCRYPT_SECRET', 'secret')
NANO_HOST = os.getenv('NANO_HOST', '[::1]')
