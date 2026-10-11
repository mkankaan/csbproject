from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import abort

import sqlite3

import users

app = Flask(__name__)
app.secret_key = "1"
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    all_users = users.get_all_users()

    # delete
    if len(all_users) > 0:
        print("all users:")
        for user in all_users:
            print(user["username"], user["password"])
    else:
        print("no users")


    if "user_id" not in session:
        return redirect("/login")
    else:
        return redirect("/user/" + str(session["user_id"]))


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = users.check_password_matches(username, password)

        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            print("wrong username or password")
            return render_template("login.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")


@app.route("/user/<int:user_id>")
def user_page(user_id):
    user = users.get_user(user_id)

    if not user:
        abort(404)

    return render_template("user.html", user=user)

