from flask import Flask, g
import config
from .urls.blueprints import Blueprints
from flask.ext.login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from iptv_app.models.user import User
from sqlalchemy.ext.declarative import declarative_base
from flask_user import login_required, UserManager, SQLAlchemyAdapter
from flask_mail import Mail
login_manager = LoginManager()
login_manager.login_view = 'auth.login_development'


@login_manager.user_loader
def load_user(id):
    return g.db.query(User).filter_by(id=int(id)).first()


def init_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.before_request(get_current_user)
    app.before_request(db_session)
    blueprints = Blueprints(app)
    app = blueprints.register()
    login_manager.init_app(app)
    mail = Mail(app)
    Base = declarative_base()
    db = SQLAlchemy(app)

    class UserModify(db.Model, User):
        pass
    db_adapter = SQLAlchemyAdapter(db, UserModify)
    user_manager = UserManager(db_adapter, app)
    return app


def get_current_user():
    g.user = current_user


def db_session():
    Base = declarative_base()
    db = SQLAlchemy(init_app())
    db.Model = Base
    g.db = db.session
