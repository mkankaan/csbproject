import db


def create_user(username, password):
    sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    db.execute(sql)


def get_user(user_id):
    sql = "SELECT id, username, password FROM users WHERE id = ?"
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
    sql = "SELECT id, password FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, correct_password = result[0]

        if password == correct_password:
            return user_id

    return None


def change_username(user_id, new_username):
    sql = f"UPDATE users SET username = '{new_username}' WHERE id = '{user_id}'"
    db.execute(sql, [new_username, user_id])


def change_password(user_id, new_password):
    sql = f"UPDATE users SET password = '{new_password}' WHERE id = '{user_id}'"
    db.execute(sql, [new_password, user_id])
