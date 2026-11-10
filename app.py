from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask import flash

import sqlite3
import secrets

import users
import rooms
import messages
import members

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
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
       
        # check username + password valid
       
        try:
            users.create_user(username, password)
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Username already taken")
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
            # FLAW 3 FIX:
            # session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("Incorrect username or password")
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
# FLAW 1 FIX:
# @app.route("/profile")
def user_page(user_id):    
    """
    FLAW 1 FIX:
    if "user_id" in session:
        user_id = users.get_user(session["user_id"])
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

    """
    FLAW 1 FIX:
    if session["user_id"] not in [member["user_id"] for member in room_members]:
        abort(403)
    """


    return render_template("room.html", room=room, messages=room_messages, members=room_members)


@app.route("/new_message", methods=["POST"])
def new_message():
    if request.method == "POST":
        print(dict(request.form))

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
        print(dict(request.form))

        """
        FLAW 3 FIX:
        if "csrf_token" not in request.form or request.form["csrf_token"] != session["csrf_token"]:
            abort(403)
        """
        
        room_id = request.form["room_id"]
        username = request.form["username"]
        user = users.get_by_username(username)

        if not user:
            flash("User not found")
            return redirect("/room/" + str(room_id))
        else:
            new_member_id = user["id"]
            members.add_member(new_member_id, room_id)

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
            user_id = users.get_user(session["user_id"])
        else:
            abort(403)
        """

        user = users.get_user(user_id)
        
        if not user:
            abort(404)

        return render_template("edit_profile.html", user=user, username_error="", password_error="")


@app.route("/change_username", methods=["POST"])
def change_username():
    if request.method == "POST":
        # csrf!
        user_id = session["user_id"]
        user = users.get_user(user_id)
        new_username = request.form["new_username"]

    try:
        users.change_username(user_id, new_username)
        user = users.get_user(user_id)
        session["username"] = new_username
        return render_template("edit_profile.html", user=user, username_error="", password_error="")
    
    except sqlite3.IntegrityError:
        print("username taken")
        return render_template("edit_profile.html", user=user, username_error="Username already taken", password_error="")


@app.route("/change_password", methods=["POST"])
def change_password():
    if request.method == "POST":
        # csrf!
        user_id = session["user_id"]
        user = users.get_user(user_id)
        new_password = request.form["new_password"]
        new_password2 = request.form["new_password2"]
        old_password = request.form["old_password"]

    if new_password != new_password2:
        return render_template("edit_profile.html", user=user, username_error="", password_error="Passwords don't match")

    if old_password != user["password"]:
        return render_template("edit_profile.html", user=user, username_error="", password_error="Old password is incorrect")

    if new_password == old_password:
        return render_template("edit_profile.html", user=user, username_error="", password_error="New password can't be the same as old password")

    # validate new password

    users.change_password(user_id, new_password)
    return render_template("edit_profile.html", user=user, username_error="", password_error="")


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

        # check that user is owner

        rooms.delete_room(room_id)
        return redirect("/user/" + str(user_id))

