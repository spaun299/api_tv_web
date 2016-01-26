from sqlalchemy.ext.declarative import declarative_base
from flask import g
Base = declarative_base()


def db_query(arg, **kwargs):
    return g.db.query(arg).filter_by(**kwargs)