from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask import flash

import sqlite3
import hashlib
import secrets # FLAW 3 FIX
import logging # FLAW 5 FIX
import hmac # FLAW 4 FIX
import re # FLAW 6 FIX

import users
import rooms
import messages
import members
from security_params import * # FLAW 4 FIX

#logging.basicConfig(filename='record.log', level=logging.DEBUG) # FLAW 5 FIX
app = Flask(__name__)
app.secret_key = "1"
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    else:
        return redirect("/user/" + str(session["user_id"]))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        errors = []
   
        if len(username.replace(' ', '')) != len(username):
            errors.append("Username can't contain spaces")

        if len(password.replace(' ', '')) != len(password):
            errors.append("Password can't contain spaces")

        # FLAW 6 FIX:
        # errors += strong_password(password, username)

        if errors:
            return render_template("register.html", errors=errors, filled={"username": username})       

        try:
            users.create_user(username, password)
            return redirect("/")
        except sqlite3.IntegrityError:
            return render_template("register.html", errors=["Username already taken"], filled={"username": username})       


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
            # FLAW 3 FIX:
            # session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("Wrong username or password")
            return render_template("login.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
        # FLAW 3 FIX:
        # del session["csrf_token"]
    return redirect("/")


@app.route("/user/<int:user_id>")
def user_page(user_id):
# FLAW 1 FIX:
# @app.route("/profile")
# def user_page():
    """
    FLAW 1 FIX:
    if "user_id" in session:
        user_id = session["user_id"]
    else:
        abort(403)
    """

    user = users.get_user(user_id)

    if not user:
        abort(404)

    user_rooms = rooms.get_user_rooms(user_id)
    chat_rooms = {}

    for room in user_rooms:
        room_id = room["id"]
        chat_rooms[room_id] = { "id": room_id,
                               "owner": room["owner"],
                               "owner_username": room["owner_username"],
                               "name": room["name"],
                               "members": []}
        room_members = list(members.get_by_room(room_id))

        for member in room_members:
            chat_rooms[room_id]["members"].append(member["username"]) 

    return render_template("user.html", user=user, chat_rooms = chat_rooms)


@app.route("/new_room", methods=["GET", "POST"])
def new_room():
    if request.method == "GET":
        return render_template("new_room.html")

    if request.method == "POST":
        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """
        
        room_name = request.form["room_name"]
        user_id = session["user_id"]
        rooms.create_room(room_name, user_id)
        return redirect("/user/" + str(session["user_id"]))


@app.route("/room/<int:room_id>")
def chat_room(room_id):
    """
    FLAW 1 FIX:
    if "user_id" not in session:
        abort(403)
    """
    
    room = rooms.get_room(room_id)

    if not room:
        abort(404)

    room_messages = messages.get_messages_by_room(room_id)
    room_members = members.get_by_room(room_id)
    user_search_results = []
    error = ""

    if "user_search_results" in session:
        user_search_results = session["user_search_results"]
        error = session["search_results_error"]
        del session["user_search_results"]
        del session["search_results_error"]

    """
    FLAW 1 FIX:
    if session["user_id"] not in [member["user_id"] for member in room_members]:
        abort(403)
    """

    return render_template("room.html", room=room, messages=room_messages, members=room_members, user_search_results=user_search_results, error=error)


@app.route("/search_user", methods=["POST"])
def search_user():
    username = request.form["username"]
    room_id = request.form["room_id"]
    results = users.search_user(username, room_id)
    session["user_search_results"] = [user["username"] for user in results]
    session["search_results_error"] = "No results" if results == [] else ""
    return redirect("/room/" + str(room_id))


@app.route("/new_message", methods=["POST"])
def new_message():
    if request.method == "POST":
        print(dict(request.form)) # for screenshots

        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """

        room_id = request.form["room_id"]
        content = request.form["content"]
        user_id = request.form["user_id"]
        messages.create_message(user_id, room_id, content)
        return redirect("/room/" + str(room_id))


@app.route("/add_member", methods=["POST"])
def add_member():
    if request.method == "POST":        
        print("Add member", dict(request.form)) # for screenshots

        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """
        
        room_id = request.form["room_id"]
        user = users.get_by_username(request.form.get("username"))
        members.add_member(user["id"], room_id)
        return redirect("/room/" + str(room_id))


@app.route("/leave_room", methods=["POST"])
def leave_room():
    if request.method == "POST":
        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """
        
        room_id = request.form["room_id"]
        user_id = session["user_id"]
        members.remove_member(user_id, room_id)
        return redirect("/user/" + str(user_id))


@app.route("/edit_profile/<int:user_id>", methods=["GET"])
def edit_profile(user_id):
# FLAW 1 FIX:
# @app.route("/edit_profile", methods=["GET"])
# def edit_profile():
    if request.method == "GET":
        """
        FLAW 1 FIX:
        if "user_id" in session:
            user_id = session["user_id"]
        else:
            abort(403)
        """

        user = users.get_user(user_id)
        
        if not user:
            abort(404)

        return render_template("edit_profile.html", user=user, username_error="", filled={"username": user["username"]})


@app.route("/change_username", methods=["POST"])
def change_username():
    if request.method == "POST":
        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """
        
        user_id = request.form["user_id"]

        # FLAW 1 FIX:
        # user_id = session["user_id"]

        user = users.get_user(user_id)
        new_username = request.form["new_username"]

        if len(new_username.replace(' ', '')) != len(new_username):
            print("spaces")
            return render_template("edit_profile.html", user=user, username_error="Username can't contain spaces", filled={"username": new_username})

        try:
            users.change_username(user_id, new_username)
            user = users.get_user(user_id)
            session["username"] = new_username
            return render_template("edit_profile.html", user=user, username_error="Username changed", filled={"username": new_username})
        except sqlite3.IntegrityError:
            return render_template("edit_profile.html", user=user, username_error="Username already taken", filled={"username": new_username})


@app.route("/change_password", methods=["POST"])
def change_password():
    if request.method == "POST":
        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """
        
        user_id = request.form["user_id"]
        
        # FLAW 1 FIX:
        # user_id = session["user_id"]

        user = users.get_user(user_id)
        new_password1 = request.form["new_password"]
        new_password2 = request.form["new_password2"]
        old_password = request.form["old_password"]

        errors = validate_new_password(new_password1, new_password2, old_password, user["password_hash"])
        # FLAW 4 FIX:
        # errors = validate_new_password(new_password1, new_password2, old_password, user["password_hash"], user["salt"])

        if errors == []:
            users.change_password(user_id, new_password1)
            flash("Password changed")
        else:
            for error in errors:
                flash(error)

        return render_template("edit_profile.html", user=user, username_error="", filled={"username": user["username"]})


def validate_new_password(new_password1, new_password2, old_password, old_password_hash):
    if new_password1 != new_password2:
        return ["Passwords don't match"]

    if len(new_password1.replace(' ', '')) != len(new_password1):
        return ["Password can't contain spaces"]

    sha1 = hashlib.sha1()
    sha1.update(old_password.encode())
    old_password_input_hash = sha1.hexdigest()

    if old_password_input_hash != old_password_hash:
        return ["Old password is incorrect"]

    sha1 = hashlib.sha1()
    sha1.update(new_password1.encode())
    new_password_hash = sha1.hexdigest()
            
    if new_password_hash == old_password_hash:
        return ["New password can't be the same as old password"]

    return []


"""
FLAW 4 FIX:
def validate_new_password(new_password1, new_password2, old_password, old_password_hash, salt):
    if new_password1 != new_password2:
        return ["Passwords don't match"]

    if len(new_password1.replace(' ', '')) != len(new_password1):
        return ["Password can't contain spaces"]

    old_password_input_hash = hashlib.scrypt(old_password.encode(), salt=salt, n=N, r=R, p=P, maxmem=MAXMEM)

    if not hmac.compare_digest(old_password_input_hash, old_password_hash):
        return ["Old password is incorrect"]

    new_password_hash = hashlib.scrypt(new_password1.encode(), salt=salt, n=N, r=R, p=P, maxmem=MAXMEM)
            
    if hmac.compare_digest(new_password_hash, old_password_hash):
        return ["New password can't be the same as old password"]

    return []
"""

"""
FLAW 6 FIX:
def strong_password(password, username):
    errors = []
    password_stripped = password.replace(' ', '')

    if not re.search('\d', password):
        errors.append("Password should contain at least one number")

    if not re.search('.*[a-z].*', password):
            errors.append("Password should contain at least one lowercase letter")

    if not re.search('.*[A-Z].*', password):
        errors.append("Password should contain at least one uppercase letter")

    if len(password_stripped) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password should be at least {MIN_PASSWORD_LENGTH} characters")

    if len(password_stripped) > MAX_PASSWORD_LENGTH:
        errors.append("Password is too long")

    if password == username:
        errors.append("Username and password must be different")

    weak_passwords = [p.strip() for p in open("weakpasswords.txt")]

    if password in weak_passwords:
        errors.append("Password is too weak")

    return errors
"""


@app.route("/delete_room/<int:room_id>", methods=["POST"])
def delete_room(room_id):
    if request.method == "POST":
        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """

        room_id = request.form["room_id"]
        user_id = session["user_id"]
        rooms.delete_room(room_id)
        return redirect("/user/" + str(user_id))
