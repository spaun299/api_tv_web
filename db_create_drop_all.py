from db_init import db, Base
from iptv_app.models.user import User


def create_models():
    return db.create_all()


def drop_models():
    return db.drop_all()
