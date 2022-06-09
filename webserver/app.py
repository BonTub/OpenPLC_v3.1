from flask import Flask
from flask import session

from flask_session import Session

from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from flask_login import(
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
    )

from models import db
# from models import migrate

migrate = Migrate()
bcrypt = Bcrypt()


login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"


def create_app():
    # @alt app = Flask('yourapplication')
    # @alt app = Flask(__name__.split('.')[0])
    app = Flask(__name__)
    app.secret_key = 'secret-key'
    # import os
    # from os import urandom
    # app.secret_key = str(os.urandom(16)) # disables the cookied headers from other/previous app instances
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
   
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    # bcrypt.init_app(app)
    # sess=Session()
    # sess.init_app(app)
    # print (db.session)

    return app


#def init_app(app):
def configure_openplc(app):
    global openplc_runtime
    with app.app_context():
        pass
