from sqlalchemy import ForeignKey,Column,Integer,String,DateTime
import sys
import unicodedata
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy import create_engine
Base=declarative_base()
#create User table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    password=Column(String(20),nullable=False)
    email = Column(String(250), nullable=False)
    registered_on = Column(DateTime, default=datetime.datetime.utcnow())


    def __init__(self, username, password, email):
       self.username = username
       self.password = password
       self.email = email
       self.registered_on = datetime.datetime.utcnow()


    def is_authenticated(self):
       return True


    def is_active(self):
       return True

    def is_anonymous(self):
       return False


    def get_id(self):
       return self.id.decode("UTF-8")


    def __repr__(self):
       return '<User %r>' % (self.username)
#engine creation
engine=create_engine('sqlite:///HomeAutomation.db')
Base.metadata.create_all(engine)
