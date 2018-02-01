import uuid

from sqlalchemy import Column, String, Binary, types

from app.database import Base


class UUID(types.TypeDecorator):
    impl = Binary


class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(String, primary_key=True, default=uuid.uuid4)
    email = Column(String)
    account = Column(String, nullable=False)

    def __init__(self, email, account):
        self.id = str(uuid.uuid4())
        self.email = email
        self.account = account


class User(Base):
    __tablename__ = 'user'
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email

    def __repr__(self):
        return '<User %r>' % self.email
