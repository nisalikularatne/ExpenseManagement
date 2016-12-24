from flask import Flask
# import all the modules for the project
from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify
from flask import session as login_session
import random
import string
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
    return User.query.get(int(id))

@app.route('/index')
def hello_world():
    return 'Hello World!'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'], request.form['password'], request.form['email'])
    session.add(user)
    session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
