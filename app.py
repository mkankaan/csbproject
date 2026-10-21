from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import abort

import sqlite3

import users
import rooms
import messages
import members

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

    user_rooms = rooms.get_user_rooms(user_id)
    chat_rooms = {}

    for room in user_rooms:
        room_id = room["id"]
        chat_rooms[room_id] = { "id": room_id,
                               "owner": room["owner"],
                               "name": room["name"],
                               "joined": room["joined"],
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
        room_name = request.form["room_name"]
        user_id = session["user_id"]
        print("create chat room", room_name, "user", user_id)

        rooms.create_room(room_name, user_id)
        return redirect("/user/" + str(session["user_id"]))


@app.route("/room/<int:room_id>")
def chat_room(room_id):
    room = rooms.get_room(room_id)
    user = users.get_user(session["user_id"])  

    if not room:
        abort(404)

    room_messages = messages.get_messages_by_room(room_id)
    room_members = members.get_by_room(room_id)
    usernames=[member["username"] for member in room_members]

    return render_template("room.html", room=room, user=user, messages=room_messages, members=usernames)


@app.route("/new_message", methods=["POST"])
def new_message():
    if request.method == "POST":
        room_id = request.form["room_id"]
        content = request.form["content"]
        user_id = session["user_id"]
        messages.create_message(user_id, room_id, content)
        return redirect("/room/" + str(room_id))


@app.route("/add_member", methods=["POST"])
def add_member():
    if request.method == "POST":
        # check that logged in user is owner
        room_id = request.form["room_id"]
        username = request.form["username"]
        print("add member", username, "to room", room_id)

        user = users.get_by_username(username)

        if not user:
            print("user doesn't exist")
        else:
            new_member_id = user["id"]
            print("found", username, "id", new_member_id)
            members.add_member(new_member_id, room_id)

        return redirect("/room/" + str(room_id))



