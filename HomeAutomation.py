from flask import Flask
# import all the modules for the project
from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from flask_login import login_user , logout_user , current_user , login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User,Base
from flask_login import LoginManager
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
    return 'Hello World!'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username=request.form['username'];
    registered_user = session.query(User).filter_by(username=username).all()
    if int(len(registered_user))>0:
        flash("User already exists")
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
      login_user(registered_user)
      flash('Logged in successfully')
      return redirect(url_for('hello'))
    return render_template('login.html')


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
