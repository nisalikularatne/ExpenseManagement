# import all the modules for the project
from flask import Flask, jsonify, render_template, url_for
from flask_googlecharts import GoogleCharts, BarChart, MaterialLineChart
from flask_googlecharts.utils import prep_data
import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask import flash,jsonify
from flask_login import login_user
from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker
from flask_wtf import Form
from database_setup import User,Base,Budget,Categories,Transactions
from flask_login import LoginManager
from flask import session as login_session
from wtforms import DateField
from datetime import datetime
from flask_googlecharts import BarChart,PieChart

import json
import urllib2 as url_request
import simplejson
from flask_googlecharts import GoogleCharts
import os
import requests

os.environ['no_proxy'] = '127.0.0.1,localhost'

app = Flask(__name__)
@app.route('/chart', methods=['GET', 'POST'])
def chart():
	# The data can come from anywhere you can read it; for instance, a SQL
	# query or a file on the filesystem created by another script.
	# This example expects two values per row; for more complicated examples,
	# refer to the Google Charts gallery.

    r = requests.get('http://0.0.0.0:9000/chart/JSON',allow_redirects=False)
    data = json.load(r)
    return render_template('template.html', data=data)

login_manager = LoginManager()
login_manager.init_app(app)
engine = create_engine('sqlite:///HomeAutomation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class DateForm(Form):
    dt = DateField('Pick a Date', format="%m/%d/%Y")

login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(id):
    return session.query(User).get(int(id))




@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('HomePage.html')
@app.route('/hi', methods=['GET', 'POST'])
def hi():
    if 'username' not in login_session:
        return render_template(
            'register.html')
    else:
      return render_template('FrontPage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username=request.form['username'];
    email=request.form['email'];
    registered_user = session.query(User).filter_by(username=username).all()
    registered_email=session.query(User).filter_by(email=email).all()
    if int(len(registered_user))>0:
        flash("User already exists")
        return  redirect(url_for('register'))
    if int(len(registered_email))>0:
        flash("Email registered on database")
        return  redirect(url_for('register'))
    else:
      user = User(request.form['username'], request.form['password'], request.form['email'])
      session.add(user)
      session.commit()
      flash('User successfully registered')
      return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    registered_user = session.query(User).filter_by(username=username,password=password).first()
    if request.method=='POST':
     if registered_user is None:
        flash('Username or Password is invalid')

     else:
      login_session['username'] = username
      login_session['password']= password
      login_session['user_id']=registered_user.id
      login_user(registered_user)
      flash('Logged in successfully')
      return redirect(url_for('showbudget'))
    return render_template('login.html')

@app.route('/createBudget',methods=['GET','POST'])
def newBudget():
    if request.method == 'POST':
        newbudgetname = Budget(
            B_name=request.form['name'],
            B_Amount=float(request.form['B_Amount']),
            user_id=login_session['user_id'])
        session.add(newbudgetname)
        session.commit()
        flash('new budget created')
        return render_template('Frontpage.html')
    else:
        return render_template('createnewbudget.html')

@app.route('/budget',methods=['GET','POST'])
def showbudget():
    budget_first = session.query(Budget).all()
    transactions=session.query(Transactions.budget_id.label("budget_id"),func.sum(Transactions.B_Amount).label("total"))
    transactions=transactions.group_by(Transactions.budget_id).all()
    budget_user_id=login_session['user_id']


    return render_template(
            'budget.html',budget_first=budget_first,budget_user_id=budget_user_id,transactions=transactions)

@app.route('/chart/JSON',methods=['GET','POST'])
def showchartJSON():

    chart=session.query(Categories.C_name,func.sum(Transactions.B_Amount).label('total')).filter(Categories.id==Transactions.category_id).group_by(Categories.C_name).all()
    l=jsonify(Categories=chart)

    data=map(list,chart)
    return render_template('template.html',data=data)




"""new category"""
@app.route('/budget/<int:budget_id>/categories/new', methods=['GET', 'POST'])
def newBudgetCategory(budget_id):
    budget = session.query(Budget).filter(Budget.id == budget_id).one()
    if request.method == 'POST':
        newBudgetCategory = Categories(
            C_name=request.form['name'],budget_id=budget_id)
        session.add(newBudgetCategory)
        session.commit()
        flash('new category created')
        return redirect(url_for('showCategory',budget_id=budget_id))
    else:
        return render_template(
            'newcategory.html',budget=budget,budget_id=budget_id )

@app.route('/budget/<int:budget_id>/categories', methods=['GET', 'POST'])
def showCategory(budget_id):
    budget = session.query(Budget).filter(Budget.id == budget_id).one()
    categories = session.query(Categories).filter(
        budget_id == Categories.budget_id).all()


    return render_template(
            'categories.html', budget=budget, categories=categories,budget_id=budget_id)

@app.route('/clearSession')
def clearSession():
    login_session.clear()
    flash("logged out")
    return redirect('/login')

@app.route('/budget/<int:budget_id>/categories/<int:category_id>/newTransaction', methods=['GET', 'POST'])
def newTransaction(category_id,budget_id):
    category = session.query(Categories).filter(Categories.id == category_id).one()
    budget = session.query(Budget).filter(Budget.id == budget_id).one()

    if request.method == 'POST':
        dt_start = datetime.strptime(request.form['transaction-date'], '%Y-%m-%d')

        newCategoryTransaction = Transactions(
            B_Amount=request.form['amount'],registered_on=dt_start, category_id=category_id,budget_id=budget_id)
        session.add(newCategoryTransaction)
        session.commit()
        flash('new category created')
        return redirect(url_for('showTransactions', category_id=category_id,budget_id=budget_id))
    else:
        return render_template(
            'newTransactions.html', category_id=category_id,budget_id=budget_id,budget=budget,category=category)

@app.route('/budget/<int:budget_id>/categories/<int:category_id>/Transactions', methods=['GET', 'POST'])
def showTransactions(budget_id,category_id):
    transactions = session.query(Transactions).filter(
        category_id==Transactions.category_id).all()
    return render_template('transactions.html',transactions=transactions,category_id=category_id,budget_id=budget_id)



if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
