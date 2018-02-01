import bcrypt

from app.database import init_db, db_session
from app.models import User

init_db()
user = User('benjefferies@echosoft.uk', bcrypt.hashpw('password'.encode(), bcrypt.gensalt()))
db_session.add(user)
db_session.commit()