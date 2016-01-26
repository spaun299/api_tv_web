from sqlalchemy import Column, Integer, String
from db_init import Base
from flask import g


class Info(Base):

    __tablename__ = 'info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100))
    email = Column(String(100))
    password = Column(String(100))

    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password

    def save(self):
        g.db.add(self)
        g.db.commit()
