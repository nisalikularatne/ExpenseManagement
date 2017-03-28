from sqlalchemy import ForeignKey,Column,Integer,String,DateTime
import sys
import unicodedata
import datetime
from datetime import date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy import create_engine
Base=declarative_base()
#create User table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(250),nullable=False)
    password=Column(String(20),nullable=False)
    email = Column(String(250), nullable=False)
    registered_on = Column(DateTime, default=datetime.datetime.utcnow())
    budget = RelationshipProperty("Budget")
    transactions = RelationshipProperty("Transactions")



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
        return self.id

    def __repr__(self):
       return '<User %r>' % (self.username)



class Budget(Base):
    __tablename__='budget'
    id = Column(Integer, primary_key=True)
    B_name=Column(String(250),nullable=False)
    B_Amount=Column(Integer(200))
    registered_on = Column(DateTime, default=datetime.datetime.utcnow())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = RelationshipProperty(User)
    category=RelationshipProperty("Categories")
    transactions = RelationshipProperty("Transactions")

class Categories(Base):
    __tablename__='categories'
    id=Column(Integer,primary_key=True)
    C_name = Column(String(250), nullable=False)
    Icon  = Column(String(250), nullable=False)
    Icon_Face = Column(String(250), nullable=False)
    budget = RelationshipProperty(Budget)
    registered_on = Column(DateTime, default=datetime.datetime.utcnow())
    budget_id = Column(Integer, ForeignKey('budget.id'))

    transactions = RelationshipProperty("Transactions")

class Transactions(Base):
    __tablename__='transactions'
    id=Column(Integer,primary_key=True)
    B_Amount = Column(String(200),nullable=False)
    description=Column(String(1000))
    registered_on = Column(DateTime)
    budget_id = Column(Integer, ForeignKey('budget.id'))
    category_id=Column(Integer,ForeignKey('categories.id'))
    transaction_user_id = Column(Integer, ForeignKey('user.id'))
    user = RelationshipProperty(User)
    budget = RelationshipProperty(Budget)
    category = RelationshipProperty(Categories)








#engine creation
engine=create_engine('sqlite:///HomeAutomation.db')
Base.metadata.create_all(engine)
