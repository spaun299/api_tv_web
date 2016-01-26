from sqlalchemy import Column, Integer, String, Boolean, DateTime
from db_init import Base, db_query
from datetime import datetime
from flask_user import UserMixin
from flask import session, g
import urllib
import hashlib
import json


class User(Base, UserMixin):

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    shown_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200))
    reset_password_token = Column(String(100))
    md_tm = Column(DateTime, default=datetime.utcnow())
    confirmed_at = Column(DateTime)
    active = Column(Boolean, nullable=False)
    registered_via = Column(String(70), default='tv.online.in.ua')
    facebook_id = Column(String(500), unique=True)
    vkontakte_id = Column(String(500), unique=True)
    google_id = Column(String(500), unique=True)

    def __init__(self, username=None, email=None, password=None, reset_password_token=None,
                 confirmed_at=None, active=None, registered_via='tv.online.in.ua', shown_name=None,
                 facebook_id=None, vkontakte_id=None, google_id=None):
        self.username = username
        self.email = email
        self.password = password
        self.shown_name = shown_name
        self.reset_password_token = reset_password_token
        self.confirmed_at = confirmed_at
        self.active = active
        self.registered_via = registered_via
        self.facebook_id = facebook_id
        self.vkontakte_id = vkontakte_id
        self.google_id = google_id

    def avatar(self, size=100):
        if session.get('login_via') == 'vkontakte':
            avatar = json.load(urllib.urlopen("https://api.vk.com/method/users.get?v=5.8&fields="
                                              "photo_{size}&access_token={access_token}".
                                              format(size=str(size),
                                                     access_token=session['access_token'])))['response'][0].get(
                                                     'photo_{size}'.format(size=size))
            if avatar == 'http://vk.com/images/camera_{size}.png'.format(size=size):
                avatar = self.gravatar(size=size)
        if session.get('login_via') == 'facebook':
            avatar = json.load(urllib.urlopen('http://graph.facebook.com/{facebook_id}/picture?width={size}&height={size}&redirect=0'.format(
                facebook_id=g.user.facebook_id, size=size)))
            if avatar['data'].get('is_silhouette'):
                avatar = self.gravatar(size=size)
            else:
                avatar = avatar['data'].get('url')
        else:
            avatar = self.gravatar(size=size)

        return avatar

    def gravatar(self, size=100):
        email = self.email
        default = 'http://s16.postimg.org/bkksnh1qp/Default_Avatar.png'
        gravatar = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar += urllib.urlencode({'d': default, 's': str(size)})
        return gravatar

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
