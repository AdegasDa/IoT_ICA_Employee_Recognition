from flask import Flask, render_template, request, redirect, session, jsonify

import json
import time
from dotenv import load_dotenv
from functools import wraps

from .config import config 
from . import my_db, pb


db = my_db.db

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = config.get('APP_SECRET_KEY')
db.init_app(app)


def login_is_required(function):
    @wraps(function) 
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        else:
            return function(*args, **kwargs)
    
    return wrapper


def admin_is_required(function):
    @wraps(function) 
    def wrapper(*args, **kwargs):
        if str(session['user_id']) != config.get("GOOGLE_ADMIN_ID"):
            return redirect("/index")
        else:
            return function(*args, **kwargs)
    
    return wrapper

 
@app.route("/", methods = ["GET", "POST"])
def signin():
    return render_template("signin.html")


@app.route("/signup", methods = ["GET"])
def signup():
    return render_template("signup.html")


@app.route("/index", methods = ["GET", "POST"])
@login_is_required
def index():
    
    return render_template("/index.html")


@app.route("/admin", methods = ["GET", "POST"])
@login_is_required
@admin_is_required
def admin():
    users = my_db.get_all_users()
    return render_template("/admin.html", users = users)


@app.route("/logout", methods = ["GET", "POST"])
def logout():
    my_db.logout(session['user_email'])
    session.clear()
    return redirect("/")


@app.route("/login", methods = ["POST"])
def login():
    email = request.form['email']
    password = request.form['password']

    res = my_db.login(email, password)
    if res['state'] == 1:
        user_info = my_db.get_user_info(email)
        if user_info:
            session['user_id'] = user_info['user_id']
            session['user_email'] = user_info['user_email']
            return redirect("/index")
    return redirect("/")


@app.route("/register", methods = ["POST"])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    res = my_db.register(email, password, confirm_password)
    if (res['state'] == 1):
        user_info = my_db.get_user_info(email)
        if user_info:
            print()
            session['user_id'] = user_info['user_id']
            session['user_email'] = user_info['user_email']
            return redirect("/index")
        return redirect("/")
    else:
        return redirect("/")


if __name__ == '__main__':
    app.run()
