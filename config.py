import os
from flask_oauth import OAuth

def database_url():
    db_url = os.environ['OPENSHIFT_POSTGRESQL_DB_URL'] if os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL') else \
        'postgresql://admin:1111@localhost:5432/api'

    return db_url

SQLALCHEMY_DATABASE_URI = database_url()
DEBUG = True
SECRET_KEY = 'asdfkjsdg;lk2asd`~s63xzcx/.xalsdfriotpeir342dsfdsefdlfm'
OPENSHIFT_PASSWORD = SECRET_KEY
MAIL_USERNAME = 'api.tv.web@gmail.com'
MAIL_PASSWORD = "/~sdfk`ds21wfvcbmghj45xzccc687xvcjh;;65~13"
SOCIAL_NETWORK_MAIL = 'tvonline.in.ua@gmail.com'
SOCIAL_NETWORK_PASSWORD = 'mvfd4v~sda3sa0s-dsdsdxz`+xl;gf'
MAIL_DEFAULT_SENDER = 'api.tv.web@gmail.com <api.tv.web@gmail.com>'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
USER_APP_NAME = 'api.tv.web'
# USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
USER_LOGIN_TEMPLATE = 'login_development.html'
USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
USER_AUTO_LOGIN_AFTER_CONFIRM = True
USER_AUTO_LOGIN_AFTER_REGISTER = False
