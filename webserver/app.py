from flask import Flask
from flask import session

from flask_session import Session

from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap


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

from nav import nav
from frontend import frontend

def create_app():
    # @alt app = Flask('yourapplication')
    # @alt app = Flask(__name__.split('.')[0])
    app = Flask(__name__)
    app.secret_key = 'secret-key'
    # import os
    # from os import urandom
    # app.secret_key = str(os.urandom(16)) # disables the cookied headers from other/previous app instances
    UPLOAD_FOLDER = 'st_files'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'st'}
    

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS   
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 
    
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
   
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    # bcrypt.init_app(app)
    # sess=Session()
    # sess.init_app(app)
    # print (db.session)
    Bootstrap(app)
    
    # Our application uses blueprints as well; these go well with the
    # application factory. We already imported the blueprint, now we just need
    # to register it:
    app.register_blueprint(frontend)

    # Because we're security-conscious developers, we also hard-code disabling
    # the CDN support (this might become a default in later versions):
    # app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # We initialize the navigation as well
    nav.init_app(app)
    
    return app


#def init_app(app):
def configure_openplc(app):
    global openplc_runtime
    with app.app_context():
        pass
