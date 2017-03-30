# import all the modules for the project
import datetime
from datetime import date
from flask import Flask, render_template, request, redirect, url_for,send_from_directory
from flask import flash,jsonify
from flask_login import login_user
from sqlalchemy import create_engine,func,extract
from sqlalchemy.orm import sessionmaker
from database_setup import User,Base,Budget,Categories,Transactions
from flask_login import LoginManager
from flask import session as login_session
from datetime import datetime
from datetime import timedelta
import os
from passlib.hash import sha256_crypt
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
photos = UploadSet('photos', IMAGES)

os.environ['no_proxy'] = '127.0.0.1,localhost'
#statements to load the database
app = Flask(__name__)
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
engine = create_engine('sqlite:///HomeAutomation.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(id):
    return session.query(User).get(int(id))

#url and functionality for the front page
@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('HomePage.html')

#url for the dashboard and also its functionality
@app.route('/hi', methods=['GET', 'POST'])
def hi():
    #the dashboard only renders if a user is logged into the system else it redirects to the login page
    if 'username' not in login_session:
        return render_template(
            'login.html')
    else:
        today=date.today()#gets todays details
        month=today.month#gets the current month
        budget_user_id = login_session['user_id']#get the logged in users id
        budget_first = session.query(Budget).filter(extract('month',Budget.registered_on) == month,Budget.user_id==budget_user_id).all()#extracts all the budgets in the current month of the user logged in
        budget_count = session.query(Budget, func.count().label("sum")).filter(Budget.user_id == budget_user_id,extract('month',Budget.registered_on) == month).one()#function to count how many budgets the user has created
        #to get the transactions made in the current month
        number_transaction=session.query(Transactions,func.count().label("number_trans")).filter(
        Transactions.transaction_user_id==login_session['user_id'],extract('month',Transactions.registered_on) == month).one()
        #the transaction object for the table of transactions in the dashboard
        transactions = session.query(Transactions).filter(Transactions.transaction_user_id==login_session['user_id']).all()
        category = session.query(Categories).all();
        return render_template('dashboard.html',category=category,number_transaction=number_transaction, transactions=transactions,budget_first=budget_first, budget_user_id=budget_user_id, budget_count=budget_count)

@app.template_filter('strftime')
def datetimeformat(date, format='%d-%m-%Y'):
        return date.strftime(format)
#the handler which deals with the user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form['username'];
    email = request.form['email'];
    registered_user = session.query(User).filter_by(username=username).all()
    registered_email = session.query(User).filter_by(email=email).all()
    if int(len(registered_user)) > 0:
        flash("User already exists")
        return redirect(url_for('register'))
    if int(len(registered_email)) > 0:
        flash("Email registered on database")
        return redirect(url_for('register'))
    else:
        password = sha256_crypt.encrypt(request.form['password'])
        user = User(request.form['username'], password, request.form['email'])
        session.add(user)
        session.commit()
        flash('User successfully registered')
        return redirect(url_for('login'))
#contact handler not yet working
@app.route('/contact')
def contact():
    return render_template('Contact.html')

#login handler for the software
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')


    username = request.form['username']
    password = sha256_crypt.encrypt(request.form['password'])
    registered_user = session.query(User).filter_by(username=username).first()
    if request.method == 'POST':
        text = request.form.get('checksign')
        if text:
            session.permanent = True
        if not text:
            session.permanent = False
            app.permanent_session_lifetime = timedelta(seconds=5)
        if registered_user is None:
            flash('Username or Password is invalid')

        elif sha256_crypt.verify(request.form['password'], password):

            login_session['username'] = username
            login_session['password'] = password
            login_session['user_id'] = registered_user.id
            login_user(registered_user)
            flash('Logged in successfully')
            return redirect(url_for('hi'))
    return render_template('login.html')

#when a budget under the navigation bar is clicked it renders a new page with the budget details and also we can then make new transactions from there
@app.route('/budget/<int:budget_id>',methods=['GET','POST'])
def showindividualbudget(budget_id):
    budget_first = session.query(Budget).filter(Budget.id == budget_id).one()#gets the budget details depending on which budget is clicked
    transactions = session.query(Transactions.budget_id.label("budget_id"),
                                 func.sum(Transactions.B_Amount).label("total"))
    transactions = transactions.group_by(Transactions.budget_id).all()# calculation of total transaction for that budget
    categories = session.query(Categories).filter(
        budget_id == Budget.id).all()#categories for that budget
    categoriesfull = session.query(Categories).all()#all the categories..This is used for the dropdown for selecting the category for which the transaction should be made
    categoriesnames = session.query(Categories).filter(
        Categories.id == Transactions.category_id, budget_id==Transactions.budget_id).all()
    transactionsinbudget=session.query(Transactions).filter(
        budget_id==Transactions.budget_id).all()
    groupbytransactions=session.query(Categories.C_name,Transactions.description,func.sum(Transactions.B_Amount).label('transaction_category')).filter(Transactions.budget_id==budget_id,Transactions.category_id==Categories.id).group_by(Categories.C_name).all()
    #handles the posting of a transaction into the database
    if request.method=='POST':
      categoryname=request.form.get('categoryname')
      categoryidofname = session.query(Categories).filter(
          Categories.C_name == categoryname).one()

      newCategoryTransaction = Transactions(
          B_Amount=request.form['amount'], registered_on=datetime.now(), category_id=categoryidofname.id, budget_id=budget_id,
          transaction_user_id=login_session['user_id'],description=request.form['description'])
      session.add(newCategoryTransaction)
      session.commit()
      return redirect(url_for('showindividualbudget', budget_id=budget_id))


    return render_template('individualbudget.html', categoriesfull=categoriesfull, categoriesnames=categoriesnames,
                           budget_first=budget_first, transactions=transactions,
                           transactionsinbudget=transactionsinbudget, categories=categories,groupbytransactions=groupbytransactions)

#for handling the charts
@app.route('/charts',methods=['GET','POST'])
def showchartJSON():
    today = date.today()  # gets todays details
    month = today.month  # gets the current month
    budget_user_id = login_session['user_id']  # get the logged in users id
   # extracts all the budgets in the current month of the user logged in
    budgetname1 = request.form.get('budgetname')
    budget_first = session.query(Budget).filter(extract('month', Budget.registered_on) == month,
                                                Budget.user_id == budget_user_id).all()



    if request.method=='POST' and request.form.get('budgetname') and request.form.get('monthname'):
        budgetname = request.form.get('budgetname')
        month=request.form.get('monthname')
        budget_first = session.query(Budget).filter(extract('month', Budget.registered_on) == month,
                                                    Budget.user_id == budget_user_id).all()
        budgetid = session.query(Budget).filter(Budget.B_name == budgetname).first()
        chart = session.query(Categories.C_name, func.sum(Transactions.B_Amount).label('total')).filter(
            Categories.id == Transactions.category_id, Transactions.budget_id == budgetid.id).group_by(
            Categories.C_name).all()
        data = map(list, chart)
        return render_template('charts.html',data=data,budgetname=budgetname,budget_first=budget_first,month=month)
    if request.method == 'POST' and request.form.get('monthname'):
        month = request.form.get('monthname')
        budget_first = session.query(Budget).filter(extract('month', Budget.registered_on) == month,
                                                    Budget.user_id == budget_user_id).all()

        return render_template('charts.html', budget_first=budget_first)

    return render_template('charts.html', budget_first=budget_first, month=month)


#for handling the reports
@app.route('/reports/monthly',methods=['GET','POST'])
def showreports():
    if request.method=='POST':
      month=request.form.get('monthname');
      budget_user_id = login_session['user_id']
      budget_name = session.query(Budget).filter(extract('month',Budget.registered_on) == month,Budget.user_id==budget_user_id).all();
      category = session.query(Categories).all();
      transaction = session.query(Transactions).all();
      return render_template('reports.html',budget_name = budget_name,category = category,transaction = transaction,month=month)
    return render_template('reports.html')
@app.template_filter('strftime')
def datetimeformat(date, format='%d-%m-%Y %H:%M'):
        return date.strftime(format)

@app.route('/reports/yearly',methods=['GET','POST'])
def showweeklyreports():
    if request.method=='POST':
      year=request.form.get('year');
      budget_user_id = login_session['user_id']
      budget_name = session.query(Budget).filter(extract('year',Budget.registered_on) == year,Budget.user_id==budget_user_id).all();
      category = session.query(Categories).all();
      transaction = session.query(Transactions).all();

      return render_template('weeklyreport.html',budget_name = budget_name,category = category,transaction = transaction,year=year)
    return render_template('weeklyreport.html')
@app.template_filter('strftime')
def datetimeformat(date, format='%d-%m-%Y %H:%M'):
        return date.strftime(format)

@app.template_filter('str')
def dateformat(date, format='%d-%m-%Y %H:%M'):
    return date.strftime('%B')
#for the log out functionality
@app.route('/clearSession')
def clearSession():
    login_session.clear()
    flash("logged out")
    return redirect('/login')


#main function
if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
