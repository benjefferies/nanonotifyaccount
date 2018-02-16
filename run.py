import datetime

import os
from flask import Flask, send_from_directory, request
from flask_login import LoginManager
from werkzeug.utils import redirect

from app.config import BCRYPT_SECRET
from app.database import init_db
from app.models import User
from app.routes import nano

app = Flask(__name__)
PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=30)
app.secret_key = BCRYPT_SECRET
app.register_blueprint(nano)
app.config['TEMPLATES_AUTO_RELOAD'] = True
login_manager = LoginManager()
login_manager.init_app(app)
init_db()


@login_manager.user_loader
def load_user(email):
    return User.query.filter(User.email == email).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.run(debug=True, use_reloader=True)

