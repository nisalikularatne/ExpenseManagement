from flask import Flask
# import all the modules for the project
from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from flask_login import login_user , logout_user , current_user , login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User,Base,Budget,Categories,Transactions
from flask_login import LoginManager
from flask import session as login_session
app = Flask(__name__)
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

@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('HomePage.html')


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
      return redirect(url_for('newBudget'))
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
        return redirect(url_for('showbudget'))
    else:
        return render_template('createnewbudget.html')

@app.route('/budget',methods=['GET','POST'])
def showbudget():
    budget_first = session.query(Budget).all()
    transactions=session.query(Transactions).filter(Transactions.budget_id==Budget.id).all()
    budget_user_id=login_session['user_id']


    return render_template(
            'budget.html',budget_first=budget_first,budget_user_id=budget_user_id,transactions=transactions)

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

@app.route('/budget/<int:budget_id>/categories/<int:category_id>/newTransaction', methods=['GET', 'POST'])
def newTransaction(category_id,budget_id):
    category = session.query(Categories).filter(Categories.id == category_id).one()
    budget = session.query(Budget).filter(Budget.id == budget_id).one()
    if request.method == 'POST':
        newCategoryTransaction = Transactions(
            B_Amount=request.form['amount'], category_id=category_id,budget_id=budget_id)
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
