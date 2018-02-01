from flask import Flask
from flask_login import LoginManager
from werkzeug.utils import redirect

from app.database import init_db
from app.models import User
from app.routes import nano

app = Flask(__name__)
app.secret_key = 'secret'
app.register_blueprint(nano)
login_manager = LoginManager()
login_manager.init_app(app)
init_db()


@login_manager.user_loader
def load_user(email):
    return User.query.filter(User.email == email).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


app.run(host='0.0.0.0')
