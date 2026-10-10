from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask import redirect

import sqlite3

import users

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    user_list = users.get_all_users()

    for user in user_list:
        print(user["username"])

    return "hello world"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
       
        # check username + password valid
       
        try:
            users.create_user(username, password)
            return redirect("/")
        except sqlite3.IntegrityError:
            print("username taken")
            return render_template("register.html")

