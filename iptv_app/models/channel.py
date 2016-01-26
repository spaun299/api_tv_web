from sqlalchemy import Column, Integer, String
from db_init import Base


class Channel(Base):

    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    def __init__(self, name=None):
        self.name = name
