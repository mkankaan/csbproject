import db
import os
import hashlib
import hmac
from scrypt_params import *


def create_user(username, password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode())
    password_hash = sha1.hexdigest()
    sql = f"INSERT INTO users (username, password_hash, salt) VALUES ('{username}', '{password_hash}', '')"
    #db.execute(sql) # kommentti pois

    ### FLAW 4 FIX:
    salt = os.urandom(16)
    password_hash = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P, maxmem=MAXMEM)
    ###

    ### FLAWS 2 & 4 FIX:
    sql = "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)"
    db.execute(sql, [username, password_hash, salt])
    ###
    
    # for screenshots
    print("Create user:") 
    print("Username:\t", username)
    print("Password:\t", password)
    print("Password hash:\t", password_hash)



def get_user(user_id):
    sql = "SELECT id, username, password_hash FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_by_username(user_id):
    sql = "SELECT id FROM users WHERE username = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_all_users():
    sql = "SELECT username, password FROM users"
    return db.query(sql)

# bad code
def _check_password_matches(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, correct_password_hash = result[0]
        sha1 = hashlib.sha1()
        sha1.update(password.encode())
        password_hash = sha1.hexdigest() 

        if password_hash == correct_password_hash:
            return user_id
    
    return None

# FLAW 2 & 4 FIX
def check_password_matches(username, password):

    # FLAW 2 FIX:

    sql = "SELECT id, password_hash, salt FROM users WHERE username = ?"
    result = db.query(sql, [username])

    # FLAW 4 FIX:

    if len(result) == 1:
        user_id, correct_password_hash, salt = result[0]
        password_input_hash = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P, maxmem=MAXMEM)

        if hmac.compare_digest(password_input_hash, correct_password_hash):
            return user_id

    return None
        

def change_username(user_id, new_username):
    sql = f"UPDATE users SET username = '{new_username}' WHERE id = '{user_id}'"
    db.execute(sql)

    """
    FLAW 2 FIX:
    sql = "UPDATE users SET username = ? WHERE id = ?"
    db.execute(sql, [new_username, user_id])
    """


def change_password(user_id, new_password):
    sha1 = hashlib.sha1()
    sha1.update(new_password.encode())
    new_password_hash = sha1.hexdigest()
    
    sql = f"UPDATE users SET password_hash = '{new_password_hash}' WHERE id = '{user_id}'"
    db.execute(sql)

    """
    FLAW 2 FIX:
    sql = "UPDATE users SET password = ? WHERE id = ?"
    db.execute(sql, [new_password, user_id])
    """


def search_user(search_word, room_id):
    sql = f"""SELECT users.username
        FROM users
        LEFT JOIN members ON users.id = members.user_id
        WHERE users.id NOT IN
            (SELECT user_id FROM rooms WHERE room_id = {room_id})
        AND username LIKE '%{search_word}%'
        """

    return db.query(sql)

