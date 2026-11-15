import db
import os
import hashlib


def create_user(username, password):
    """ bad code
    sha1 = hashlib.sha1()
    sha1.update(password.encode())
    password_hash = sha1.hexdigest()
    sql = f"INSERT INTO users (username, password_hash, salt) VALUES ('{username}', '{password_hash}', '')"
    db.execute(sql)
    """

    # flaw 2 fix
    salt = os.urandom(16)
    password_hash = hashlib.scrypt(password.encode(), salt=salt, n=2**17, r=8, p=1, maxmem=256*1024*1024)

    #"""
    #FLAW 2 & 5 FIX:
    sql = "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)"
    db.execute(sql, [username, password_hash, salt])
    #"""

    # for screenshots
    print("Create user:", 
            {
                "username": username,
                "password": password,
                "password hash": password_hash.hex()
            })

def create_user(username, password):
    pass


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


def check_password_matches(username, password):
    sql = "SELECT id, password_hash, salt FROM users WHERE username = ?"
    result = db.query(sql, [username])

    
    #FLAW 5 FIX:
    if len(result) == 1:
        user_id, hash, salt = result[0]
        print("g")
        print(user_id, hash, salt)

        try:
            #scrypt.verify(password.encode(), hash + salt)
            print("Password verified successfully!")
        except ValueError:
            print("Incorrect password.")
    
    return None
    """
        if password_hash == correct_password_hash:
            return user_id

    return None
    """
#

    if len(result) == 1:
        user_id, correct_password_hash = result[0]
        sha1 = hashlib.sha1()
        sha1.update(password.encode())
        password_hash = sha1.hexdigest() 

        if password_hash == correct_password_hash:
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
    sql = f"UPDATE users SET password = '{new_password}' WHERE id = '{user_id}'"
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

