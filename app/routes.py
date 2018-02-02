import datetime

import bcrypt
import flask
from flask import render_template, Blueprint, url_for, request, session
from flask_login import login_required, login_user, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from app.database import db_session
from app.models import Subscription, User

nano = Blueprint('profile', __name__, template_folder='templates', static_folder='static')


@nano.teardown_app_request
def shutdown_session(exception=None):
    if not exception:
        try:
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()
            db_session.remove()
    else:
        db_session.rollback()
    db_session.remove()


@nano.before_request
def before_request():
    flask.session.permanent = True
    nano.permanent_session_lifetime = datetime.timedelta(minutes=30)
    flask.session.modified = True
    flask.g.user = current_user


@nano.route('/', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = db_session.query(User).filter(User.email == email).first()
    user.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    if user and bcrypt.checkpw(password.encode(), user.password):
        login_user(user)
        return redirect(url_for('.subscribe'))
    else:
        return render_template('index.html', error='Invalid email or password')


@nano.route('/register', methods=['POST'])
def get_register():
    email = request.form['email']
    password = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt())
    user = User(email, password)
    db_session.add(user)
    return redirect(url_for('.get_login'))


@nano.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@nano.route('/subscribe', methods=['POST'])
def subscribe():
    subscription = Subscription(email=current_user.email, account=request.form['account'])
    db_session.add(subscription)
    subscriptions = db_session.query(Subscription).filter(User.email == current_user.email).all()
    subscriptions.append(subscription)
    return render_template('subscribe.html', subscriptions=subscriptions)


@nano.route('/', methods=['GET'])
def get_login():
    return render_template('index.html')


@nano.route('/subscribe', methods=['GET'])
@login_required
def get_subscribe():
    subscriptions = db_session.query(Subscription).filter(User.email == current_user.email).all()
    return render_template('subscribe.html', subscriptions=subscriptions)
